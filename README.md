WordPress Repo Slurper
========================

A command line Python 3.X script that downloads and updates a copy of the latest stable
version of every plugin and or theme in the WordPress repo.

Improvements over PHP
---------------------

* Threaded support. Downloads 10x faster than PHP
* Partial download support for initial download
* Support both plugins and themes in one script

Common Issues
-------------

* Since the Slurper is not a true SVN client, you may be missing some plugins if you take too long to do the initial 
download. It is possible that we can track revisions for the initial download but currently just do the initial download
is a reasonable time.

Requirements
------------

* Python 3.x

Instructions
------------

1. `cd WordPress-Repo-Slurper`
2. `./python plugin-slurper.py`

### Options ###

* -r / repo 'plugins' or 'themes' - Which repo you will slurp on (defaults to plugins).
* -t / threads - Number of threads to run on while slurping (defaults to 10).

### Example ###

`.wordpress-repo-slurper.py [-r/repo]=plugins|themes [-t/threads]=1-20`

The `plugins/` directory will contain all the plugins, when the script is done.

FAQ
----

### How long will it take? ###

Initial run will take between 8-16 hours. Updates over revisions take a matter of minutes if not seconds.

### How much disk space do I need? ###

Questionable. I will get back to you.

### I don't have 18 hours straight. Can I do Partial Updates? ###

The script is designed to store the last index so even if you kill the script, the script will track the last downloaded index. 
If there is a partial update during launch of the script, the script will ask if you want to continue with the download.

Things could get hairy if there is a big difference in revisions between partial downloads. This is just a theory and not tested yet.
Feel free to test away and contribute to the project.
