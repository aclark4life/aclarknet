:title: SELinux: 0, Alex Clark: 1
:date: 2023-11-19
:slug: selinux-0-alex-clark-1
:source: blog
:status: draft

|

.. image:: /images/selinux-0-alex-clark-1.jpg
    :align: center
    :class: blog-image

Introduction
------------

I don’t like to give up on a technical challenge, particularly when the progress is slow-but-consistent. It’s only when I know I can’t make any discernible progress easily or at all that I can force myself to give up.

Sound familiar? I wrote about a `similar encounter six years ago <https://aclark.net/blog/2017/06/26/saml-1-alex-clark-0/>`_!

The task at hand
----------------

Now the task at hand is running Samba on Rocky Linux 9. For years I ran File Sharing on a 2010 Mac Pro running Sierra and recent circumstances led me to replace that server with an HP Envy laptop with 11G RAM. It's a surprisingly good server!

.. image:: /images/server-2023.jpg

It's been a lot of fun building out the services on this laptop running Rocky Linux 9, including:

- Jenkins
- RedHat Cockpit
- Microsoft Remote Desktop

Having Samba fail mysteriously was not fun, and I should have known better than to go down any rabbit hole without first considering SE Linux, but what can I say? I've been out of the game for a while. Eventually I prevailed and this is the story of that encounter.

Attempts
--------

My recent encounter with Samba on Rocky Linux was embarrasingly long, but it started off normal.

In the beginning
~~~~~~~~~~~~~~~~

If you Google or ChatGPT "Samba on Rocky Linux" you'll get steered toward something like:

::

    sudo dnf install xrdp

Followed by some firewall instructions and, if you are lucky, some SE Linux instructions. If you are unlucky, you will proceed merrily with:

::

    sudo systemctl enable smb
    sudo systemctl start smb

After which you can delight in ``sudo systemctl status smb``:

::

    parkwoodstudios➜  ~  ᐅ  sudo systemctl status smb
    ● smb.service - Samba SMB Daemon
         Loaded: loaded (/usr/lib/systemd/system/smb.service; enabled; preset: disabled)
         Active: active (running) since Sat 2023-11-18 15:04:46 EST; 23h ago
           Docs: man:smbd(8)
                 man:samba(7)
                 man:smb.conf(5)
       Main PID: 1655 (smbd)
         Status: "smbd: ready to serve connections..."
          Tasks: 4 (limit: 72791)
         Memory: 51.0M
            CPU: 3.761s
         CGroup: /system.slice/smb.service
                 ├─1655 /usr/sbin/smbd --foreground --no-process-group
                 ├─1880 /usr/sbin/smbd --foreground --no-process-group
                 ├─1881 /usr/sbin/smbd --foreground --no-process-group
                 └─3992 /usr/sbin/smbd --foreground --no-process-group

    Nov 18 15:04:46 parkwoodstudios systemd[1]: Starting Samba SMB Daemon...
    Nov 18 15:04:46 parkwoodstudios smbd[1655]: [2023/11/18 15:04:46.273770,  0] ../../source3/smbd/server.c:1741(main)
    Nov 18 15:04:46 parkwoodstudios smbd[1655]:   smbd version 4.17.5 started.
    Nov 18 15:04:46 parkwoodstudios smbd[1655]:   Copyright Andrew Tridgell and the Samba Team 1992-2022
    Nov 18 15:04:46 parkwoodstudios systemd[1]: Started Samba SMB Daemon.

Unfortunately, the joyfulness will end when you try to connect, even though the ports are open:

::

    ╰─(blog) ⠠⠵ sudo nmap 192.168.1.2
    Password:
    Starting Nmap 7.94 ( https://nmap.org ) at 2023-11-19 14:20 EST
    Nmap scan report for parkwoodstudios.fios-router.home (192.168.1.2)
    Host is up (0.022s latency).
    Not shown: 979 filtered tcp ports (no-response), 15 filtered tcp ports (admin-prohibited)
    PORT     STATE SERVICE
    22/tcp   open  ssh
    139/tcp  open  netbios-ssn
    445/tcp  open  microsoft-ds
    3389/tcp open  ms-wbt-server
    8080/tcp open  http-proxy
    9090/tcp open  zeus-admin
    MAC Address: 30:24:32:39:7F:E7 (Intel Corporate)

    Nmap done: 1 IP address (1 host up) scanned in 9.30 seconds

I would love to say I immediately recognized the issue as being related to SE Linux, but I didn't. In fact, I went in the opposite direction:

  "Maybe the version of Samba is too old!"

And then there was hombrew, and the brew was good
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

My experience with Homebrew on macOS led me to try running Samba on Linux via Homebrew. It worked! The Samba version was newer, and the connection worked fine. Unfortunately I couldn't get systemd to run the Homebrew version of Samba, so after fighting with that for a while, I gave up.

What source have you compiled for me lately?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next I tried compiling Samba from source. This is the kind of thing that sounds reasonable at 11pm after a long day of troubleshooting. I pulled the latest tarball, worked through the dependency chain (and there are many), and eventually got a build. It connected! But like the Homebrew attempt, I couldn't get systemd to manage it cleanly, and the whole exercise felt like I was solving the wrong problem.

At this point I had spent the better part of two days on something that should have taken twenty minutes. I had a working Samba — just not one I could live with.

Light Bulb
----------

I finally did what I should have done on day one: checked ``/var/log/audit/audit.log``.

::

    type=AVC msg=audit(1700340286.123:456): avc:  denied  { read } for  pid=1655
    comm="smbd" name="shared" dev="sda1" ino=12345
    scontext=system_u:system_r:smbd_t:s0
    tcontext=unconfined_u:object_r:user_home_t:s0 tclass=dir permissive=0

There it was. SELinux was silently blocking Samba from reading the share directory because it was labeled ``user_home_t`` instead of ``samba_share_t``. The service was running fine. The ports were open. SELinux was just quietly saying no.

The fix was two commands:

::

    sudo semanage fcontext -a -t samba_share_t "/srv/shares(/.*)?"
    sudo restorecon -R /srv/shares

And then, for good measure:

::

    sudo setsebool -P samba_enable_home_dirs on

Connection successful. Every machine on the network could see the share immediately.

Conclusion
----------

The lesson, which I have now learned twice (see the `SAML post <https://aclark.net/blog/2017/06/26/saml-1-alex-clark-0/>`_), is: on RHEL-family systems, check SELinux first. Not second, not after you've compiled software from source at midnight — first.

SELinux gets a bad reputation for being opaque and frustrating, and I won't pretend the audit log is pleasant reading. But it is doing its job, and once you know where to look, the fix is usually straightforward. The real culprit here was my own tunnel vision.

Score: SELinux 0, Alex Clark 1. But only just.
