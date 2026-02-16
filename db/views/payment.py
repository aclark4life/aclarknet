"""Payment views for Stripe integration."""

import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..models import Invoice, Payment

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PublicInvoicePaymentView(View):
    """Public view for invoice payment - no authentication required."""

    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        context = {
            "invoice": invoice,
        }
        return render(request, "payment/invoice.html", context)


class CreateCheckoutSessionView(View):
    """Create a Stripe Checkout session for an invoice."""

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        # Check if invoice has a balance to pay
        if not invoice.balance or invoice.balance <= 0:
            messages.error(request, "This invoice has already been paid.")
            return redirect("public_invoice_payment", invoice_id=invoice_id)

        # Check if Stripe is configured
        if not settings.STRIPE_SECRET_KEY:
            logger.error("Stripe secret key is not configured")
            messages.error(
                request,
                "Payment system is not configured. Please contact support.",
            )
            return redirect("public_invoice_payment", invoice_id=invoice_id)

        try:
            logger.info(
                f"Creating Stripe checkout session for invoice {invoice.invoice_number}, "
                f"amount: ${invoice.balance}"
            )

            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": settings.STRIPE_CURRENCY,
                            "unit_amount": int(
                                invoice.balance * 100
                            ),  # Convert to cents
                            "product_data": {
                                "name": f"Invoice #{invoice.invoice_number}",
                                "description": invoice.name
                                or f"Payment for Invoice #{invoice.invoice_number}",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("payment_success"))
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(
                    reverse("public_invoice_payment", args=[invoice_id])
                ),
                metadata={
                    "invoice_id": str(invoice.id),
                    "invoice_number": str(invoice.invoice_number),
                },
            )

            logger.info(f"Stripe checkout session created: {checkout_session.id}")
            return redirect(checkout_session.url, code=303)

        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error: {e}", exc_info=True)
            messages.error(
                request,
                "Payment system authentication failed. Please contact support.",
            )
            return redirect("public_invoice_payment", invoice_id=invoice_id)
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Stripe invalid request error: {e}", exc_info=True)
            messages.error(
                request,
                f"Invalid payment request: {str(e)}",
            )
            return redirect("public_invoice_payment", invoice_id=invoice_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}", exc_info=True)
            messages.error(
                request,
                f"Payment system error: {str(e)}",
            )
            return redirect("public_invoice_payment", invoice_id=invoice_id)
        except Exception as e:
            logger.error(
                f"Unexpected error creating Stripe checkout session: {e}", exc_info=True
            )
            messages.error(
                request,
                f"An unexpected error occurred: {str(e)}",
            )
            return redirect("public_invoice_payment", invoice_id=invoice_id)


class PaymentSuccessView(View):
    """Handle successful payment redirect."""

    def get(self, request):
        session_id = request.GET.get("session_id")

        if not session_id:
            messages.error(request, "Invalid payment session.")
            return redirect("dashboard")

        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            context = {
                "session": session,
                "invoice_id": session.metadata.get("invoice_id"),
            }

            return render(request, "payment/success.html", context)

        except Exception as e:
            logger.error(f"Error retrieving payment session: {e}")
            messages.error(request, "Unable to verify payment. Please contact support.")
            return redirect("dashboard")


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """Handle Stripe webhook events."""

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            # Invalid payload
            logger.error("Invalid Stripe webhook payload")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            logger.error("Invalid Stripe webhook signature")
            return HttpResponse(status=400)

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            self._handle_checkout_session_completed(session)
        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            self._handle_payment_intent_succeeded(payment_intent)
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            self._handle_payment_intent_failed(payment_intent)

        return HttpResponse(status=200)

    def _handle_checkout_session_completed(self, session):
        """Handle completed checkout session."""
        try:
            invoice_id = session["metadata"].get("invoice_id")
            if not invoice_id:
                logger.error("No invoice_id in checkout session metadata")
                return

            invoice = Invoice.objects.get(id=invoice_id)
            payment_intent_id = session.get("payment_intent")

            # Create or update payment record
            payment, created = Payment.objects.get_or_create(
                stripe_payment_intent_id=payment_intent_id,
                defaults={
                    "invoice": invoice,
                    "stripe_checkout_session_id": session["id"],
                    "amount": session["amount_total"] / 100,  # Convert from cents
                    "currency": session["currency"],
                    "status": "succeeded",
                    "customer_email": session.get("customer_details", {}).get("email"),
                    "metadata": session.get("metadata", {}),
                },
            )

            if not created:
                payment.status = "succeeded"
                payment.stripe_checkout_session_id = session["id"]
                payment.save()

            # Update invoice paid_amount and balance
            invoice.paid_amount = (invoice.paid_amount or 0) + payment.amount
            invoice.balance = invoice.amount - invoice.paid_amount
            invoice.save()

            logger.info(
                f"Payment {payment_intent_id} completed for invoice {invoice.invoice_number}"
            )

        except Invoice.DoesNotExist:
            logger.error(f"Invoice {invoice_id} not found for payment")
        except Exception as e:
            logger.error(f"Error handling checkout session completed: {e}")

    def _handle_payment_intent_succeeded(self, payment_intent):
        """Handle successful payment intent."""
        try:
            payment_intent_id = payment_intent["id"]
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()

            if payment:
                payment.status = "succeeded"
                payment.save()
                logger.info(f"Payment intent {payment_intent_id} succeeded")

        except Exception as e:
            logger.error(f"Error handling payment intent succeeded: {e}")

    def _handle_payment_intent_failed(self, payment_intent):
        """Handle failed payment intent."""
        try:
            payment_intent_id = payment_intent["id"]
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()

            if payment:
                payment.status = "failed"
                payment.save()
                logger.warning(f"Payment intent {payment_intent_id} failed")

        except Exception as e:
            logger.error(f"Error handling payment intent failed: {e}")
