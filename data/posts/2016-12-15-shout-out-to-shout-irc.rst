:title: A Shout Out to Shout IRC
:date: 2016-12-15
:slug: shout-out-to-shout-irc
:tags: Plone, Python
:source: blog-2017
:status: published

I'm back on IRC for the foreseeable future, and loving it. Thank you `Shout IRC <https://thelounge.chat>`_ (now The Lounge).

.. image:: /images/shout-irc2.png
    :align: center
    :class: blog-image

Backlog
-------

A few years ago, I got old and gave up running command line IRC clients. I've run them all or at least a lot of them, including one whose name is almost certainly in the crosshairs of political correctness. Most recently I ran Weechat and irssi before that. For a while, I gave up IRC completely because I couldn't be bothered. But I missed it, and nothing else seemed to suffice. I tried Slack and thought it was OK, but not IRC. I tried various web clients, but couldn't find one I could stand to use long term. Then `Shout IRC <https://thelounge.chat>`_ came along.

Stay online
-----------

I tried Shout for the first time over a year ago, but never bothered to create a Shout account on my server. This was a mistake, since user account creation enables one of Shout's most powerful features: stay online on IRC even when you log out.

Configuration
-------------

I had gotten annoyed with having to login each time, so I stopped using Shout for a while. I heard good things about Kiwi, but was disappointed to see no npm release. This led me back to Shout, which does have an npm release. What follows are configuration details for ``irc.aclark.net``, for posterity. (I added `Let's Encrypt <https://letsencrypt.org>`_ at the last minute for good measure.)

.. image:: /images/shout-irc1.png
    :align: center
    :class: blog-image

AWS
~~~

- EC2 t2.micro running Ubuntu 16.04.1 LTS

Ubuntu
~~~~~~

::

    apt-get install aptitude
    aptitude update; aptitude upgrade -y
    aptitude install nginx nodejs-legacy npm python python-pip

Python
~~~~~~

::

    sudo -H pip install dotfiles

JavaScript
~~~~~~~~~~

::

    sudo npm install -g shout

Certbot (Let's Encrypt)
~~~~~~~~~~~~~~~~~~~~~~~

::

    sudo certbot certonly --manual

NGINX
~~~~~

::

    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;
        return 301 https://$host$request_uri;
    }
    server {
        listen 443 ssl default_server;
        listen [::]:443 ssl default_server;
        root /var/www/html;
        server_name _;
        location / {
            proxy_pass http://localhost:9000;
        }
        ssl    on;
        ssl_certificate    /etc/ssl/fullchain.pem;
        ssl_certificate_key    /etc/ssl/privkey.pem;
    }

Dotfiles
~~~~~~~~

(I store my ``.shout`` directory, which includes my Shout & Freenode credentials, in a private dotfiles repository.)

::

    git clone git@bitbucket.org:aclark4life/dotfiles.git Dotfiles
    dotfiles -s

Conclusion
----------

If you've been looking for a self-hosted IRC web client that keeps you connected around the clock, Shout IRC — now `The Lounge <https://thelounge.chat>`_ — is worth your time. The setup is straightforward, and the always-on feature alone makes it worth running on even the smallest VPS.
