How-to Guides
=============

**How-to guides are goal-oriented directions that help you accomplish specific tasks.**

These guides assume you're already familiar with aclarknet basics. They provide practical steps to solve real-world problems and achieve specific goals.

.. toctree::
   :maxdepth: 1

   deployment-quickstart
   aws-ses-setup
   ec2-iam-role-setup
   fix-gmail-warning
   testimonials-quickstart
   manual-testing-guide

Deployment
----------

:doc:`deployment-quickstart`
   Quick reference for deploying aclarknet to production. Covers the essential steps to get your application running on a server.

:doc:`aws-ses-setup`
   Configure Amazon Simple Email Service (SES) for sending emails from your application. Includes both IAM user and IAM role authentication methods.

:doc:`ec2-iam-role-setup`
   Add an IAM role to your EC2 instance for secure AWS service access without storing credentials in your code.

Email
-----

:doc:`fix-gmail-warning`
   Fix the "Be careful with this message" warning that Gmail displays for emails sent from AWS SES. Add DMARC and DKIM records to pass email authentication.

Content Management
------------------

:doc:`testimonials-quickstart`
   Manage client testimonials through the Django admin interface. Learn how to add, feature, and organize testimonials on your site.

Testing
-------

:doc:`manual-testing-guide`
   Manually test the application to verify functionality. Covers testing contact forms, client categorization, testimonials, and admin features.

Need More Help?
---------------

* **Learning the basics?** See :doc:`../tutorials/index`
* **Want to understand why?** See :doc:`../explanation/index`
* **Need technical details?** See :doc:`../reference/index`
