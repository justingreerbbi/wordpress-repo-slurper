# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation under GPL v1

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# TODO's
# - Add progress tracking to prevent having to re-download the entire library if there is an interruption in downloading.

import urllib
import re
import sys
import os.path
import zipfile
import shutil

slurp_version = "1.0.0"

local_revision = False;


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print bcolors.FAIL + "" + bcolors.ENDC
print bcolors.FAIL + bcolors.BOLD + "WordPress Plugin Slurp v." + slurp_version + bcolors.ENDC
print bcolors.FAIL + "Slurp all the plugins from the WordPress Repository" + bcolors.ENDC
print bcolors.FAIL + "This software is beta and should only be used as a tool for plugin moderators and administrators." + bcolors.ENDC
print ""

#
# CHECK FOR PARTIAL DOWNLOAD
# ASK USER IF THEY WANT TO CONTINUE TO DOWNLOAD
#
if os.path.isfile(".partial"):
	user_input = raw_input("Continue download? Yes or No: ")
	if user_input.lower() == "no":
		print "Deleting partial download..."
		print ""
		os.remove(".partial")
		if os.path.isdir("plugins"):
			shutil.rmtree("plugins")

#
# DEPENDANT THINGYS
#
if not os.path.exists( "plugins" ):
    os.makedirs("plugins")

#
# GET THE CURRENT REVISION NUMBER
# 
chnagelog_url = "http://plugins.trac.wordpress.org/log/?format=changelog&stop_rev=HEAD"

#print "Fetching most recent repository revision..."
f = urllib.urlopen( chnagelog_url )
content = f.read()
svn_last_revision = re.search("\[([0-9]+)\]", content)

if svn_last_revision:
	print "Remote at " + bcolors.BOLD + svn_last_revision.group(1).strip() + bcolors.ENDC

	# Check to see if there is a local copy of the plugin repository already
	if os.path.isfile(".revision"):
		f = open(".revision")
		f_text = f.read()
		rev = re.search("\[([0-9]+)\]", f_text)
		if rev: 
			last_revision = rev.group(1)

			# Only stop if the rev numbers both match
			if int(local_revision) >= int(svn_last_revision.group(1)):
				print bcolors.OKGREEN + bcolors.BOLD + "You are up-to-date" + bcolors.ENDC + bcolors.ENDC
				print ""
				#sys.exit()
			else:
				print "Local at " + bcolors.BOLD + last_revision + bcolors.ENDC + " (out-dated)"
				print "" 

		else:
			last_revision = False
			print "No local revision found."

	else:

		# Create a data file with the revision
		rev_file = open(".revision", "w")
		rev_file.write( svn_last_revision.group(0))
		rev_file.close();
		
		last_revision = False
		print "No local revision found. Sit tight because this could take a while"
		print ""

else:
	print "Could not determine remote revision. Perhaps the server is down?"

#
# GET THE PLUGIN LIST
# 
#print ""
print "Retrieving plugin SVN plugin list... Please wait."
plugin_url = urllib.urlopen("http://svn.wp-plugins.org");
plugin_list = plugin_url.read()
plugins = re.findall('<li><a href="(.+)">(.+)</a></li>', plugin_list)

# Get Count of the list so that we can track progress
# TODO: This is too excessive. We should not be calling the server twice.
total_plugin_count = re.subn('<li><a href="(.+)">(.+)</a></li>',"", plugin_list)[1]
current_plugin_count = 1

# CHECK IF THERE IS A PARTIAL DOWNLOAD DONE
start = 0
if os.path.isfile(".partial"):
	f = open(".partial", "r")
	start = int(f.read())
	print "Resuming at " + plugins[start][0]
	print ""


#print plugin_count 
for x in range( start, total_plugin_count):
	rev_file = open(".partial", "w+")
	rev_file.write( str( x ) )

	# FEEBACK
	print "Updating " + plugins[x][1].rstrip("/")
 
	# SETUP
	local_zip = "plugins/" + plugins[x][1].rstrip("/") + ".zip"
	local_dir = "plugins"

	# DOWNLAOD
	plugin_zip_url = "http://downloads.wordpress.org/plugin/"+plugins[x][1].rstrip("/")+".latest-stable.zip?nostats=1"
	urllib.urlretrieve( plugin_zip_url, local_zip )

	# UNPACK
	if zipfile.is_zipfile( local_zip ):
		zip_ref = zipfile.ZipFile( local_zip, 'r' )
		zip_ref.extractall( local_dir )
		zip_ref.close()
	else:
		print bcolors.FAIL + "Update Failed for " + plugins[x][1].rstrip("/") +  bcolors.ENDC

	# CLEANUP
	os.remove( local_zip )

rev_file.close()
os.remove(".partial")
sys.exit()