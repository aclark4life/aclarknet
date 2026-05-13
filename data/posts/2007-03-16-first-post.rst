:title: First Post
:date: 2007-03-16
:slug: first-post
:source: blog
:status: published

.. image:: /images/look-at-me.jpg
    :align: center
    :class: blog-image

.. https://stackoverflow.com/a/6652379

.. role:: strike
    :class: strike

I have decided to start a blog. Why? Because Plone allows me to do so. But also:

- I have been reading a lot of |planet_plone| lately and they have inspired me to write my own.
- I want to interact with other Plone developers and users.
- I want to try new technology.

Build Tools
-----------

To that end, this post is about my |build_tools|. But first I'll note these current and likely better alternatives:

- |buildout|
- :strike:`Buildit`
- :strike:`Instance Manager`

I used Buildout for the first time at the |baarn_sprint| and I've also used Chris McDonough's Buildit.

There are probably even more to choose from, but for now I enjoy typing:

::

    newzope test-site ProductA ProductB ProductC

and having a working instance a few seconds later with Product{A,B,C} installed.

.. https://stackoverflow.com/a/11718325

.. |planet_plone| raw:: html

   <a href="https://planet.plone.org" target="_blank">Plone blogs</a>

.. |baarn_sprint| raw:: html

   <a href="https://web.archive.org/web/20071012114759/http://plone.org/events/sprints/past-sprints/baarn-ui-sprint-2007" target="_blank">Baarn UI Sprint 2007</a>

.. |build_tools| raw:: html

   <a href="https://svn.plone.org/svn/collective/newzope" target="_blank">build tools</a>

.. |buildout| raw:: html

   <a href="https://buildout.org" target="_blank">Buildout</a>
