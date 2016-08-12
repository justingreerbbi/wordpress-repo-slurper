WordPress Plugin Slurper
========================

A command line Python 3.X script that downloads and updates a copy of the latest stable
version of every plugin in the WordPress repo.

This script is model after the WordPress Plugin Directory Slurper built with PHP https://github.com/markjaquith/WordPress-Plugin-Directory-Slurper

Improvements over PHP
---------------------

* Threaded support. Downloads 10x faster than PHP
* Partial download support for initial download

Common Issues
-------------

* Since the Slurper is not a true SVN client, you may be missing some plugins if you take too long to do the initial 
download. It is possible that we can track revisions for the initial download but currently just do the initial download
is a reasonable time.

Requirements
------------

* Python 3.x(tested with 2.7)

Instructions
------------

1. `cd plugin-slurper`
2. `python3 or python plugin-slurper.py`

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
