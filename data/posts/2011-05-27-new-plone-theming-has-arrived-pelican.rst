:title: "New" Plone theming has arrived
:date: 2011-05-27
:slug: new-plone-theming-has-arrived-pelican
:source: pelican-blog
:status: published

"New" Plone theming has arrived
 Tweet





                Fri 27 May 2011



                By  aclark

 In  Blog .
 tags:  Plone
        Edit2: Enfold/Ploud.net looking for theme developers, see Alan
Runyan's comment below.
 Edit : Laurence Rowe made new Diazo and plone.app.theming releases so
the  zip file now works! Thanks Laurence.
 Due to the new Diazo theming features now available, I am very excited
about the recent release of  Plone 4.1rc2  and  plone.app.theming
1.0b2 . So much so, I created a couple themes (in just a few hours) to
demonstrate my  rapture [1] :

 (released)
 http://pypi.python.org/pypi/plonetheme.unilluminated/0.1.0
 (unreleased)  https://github.com/aclark4life/plonetheme.coolblue

 Granted, these aren't entirely "finished" (e.g. lots of CSS improvements
are needed) but it is truly impressive how much you can do with so
little effort (thanks to the hard work of the Diazo team, Plone team,
and of course the theme designers themselves).
 The best part has got to be the  zip file packaging features  in
plone.app.theming (provided by  plone.resource ). While I did have a
bit of trouble getting  my zip file  to work, I suspect I'll get that
issue resolved this week (I don't think I was able to import any zipped
themes, even the ones from p.a.theming tests).

 Suprise! I like it
 What I am most surprised about is how much I like this approach:

 Developers can easily distribute themes in Python packages, and pay a
much smaller "theming tax" with new style Diazo theming.
 They can also optionally choose to distribute Diazo themes as zip
files for easy public consumption (although I can't think of any
good, automated way to publish just the zip files.)
 If I am not mistaken the contents of a zipped theme can be loaded
 quite elegantly , without changing their contents, via a  Python
package .

 So, let us now commence the spamming of PyPI and the  Plone.org
downloads section  with "fun" easy-to-install (read: no buildout) Plone
themes! [2]


 Disclaimer
 These are my experiences with relatively new Plone technologies. If I've
made a mistake or if your experiences are different, please let me know
in the comments.
 [1] Please forgive gratuitous belated rapture humor.
 [2] Before you get upset over any suggested spamming, I only mean to
suggest that the ability to distribute a theme as a zip file lowers the
bar to Plone adoption tremendously. Personally (and tentatively, since
I'm not even sure if everything is meant to work the way I currently
expect it to), I plan to include a zipped archive of any theme I
distribute as a Python package because it is so easy to do so (or
hopefully will be very soon). But how the community chooses to
capitalize on this new-found ability remains to be seen.




       Comments !


        var disqus_identifier = "2011/05/27/quotnewquot-plone-theming-has-arrived/";
        var disqus_url = "http://blog.aclark.net/2011/05/27/quotnewquot-plone-theming-has-arrived/";
        (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = 'http://aclark-blog.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
