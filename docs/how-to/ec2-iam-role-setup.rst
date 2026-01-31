How to Add an SES IAM Role to Your EC2 Instance
===============================================

This guide walks you through creating an IAM role with SES permissions
and attaching it to your EC2 instance.

Overview
--------

Using an IAM role is the **most secure** way to give your EC2 instance
access to AWS SES: - ✅ No credentials in your code or .env file - ✅
Automatic credential rotation (every hour) - ✅ No manual key management
- ✅ Can’t accidentally leak credentials

Step 1: Create the IAM Role
---------------------------

1.1 Open IAM Console
~~~~~~~~~~~~~~~~~~~~

1. Log into `AWS Console <https://console.aws.amazon.com/>`__
2. Go to **IAM** service (search for “IAM” in the top search bar)
3. Click **Roles** in the left sidebar
4. Click **Create role** button

1.2 Select Trusted Entity
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Select **AWS service** (should be selected by default)
2. Under “Use case”, select **EC2**
3. Click **Next**

1.3 Add SES Permissions
~~~~~~~~~~~~~~~~~~~~~~~

**Option A: Use AWS Managed Policy (Quick)** 1. In the search box, type:
``AmazonSESFullAccess`` 2. Check the box next to **AmazonSESFullAccess**
3. Click **Next**

**Option B: Create Custom Policy (Recommended - Least Privilege)** 1.
Click **Create policy** (opens in new tab) 2. Click the **JSON** tab 3.
Paste this policy:

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

4.  Click **Next**
5.  Enter policy name: ``SESMinimalSendPolicy``
6.  Click **Create policy**
7.  Go back to the role creation tab
8.  Click the refresh button
9.  Search for ``SESMinimalSendPolicy``
10. Check the box next to it
11. Click **Next**

1.4 Name and Create the Role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Enter role name: ``aclarknet-ses-role`` (or any name you prefer)
2. Enter description: ``Allows EC2 instance to send emails via AWS SES``
3. Review the settings
4. Click **Create role**

✅ **Role created!** Now let’s attach it to your EC2 instance.

Step 2: Attach the Role to Your EC2 Instance
--------------------------------------------

2.1 Open EC2 Console
~~~~~~~~~~~~~~~~~~~~

1. Go to **EC2** service (search for “EC2” in the top search bar)
2. Click **Instances** in the left sidebar
3. Find your instance (e.g., the one running aclarknet)
4. Select it by clicking the checkbox

2.2 Attach the IAM Role
~~~~~~~~~~~~~~~~~~~~~~~

1. Click **Actions** dropdown (top right)
2. Select **Security** → **Modify IAM role**
3. In the “IAM role” dropdown, select **aclarknet-ses-role** (the role
   you just created)
4. Click **Update IAM role**

✅ **Role attached!** Your EC2 instance now has permission to send
emails via SES.

**Note**: You do NOT need to restart your EC2 instance. The role takes
effect immediately.

Step 3: Update Your Application Configuration
---------------------------------------------

3.1 Edit Your .env File
~~~~~~~~~~~~~~~~~~~~~~~

SSH into your EC2 instance and edit the ``.env`` file:

.. code:: bash

   ssh your-ec2-instance
   sudo nano /srv/aclarknet/.env

3.2 Update Email Settings
~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure your ``.env`` file has these settings:

.. code:: bash

   # Enable AWS SES
   USE_SES=True

   # AWS SES Region (required)
   AWS_SES_REGION_NAME=us-east-1

   # NO credentials needed! Remove or comment out these lines:
   # AWS_ACCESS_KEY_ID=...
   # AWS_SECRET_ACCESS_KEY=...

   # Optional settings
   USE_SES_V2=True
   AWS_SES_CONFIGURATION_SET=

**Important**: Remove or comment out ``AWS_ACCESS_KEY_ID`` and
``AWS_SECRET_ACCESS_KEY``. The IAM role will provide credentials
automatically.

3.3 Restart Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   sudo systemctl restart aclarknet.service

Step 4: Verify the IAM Role is Working
--------------------------------------

4.1 Check IAM Role Attachment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SSH into your EC2 instance and run:

.. code:: bash

   # Check if instance has an IAM role attached
   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

   # Should output: aclarknet-ses-role (or whatever you named it)

If you see the role name, it’s attached correctly!

4.2 Get Temporary Credentials (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To see the actual credentials that boto3 will use:

.. code:: bash

   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/aclarknet-ses-role

You should see JSON output with: - ``AccessKeyId`` - Temporary access
key - ``SecretAccessKey`` - Temporary secret key - ``Token`` - Session
token - ``Expiration`` - When credentials expire (auto-renewed)

**Note**: These credentials rotate automatically every hour. You never
need to manage them!

4.3 Test Email Sending
~~~~~~~~~~~~~~~~~~~~~~

Test from Django shell:

.. code:: bash

   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python manage.py shell --settings=aclarknet.settings.production

.. code:: python

   from django.core.mail import send_mail

   send_mail(
       'Test Email from AWS SES with IAM Role',
       'This email was sent using IAM role credentials!',
       'aclark@aclark.net',
       ['aclark@aclark.net'],
       fail_silently=False,
   )

If successful, you should see ``1`` (one email sent) and receive the
email!

Troubleshooting
---------------

Issue: “Unable to locate credentials”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Check 1**: Verify role is attached

.. code:: bash

   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

Should output your role name. If empty, the role isn’t attached.

**Check 2**: Verify .env doesn’t have credentials Make sure
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` are removed or
commented out.

**Check 3**: Restart application

.. code:: bash

   sudo systemctl restart aclarknet.service

Issue: “Access Denied” when sending email
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Check 1**: Verify role has SES permissions 1. Go to IAM Console →
Roles 2. Click on ``aclarknet-ses-role`` 3. Check “Permissions” tab 4.
Should see ``AmazonSESFullAccess`` or ``SESMinimalSendPolicy``

**Check 2**: Verify email address is verified in SES 1. Go to SES
Console → Verified identities 2. Make sure ``aclark@aclark.net`` is
verified 3. Or request production access to send to any address

Issue: Email not sending but no errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Check application logs**:

.. code:: bash

   sudo tail -f /srv/aclarknet/logs/django.log

Look for email-related errors.

Next Steps
----------

1. ✅ Verify email addresses in AWS SES Console
2. ✅ Request production access (to send to any email address)
3. ✅ Set up SPF/DKIM/DMARC records for better deliverability
4. ✅ Monitor sending in SES Console dashboard

See ``docs/aws_ses_setup.md`` for complete AWS SES configuration guide.

Summary
-------

You’ve successfully: - ✅ Created an IAM role with SES permissions - ✅
Attached the role to your EC2 instance - ✅ Configured your application
to use the role - ✅ Verified the role is working

Your application can now send emails via AWS SES without any credentials
in your code! 🎉
