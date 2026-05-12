:title: A New Plone Book
:date: 2010-03-30
:slug: a-new-plone-book
:source: blog
:status: published

|

.. image:: /images/7047_plone20site20admincov.5ae6fff11a65.jpg
    :align: center
    :class: blog-image

|

Plone 3.3 Site Administration
-----------------------------

If |Plone Conference 2006| was my inspiration for |Plone Conference 2008|, then Professional Plone Development was my inspiration for this book: |Plone 3.3 Site Administration|.

For the past 14 months or so, I have been writing a book aimed at end users of Plone: folks that have little knowledge of how to do much more than add content. It is intended to make them feel more comfortable performing various site administrator tasks. Topics like theming, maintenance, and optimization and more are covered.

Lowering the Plone Bar for Python Users
---------------------------------------

This book aims to ``"lower the Plone bar for users of Python"``. What do I mean by that? Basically this: I love Python almost as much as I love Plone. It lets me translate my thoughts directly into code. I fantasize that with little more than a Python interpreter, one can forge a working Plone site within minutes. But it is not just a fantasy, it is (more or less) the status quo.

So, this book begins at the beginning: by making sure folks are comfortable installing and using Python on there operating system of choice (or using the pre-installed Python). If you read Professional Plone Development, you may recall Martin Aspeli saying at the beginning of Chapter 3:

    "We will assume that Python 2.4 gets invoked when you run python on the command line."

This book does not make that assumption and tries to cover everything you may need to know after installing your operating system up to that point.

In Chapter 1, we cover installing and running Python on three popular operating systems: Mac OS X 10.6, Windows 7, and Ubuntu 9.10.

Buildout
--------

This book is largely a response to the ``"Oh no! I have to use Buildout to install Plone and its add-ons!"`` sentiment that has been prevalent since Buildout was first introduced to Plone several years ago. I don't know if Buildout was the "right" way to go, but I do know that I love using it and I would like to help others feel the same way.

The bottom line is this: Plone made a conscious decision to ``"become more Pythonic"`` by using eggs. With that choice came more complexity from potential conflicts between eggs. Buildout is one solution to that problem. Unfortunately, it introduces other problems like cryptic error messages and a certain too-many-moving-parts-ness.

Let me correct myself: I am fairly certain Buildout was the right way to go at the time. What I am not sure about is where to go from here. It would be nice to get back to a place where folks could just drop packages in to a directory (I don't literally mean going back to old-style products, but perhaps we could provide that type of functionality again somehow). But I don't have an answer for that. In the meantime, let's make everyone more comfortable with using Buildout.

About the Rest
--------------

The book teaches you to find your way around Buildout and Plone. Whether you choose to follow along and build your site from scratch using only Buildout (and a paper clip) or if you use one of the Buildout-based installers (like the Unified Installer), this book aims to make you more competent and comfortable performing a variety of Buildout-related tasks.

In Chapters 2-7, we present various buildout configuration files that correspond to specific tasks that are related to various subjects, e.g. theming, maintenance, and optimization. The reader is expected to ``"know how to write a buildout.cfg file"`` by the end.

In the final Chapter 8, we cover new technologies like XDV and repoze.zope2 which may become more mainstream once you decide to start using them (although the latter seems more like a toy to keep us busy until the real fix arrives: full WSGI support in Zope 2.

When Will it Arrive
-------------------

PACKT originally announced the book will arrive in March and I have been working non-stop since mid-March to make sure it gets out the door as quickly as possible. I expect it to be available sson. I apologize to those of you who have pre-ordered and are now waiting for it.

So get ready! I plan to have over 200 pages of draft material submitted by the end of this month. I will continue to work with PACKT to address any concerns that arise during editing. They have promised to try to ship the book by May, so we will see how it goes. I encourage you to pre-order now as that will go a long way to inspire them to work just that much harder to get it done and out to you, ASAP.

|

.. |Plone Conference 2006| raw:: html

   <a href="http://plone.org/events/conferences/seattle-2006" target="_blank">Plone Conference 2006</a>

.. |Plone Conference 2008| raw:: html

   <a href="https://plone.org/events/plone-conferences/washington-dc-2008" target="_blank">Plone Conference 2008</a>

.. |Plone 3.3 Site Administration| raw:: html

   <a href="https://www.packtpub.com/product/plone-3-3-site-administration/9781847197047" target="_blank">Plone 3.3 Site Administration</a>
