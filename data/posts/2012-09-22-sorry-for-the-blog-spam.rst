:title: Sorry for the blog spam
:date: 2012-09-22
:slug: sorry-for-the-blog-spam
:tags: Python
:source: blog-2017
:status: draft

**Just learning Pelican**

As I'm just learning `Pelican`_, `Dirkjan Ochtman pointed out`_ that I can have "fancy" URLs via the `ARTICLE_PERMALINK_STRUCTURE` setting. So the blog spam you are seeing is a result of my publishing the same two articles with two different URLs (fancy and non-fancy). My apologies for the noise.

publishconf.py
--------------

And actually, I found `ARTICLE_URL` and `ARTICLE_SAVE_AS` to be the settings I wanted to use instead [1]_. My `publishconf.py`_ now looks like this [2]_::

    ARTICLE_SAVE_AS = '/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
    ARTICLE_URL = '/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
    AUTHOR = u'Alex Clark'
    CATEGORY_FEED_ATOM = None
    CATEGORY_FEED_RSS = None
    DEFAULT_CATEGORY = 'Blog'
    DEFAULT_LANG = 'en'
    DEFAULT_PAGINATION = 10
    DELETE_OUTPUT_DIRECTORY = True
    DISQUS_SITENAME = 'aclark-blog'
    GITHUB_URL = 'https://github.com/ACLARKNET/aclarknet.github.com'
    GOOGLE_ANALYTICS = 'UA-34988446-1'
    SITENAME = u'Alex Clark'
    SITEURL = 'https://aclark.net/blog/'
    SOCIAL = (
        ('GitHub', 'http://github.com/aclark4life'),
com/aclark4life'),
        ('PythonPackages', 'https://pythonpackages.com/user/aclark4life'),
        ('Twitter', 'http://twitter.com/aclark4life'),
        ('atom feed (Mozilla)', 'https://aclark.net/blog//Mozilla.atom.xml'),
        ('atom feed (Plone)', 'https://aclark.net/blog//Plone.atom.xml'),
        ('atom feed (Python)', 'https://aclark.net/blog//Python.atom.xml'),
    )
    TAG_FEED_ATOM = 'feeds/%s.atom.xml'
    TAG_FEED_RSS = None
    TWITTER_USERNAME = 'aclark4life'

.. _`Dirkjan Ochtman pointed out`: https://aclark.net/blog//2012/09/21/yes-this-blog-is-now-powered-by-pelican/#comment-658707601
.. _`Pelican`: http://blog.getpelican.com
.. _`publishconf.py`: https://github.com/ACLARKNET/aclarknet.github.com/blob/master/publishconf.py
.. [1] http://pelican.notmyidea.org/en/3.0/settings.html#url-settings
.. [2] I removed the extraneous pelicanconf.py and put everything in one file
