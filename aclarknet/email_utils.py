"""Email utilities for improved deliverability and authentication."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email_with_headers(
    subject,
    plain_message,
    recipient_list,
    html_message=None,
    from_email=None,
    reply_to=None,
    fail_silently=False,
):
    """
    Send email with proper headers for better deliverability and authentication.

    This function adds headers that help with:
    - Email authentication (SPF, DKIM, DMARC)
    - Spam filtering
    - Gmail warning prevention

    Args:
        subject: Email subject line
        plain_message: Plain text message body
        recipient_list: List of recipient email addresses
        html_message: Optional HTML version of the message
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        reply_to: Reply-to address (defaults to from_email)
        fail_silently: Whether to suppress exceptions

    Returns:
        Number of successfully sent emails
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    if reply_to is None:
        reply_to = from_email

    # Prepare headers for better deliverability
    headers = {
        "Reply-To": reply_to,
        "X-Mailer": "aclark.net",
        "X-Auto-Response-Suppress": "OOF, AutoReply",  # Suppress auto-replies
        "Precedence": "bulk",  # Indicate this is automated mail
    }

    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=recipient_list,
        headers=headers,
    )

    # Attach HTML version if provided
    if html_message:
        email.attach_alternative(html_message, "text/html")

    # Send the email
    return email.send(fail_silently=fail_silently)


def send_notification_email(
    subject,
    plain_message,
    html_message=None,
    from_email=None,
    recipient_email=None,
):
    """
    Send a notification email to the site admin.

    This is a convenience wrapper for internal notifications.

    Args:
        subject: Email subject line
        plain_message: Plain text message body
        html_message: Optional HTML version of the message
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        recipient_email: Recipient email (defaults to DEFAULT_FROM_EMAIL)

    Returns:
        Number of successfully sent emails
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    if recipient_email is None:
        recipient_email = settings.DEFAULT_FROM_EMAIL

    return send_email_with_headers(
        subject=subject,
        plain_message=plain_message,
        recipient_list=[recipient_email],
        html_message=html_message,
        from_email=from_email,
        fail_silently=False,
    )
