AWS SES Email Configuration Guide
=================================

This guide explains how to configure Amazon Simple Email Service (SES)
for sending emails in production.

Overview
--------

The application supports two email backends: - **AWS SES** (recommended
for production) - Reliable, scalable email service - **SMTP** (fallback)
- Traditional SMTP server configuration

AWS SES can be used with: - **IAM Role** (recommended for
EC2/ECS/Lambda) - No credentials needed ⭐ - **IAM User Credentials**
(for non-AWS servers) - Access keys required

Prerequisites
-------------

1. An AWS account
2. AWS CLI installed (optional, for testing)
3. Verified email addresses or domain in AWS SES

Step 1: Set Up AWS SES
----------------------

1.1 Create an AWS Account
~~~~~~~~~~~~~~~~~~~~~~~~~

If you don’t have one, sign up at https://aws.amazon.com

1.2 Verify Your Email Address or Domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option A: Verify Individual Email Addresses** (Quick start) 1. Go to
`AWS SES Console <https://console.aws.amazon.com/ses/>`__ 2. Navigate to
**Verified identities** → **Create identity** 3. Select **Email
address** 4. Enter your email address (e.g., ``aclark@aclark.net``) 5.
Click **Create identity** 6. Check your email and click the verification
link 7. Repeat for any email addresses you want to send FROM

**Option B: Verify Your Domain** (Recommended for production) 1. Go to
`AWS SES Console <https://console.aws.amazon.com/ses/>`__ 2. Navigate to
**Verified identities** → **Create identity** 3. Select **Domain** 4.
Enter your domain (e.g., ``aclark.net``) 5. Follow the instructions to
add DNS records (DKIM, SPF, DMARC) 6. Wait for verification (can take up
to 72 hours)

1.3 Request Production Access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, AWS SES starts in **sandbox mode**, which only allows
sending to verified addresses.

To send to any email address: 1. In the SES Console, go to **Account
dashboard** 2. Click **Request production access** 3. Fill out the form
explaining your use case 4. AWS typically approves within 24 hours

1.4 Choose Your AWS Region
~~~~~~~~~~~~~~~~~~~~~~~~~~

Select a region close to your server for better performance: -
``us-east-1`` (N. Virginia) - Default, most features - ``us-west-2``
(Oregon) - ``eu-west-1`` (Ireland) - See `AWS SES
Regions <https://docs.aws.amazon.com/general/latest/gr/ses.html>`__ for
full list

Step 2: Set Up IAM Permissions
------------------------------

You have two options for authentication:

Option A: IAM Role (Recommended for EC2/ECS/Lambda) ⭐
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Best for**: Applications running on AWS infrastructure

**Benefits**: - ✅ No credentials in your code or .env file - ✅
Automatic credential rotation (every hour) - ✅ Most secure option - ✅
No manual key management - ✅ Can’t accidentally leak credentials

2A.1 Create IAM Role
^^^^^^^^^^^^^^^^^^^^

1. Go to `IAM Console <https://console.aws.amazon.com/iam/>`__
2. Navigate to **Roles** → **Create role**
3. Select **AWS service** → **EC2** (or ECS/Lambda depending on your
   setup)
4. Click **Next**

2A.2 Attach SES Permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Search for and select **AmazonSESFullAccess** (or create a custom
   policy - see below)
2. Click **Next**
3. Enter role name (e.g., ``aclarknet-ses-role``)
4. Click **Create role**

2A.3 Attach Role to EC2 Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Go to `EC2 Console <https://console.aws.amazon.com/ec2/>`__
2. Select your instance
3. **Actions** → **Security** → **Modify IAM role**
4. Select the role you created (``aclarknet-ses-role``)
5. Click **Update IAM role**

**That’s it!** No credentials needed in your ``.env`` file. boto3 will
automatically use the instance role.

Option B: IAM User Credentials (For Non-AWS Servers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Best for**: Applications running outside AWS (on-premises, other cloud
providers)

2B.1 Create IAM User
^^^^^^^^^^^^^^^^^^^^

1. Go to `IAM Console <https://console.aws.amazon.com/iam/>`__
2. Navigate to **Users** → **Create user**
3. Enter username (e.g., ``aclarknet-ses-user``)
4. Click **Next**

2B.2 Attach SES Permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Select **Attach policies directly**
2. Search for and select **AmazonSESFullAccess** (or create a custom
   policy - see below)
3. Click **Next** → **Create user**

2B.3 Create Access Keys
^^^^^^^^^^^^^^^^^^^^^^^

1. Click on the newly created user
2. Go to **Security credentials** tab
3. Click **Create access key**
4. Select **Application running outside AWS**
5. Click **Next** → **Create access key**
6. **IMPORTANT**: Save the Access Key ID and Secret Access Key securely
7. You won’t be able to see the secret key again!

Minimal IAM Policy (Recommended for Both Options)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of ``AmazonSESFullAccess``, use this minimal policy for better
security:

.. code:: json

   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ses:SendEmail",
           "ses:SendRawEmail"
         ],
         "Resource": "*"
       }
     ]
   }

To create a custom policy: 1. In IAM Console, go to **Policies** →
**Create policy** 2. Click **JSON** tab and paste the policy above 3.
Click **Next** → Enter name (e.g., ``SESMinimalSendPolicy``) 4. Click
**Create policy** 5. Attach this policy to your role or user instead of
``AmazonSESFullAccess``

Step 3: Configure Environment Variables
---------------------------------------

If Using IAM Role (Option A) - Recommended ⭐
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit your production ``.env`` file (e.g., ``/srv/aclarknet/.env``):

.. code:: bash

   # Enable AWS SES
   USE_SES=True

   # AWS SES Region (required)
   AWS_SES_REGION_NAME=us-east-1

   # NO credentials needed! boto3 will use the EC2 instance role
   # Leave AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY commented out or empty

   # Optional: Configuration set for tracking (leave empty if not using)
   AWS_SES_CONFIGURATION_SET=

   # Use SES v2 API (recommended)
   USE_SES_V2=True

**That’s it!** The application will automatically use the IAM role
attached to your EC2 instance.

If Using IAM User Credentials (Option B)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit your production ``.env`` file:

.. code:: bash

   # Enable AWS SES
   USE_SES=True

   # AWS Credentials (from Step 2B.3)
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

   # AWS SES Region (use the region where you verified your email/domain)
   AWS_SES_REGION_NAME=us-east-1

   # Optional: Configuration set for tracking (leave empty if not using)
   AWS_SES_CONFIGURATION_SET=

   # Use SES v2 API (recommended)
   USE_SES_V2=True

**Security Note**: Never commit these credentials to version control!

Step 4: Test Your Configuration
-------------------------------

Test from Django Shell
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python manage.py shell --settings=aclarknet.settings.production

.. code:: python

   from django.core.mail import send_mail

   send_mail(
       'Test Email from AWS SES',
       'This is a test email sent via AWS SES with IAM role authentication.',
       'aclark@aclark.net',  # Must be verified in SES
       ['recipient@example.com'],  # Must be verified if in sandbox mode
       fail_silently=False,
   )

If successful, you should see no errors and receive the email.

Test with AWS CLI (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   aws ses send-email \
     --from aclark@aclark.net \
     --destination ToAddresses=recipient@example.com \
     --message Subject={Data="Test Email",Charset=utf8},Body={Text={Data="Test message",Charset=utf8}} \
     --region us-east-1

Verify IAM Role is Working (EC2 Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SSH into your EC2 instance and check:

.. code:: bash

   # Check if instance has an IAM role attached
   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

   # Should output the role name, e.g., "aclarknet-ses-role"

   # Get temporary credentials (these auto-rotate)
   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/aclarknet-ses-role

   # Should output JSON with AccessKeyId, SecretAccessKey, Token, and Expiration

Step 5: Monitoring and Troubleshooting
--------------------------------------

Monitor Email Sending
~~~~~~~~~~~~~~~~~~~~~

1. **SES Console Dashboard**

   - Go to `SES Console <https://console.aws.amazon.com/ses/>`__
   - View sending statistics, bounces, and complaints

2. **CloudWatch Metrics**

   - Monitor delivery rates, bounces, complaints
   - Set up alarms for high bounce rates

3. **Django Logs**

   - Check ``/srv/aclarknet/logs/django.log`` for email errors

Common Issues
~~~~~~~~~~~~~

Issue: “Unable to locate credentials”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: - **If using IAM role**: Verify the role is attached to
your EC2 instance
``bash   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/``
- **If using IAM user**: Check that ``AWS_ACCESS_KEY_ID`` and
``AWS_SECRET_ACCESS_KEY`` are set in ``.env``

Issue: “Email address is not verified”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Verify the sender email address in SES Console, or request
production access to send to any address.

Issue: “Access Denied” or “InvalidClientTokenId”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: - **If using IAM role**: Verify the role has SES
permissions (check IAM policy) - **If using IAM user**: Check that AWS
credentials are correct and not expired

Issue: Emails going to spam
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: - Verify your domain (not just email address) - Set up
SPF, DKIM, and DMARC records - Use a verified domain for the FROM
address - Avoid spam trigger words in subject/body

Issue: “Daily sending quota exceeded”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: - Check your sending limits in SES Console - Request a
limit increase if needed - Implement rate limiting in your application

Sending Limits
~~~~~~~~~~~~~~

**Sandbox Mode:** - 200 emails per 24 hours - 1 email per second - Can
only send to verified addresses

**Production Mode:** - Starts at 50,000 emails per 24 hours (can be
increased) - 14 emails per second (can be increased) - Can send to any
address

Step 6: Advanced Configuration
------------------------------

Configuration Sets (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration sets allow you to track email events (opens, clicks,
bounces):

1. Create a configuration set in SES Console

2. Set up event destinations (SNS, CloudWatch, Kinesis)

3. Add to your ``.env``:

   .. code:: bash

      AWS_SES_CONFIGURATION_SET=my-config-set

Custom Email Headers
~~~~~~~~~~~~~~~~~~~~

You can add custom headers in your Django email code:

.. code:: python

   from django.core.mail import EmailMessage

   email = EmailMessage(
       'Subject',
       'Body',
       'from@example.com',
       ['to@example.com'],
       headers={'X-SES-CONFIGURATION-SET': 'my-config-set'},
   )
   email.send()

Bounce and Complaint Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up SNS notifications for bounces and complaints:

1. Create SNS topics for bounces and complaints
2. Configure SES to publish to these topics
3. Subscribe your application endpoint to handle notifications
4. Automatically remove bounced/complained addresses from your mailing
   list

Switching Between SES and SMTP
------------------------------

To switch back to SMTP (e.g., for testing):

.. code:: bash

   # In your .env file
   USE_SES=False

   # Configure SMTP settings
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password

Cost Estimation
---------------

AWS SES Pricing (as of 2026): - First 62,000 emails per month: **FREE**
(when sent from EC2) - After that: $0.10 per 1,000 emails - Attachments:
$0.12 per GB

Example: Sending 100,000 emails/month = ~$3.80/month

See `AWS SES Pricing <https://aws.amazon.com/ses/pricing/>`__ for
current rates.

Security Best Practices
-----------------------

For IAM Roles (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. ✅ **Use IAM roles** when running on AWS infrastructure
2. ✅ **Apply least privilege** - use minimal IAM policy (see Step 2)
3. ✅ **No credentials to manage** - automatic rotation
4. ✅ **Enable MFA** on your AWS account
5. ✅ **Monitor CloudTrail** logs for suspicious activity
6. ✅ **Set up billing alerts** to detect unusual usage

For IAM User Credentials
~~~~~~~~~~~~~~~~~~~~~~~~

1. ⚠️ **Never commit credentials** to version control
2. ⚠️ **Rotate access keys** regularly (every 90 days)
3. ⚠️ **Use least privilege** IAM policies
4. ⚠️ **Store in secrets manager** (not .env file) for production
5. ⚠️ **Enable MFA** on your AWS account
6. ⚠️ **Monitor CloudTrail** logs for suspicious activity
7. ⚠️ **Set up billing alerts** to detect unusual usage

Credential Rotation (IAM User Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If using IAM user credentials, rotate them regularly:

.. code:: bash

   # 1. Create new access key in IAM Console
   # 2. Update .env with new credentials
   # 3. Restart application
   sudo systemctl restart aclarknet.service
   # 4. Test email sending
   # 5. Delete old access key in IAM Console

**Note**: With IAM roles, credentials auto-rotate every hour - no manual
rotation needed!

Comparison: IAM Role vs IAM User
--------------------------------

======================= ========================= ==================
Feature                 IAM Role (EC2/ECS/Lambda) IAM User (Non-AWS)
======================= ========================= ==================
**Credentials in .env** ❌ No                     ✅ Yes
**Auto-rotation**       ✅ Every hour             ❌ Manual
**Security**            ⭐⭐⭐⭐⭐                ⭐⭐⭐
**Setup Complexity**    Easy                      Easy
**Credential Leaks**    ✅ Impossible             ⚠️ Possible
**Works on AWS**        ✅ Yes                    ✅ Yes
**Works off AWS**       ❌ No                     ✅ Yes
**Recommended**         ✅ Yes (on AWS)           ✅ Yes (off AWS)
======================= ========================= ==================

Additional Resources
--------------------

- `AWS SES Documentation <https://docs.aws.amazon.com/ses/>`__
- `django-ses
  Documentation <https://github.com/django-ses/django-ses>`__
- `AWS SES Best
  Practices <https://docs.aws.amazon.com/ses/latest/dg/best-practices.html>`__
- `Email Deliverability
  Guide <https://docs.aws.amazon.com/ses/latest/dg/send-email-concepts-deliverability.html>`__
- `IAM Roles for
  EC2 <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html>`__
- `AWS Security Best
  Practices <https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html>`__

Support
-------

For issues specific to this application, check: - Application logs:
``/srv/aclarknet/logs/django.log`` - Django settings:
``aclarknet/settings/production.py`` - Environment variables:
``/srv/aclarknet/.env``

For AWS SES issues: - `AWS
Support <https://console.aws.amazon.com/support/>`__ - `AWS SES
Forum <https://forums.aws.amazon.com/forum.jspa?forumID=90>`__

Quick Reference
---------------

Minimal .env for IAM Role (Recommended on EC2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   USE_SES=True
   AWS_SES_REGION_NAME=us-east-1
   # No credentials needed!

Minimal .env for IAM User (Non-AWS servers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   USE_SES=True
   AWS_ACCESS_KEY_ID=your-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_SES_REGION_NAME=us-east-1

Test Email Sending
~~~~~~~~~~~~~~~~~~

.. code:: python

   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])

Check IAM Role (EC2 only)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
