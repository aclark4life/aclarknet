:title: SELinux: 0, Alex Clark: 1
:date: 2023-11-19
:slug: selinux-0-alex-clark-1
:source: blog
:status: published

|

.. image:: /images/selinux-0-alex-clark-1.jpg
    :align: center
    :class: blog-image

(work in progress)

Introduction
------------

I don’t like to give up on a technical challenge, particularly when the progress is slow-but-consistent. It’s only when I know I can’t make any discernible progress easily or at all that I can force myself to give up.

Sound familiar? I wrote about a `similar encounter six years ago <https://blog.aclark.net/2017/06/26/saml-1-alex-clark-0.html>`_!

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


Light Bulb
----------

|

Conclusion
----------

|
