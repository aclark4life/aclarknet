:title: Project Makefile
:date: 2016-11-23
:slug: project-makefile
:source: blog
:status: published

|

.. image:: /images/project-makefile-tweet.png
    :align: center
    :class: blog-image

|

A while back |I was asked| to present to the |cmwg|. From that moment on I had an excuse to finish and talk about the ``Makefile`` I'd been dragging around formally since January and informally for much longer.

Finishing the Makefile
----------------------

I started writing slides on the impressive |slides| then I realized I had to finished the Makefile to finish the slides. This mostly involved deciding on target names and testing target execution.

Finishing the Slides
--------------------

As I mentioned above, slides.com is very nice. I had hoped to be able to build the slides myself with reveal.js, but in lieu of JavaScript skills I settled on using the slides.com editor. Later I exported and converted them to PDF with pandoc, which was not as nice (through no fault of pandoc, I'm sure; I just wish I could get a better PDF copy from the slides.com HTML export.)

Closed for Business
-------------------

For month after month as I continued to tweak, the project-makefile repository README contained the following::

    **DO NOT USE THIS**

    At some point I started using a ``Makefile`` in my development
    projects. This repository contains that ``Makefile``.

    **shrug**

Open for Business
-----------------

Now it looks like this:

.. image:: /images/project-makefile-open-for-biz.png
    :class: blog-image

I now invite everyone to use and contribute.

|

- |project-makefile|

.. |cmwg| raw:: html

    <a target="_blank" href="http://www.cmwg.org/">Configuration Management Working Group of DC</a>

.. |slides| raw:: html

    <a target="_blank" href="http://slides.com/aclark/project-makefile">slides.com</a>

.. |project-makefile| raw:: html

    <a target="_blank" href="https://github.com/project-makefile/project-makefile">https://github.com/project-makefile/project-makefile</a>

.. |i was asked| raw:: html

    <a href="https://twitter.com/CMWorkingGrp/status/773228143939293185" target="_blank">I was asked</a>
