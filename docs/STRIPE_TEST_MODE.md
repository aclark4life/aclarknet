# Stripe Test Mode Configuration

This guide explains how to configure and test Stripe payments in production using Stripe's test mode.

## Overview

Stripe provides separate API keys for **test mode** and **live mode**:
- **Test mode**: Use test API keys to simulate payments without processing real transactions
- **Live mode**: Use live API keys to process real payments

The application automatically detects which mode you're in based on the API key prefix:
- Test keys start with `sk_test_` or `pk_test_`
- Live keys start with `sk_live_` or `pk_live_`

## Getting Your Stripe Test Keys

1. **Sign up for Stripe** (if you haven't already):
   - Go to https://dashboard.stripe.com/register
   - Create a free account

2. **Get your test API keys**:
   - Go to https://dashboard.stripe.com/test/apikeys
   - You'll see two keys:
     - **Publishable key**: Starts with `pk_test_...` (safe to use in client-side code)
     - **Secret key**: Starts with `sk_test_...` (keep this private, server-side only)
   - Click "Reveal test key" to see your secret key

3. **Get your webhook secret** (for receiving payment confirmations):
   - Go to https://dashboard.stripe.com/test/webhooks
   - Click "Add endpoint"
   - Enter your webhook URL: `https://yourdomain.com/dashboard/payment/webhook/`
   - Select events to listen to:
     - `checkout.session.completed`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
   - Click "Add endpoint"
   - Click "Reveal" under "Signing secret" to get your webhook secret (starts with `whsec_...`)

## Environment Configuration

### For Production Testing

Update your production environment variables (`.env` file or hosting platform):

```bash
# Stripe Test Mode Keys
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
```

### For Live Mode (when ready to accept real payments)

Replace with your live keys:

```bash
# Stripe Live Mode Keys
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_LIVE_WEBHOOK_SECRET_HERE
```

## Testing Payments

### Test Card Numbers

When in test mode, use these test card numbers:

| Card Number | Description |
|-------------|-------------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |
| `4000 0000 0000 9995` | Declined (insufficient funds) |
| `4000 0000 0000 0002` | Declined (generic decline) |

**For all test cards:**
- Use any future expiration date (e.g., `12/34`)
- Use any 3-digit CVC (e.g., `123`)
- Use any ZIP code (e.g., `12345`)

Full list: https://stripe.com/docs/testing

### Testing the Payment Flow

1. **Create a test invoice** in your admin dashboard
2. **Copy the payment link** from the invoice detail page
3. **Open the payment link** in an incognito/private browser window
4. **Verify the test mode indicator** appears (yellow warning banner)
5. **Click "Pay with Stripe"**
6. **Enter test card details**:
   - Card number: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits
7. **Complete the payment**
8. **Verify success page** shows test mode indicator
9. **Check your Stripe dashboard**: https://dashboard.stripe.com/test/payments
10. **Check your invoice** in the admin dashboard - it should show as paid

### Webhook Testing

To test webhooks locally during development:

1. **Install Stripe CLI**: https://stripe.com/docs/stripe-cli
2. **Login**: `stripe login`
3. **Forward webhooks to local server**:
   ```bash
   stripe listen --forward-to localhost:8000/dashboard/payment/webhook/
   ```
4. **Trigger test events**:
   ```bash
   stripe trigger checkout.session.completed
   ```

## Visual Indicators

When in test mode, the application displays:

1. **Yellow warning banner** at the top of payment pages with test card instructions
2. **"TEST MODE" badge** in the page header
3. **Test mode notice** on the success page

These indicators automatically disappear when you switch to live mode keys.

## Switching to Live Mode

When you're ready to accept real payments:

1. **Complete Stripe account activation**:
   - Go to https://dashboard.stripe.com/account/onboarding
   - Provide business information
   - Add bank account for payouts

2. **Get live API keys**:
   - Go to https://dashboard.stripe.com/apikeys (note: no "/test/" in URL)
   - Copy your live publishable and secret keys

3. **Create live webhook**:
   - Go to https://dashboard.stripe.com/webhooks
   - Add endpoint with your production URL
   - Copy the live webhook secret

4. **Update environment variables** with live keys

5. **Test with real card** (small amount first!)

6. **Monitor payments**: https://dashboard.stripe.com/payments

## Security Notes

- ✅ **Never commit API keys** to version control
- ✅ **Use environment variables** for all keys
- ✅ **Keep secret keys private** (server-side only)
- ✅ **Use webhook secrets** to verify webhook authenticity
- ✅ **Test thoroughly** in test mode before going live
- ✅ **Monitor Stripe dashboard** for suspicious activity

## Troubleshooting

### "Payment system is not configured" error
- Check that `STRIPE_SECRET_KEY` is set in environment variables
- Verify the key starts with `sk_test_` or `sk_live_`

### Webhook not receiving events
- Check webhook URL is publicly accessible
- Verify webhook secret matches Stripe dashboard
- Check Stripe dashboard webhook logs for errors
- Ensure webhook endpoint is not behind authentication

### Payment succeeds but invoice not updated
- Check webhook is configured correctly
- Check application logs for webhook processing errors
- Verify invoice ID is in webhook metadata

## Support

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: https://support.stripe.com
- **Test Mode Dashboard**: https://dashboard.stripe.com/test
- **Live Mode Dashboard**: https://dashboard.stripe.com
