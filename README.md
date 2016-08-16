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

* Since the Slurper is not a true SVN client, you may be missing some plugins/themes if you take too long to do the initial 
download.

Requirements
------------

* Python 3.x

Instructions
------------

1. `cd wordpress-repo-slurper`
2. `./wordpress-repo-slurper.py`

### Options ###

* -r / repo 'plugins' or 'themes' - Which repo you will slurp on (defaults to plugins).
* -t / threads - Number of threads to run on while slurping (defaults to 10).

### Example ###

`./wordpress-repo-slurper.py [-r/repo] plugins|themes [-t/threads] 1-20`

The `plugins` directory will contain all the plugins
The `themes` directory will contain all the themes

FAQ
----

### How long will it take? ###

* Plugins - ~4hr (@ 50mb/s)
* Themss - ~ 28mins (@ 50mb/s)

### How much disk space do I need? ###

* Plugins - TBD
* Themes - ~4GB
