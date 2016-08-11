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

last_revision = False;
plugins = False
total_plugin_count = 0
start = 0

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
		if os.path.isfile(".revision"):
			os.remove(".revision")

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
else:
	print "Could not determine remote revision. Perhaps the server is down?"


# IF THERE IS A REVISION
# - CHECK IF IT MATCHED THE REMOTE
# - IF THE REVISON DOES NOT MATCH THE REMOTE THEN GET THE DIFF IN VERSION NUMBERS
if os.path.isfile(".revision"):
	f = open(".revision")
	f_text = f.read()
	rev = re.search("\[([0-9]+)\]", f_text)
	last_revision = rev.group(1)

	# Only stop if the rev numbers both match
	if int(last_revision) == int(svn_last_revision.group(1)):
		print bcolors.OKGREEN + bcolors.BOLD + "You are up-to-date" + bcolors.ENDC + bcolors.ENDC
		print ""
	else:
		print "Local at " + bcolors.BOLD + last_revision + bcolors.ENDC + " (out-dated)"
		print "" 
		print "Retrieving changelog... Please wait."

		svn_diff = int(svn_last_revision.group(1)) - int(last_revision)
		svn_changelog_url = "http://plugins.trac.wordpress.org/log/?verbose=on&mode=follow_copy&format=changelog&rev="+str(svn_last_revision.group(1))+"&limit="+str(svn_diff)

		changelog_content = urllib.urlopen(svn_changelog_url)
		changelog_content = changelog_content.read()
		plugins = re.findall('\s*\* ([^/A-Z ]+)', changelog_content)

		global plugins, total_plugin_count
		plugins = list(set(plugins))
		total_plugin_count = len(plugins)

else:
	rev_file = open(".revision", "w+")
	rev_file.write(svn_last_revision.group(0))
	rev_file.close();
	
	print "No local revision found. Sit tight because this could take a while."
	print ""

	plugin_url = urllib.urlopen("http://svn.wp-plugins.org");
	plugin_list = plugin_url.read()

	global plugins, total_plugin_count
	plugins = re.findall('<li><a href="(.+)">', plugin_list)
	total_plugin_count = len(plugins)



#
# GET THE REQUIRED PLUGIN LIST
# 
for x in range( start, total_plugin_count):

	rev_file = open(".partial", "w+")
	rev_file.write( str( x ) )
	rev_file.close()

	# FEEBACK
	print "Updating " + plugins[x].rstrip("/")
 
	# SETUP
	local_zip = "plugins/" + plugins[x].rstrip("/") + ".zip"
	local_dir = "plugins"

	# DOWNLAOD
	plugin_zip_url = "http://downloads.wordpress.org/plugin/"+plugins[x].rstrip("/")+".latest-stable.zip?nostats=1"
	urllib.urlretrieve( plugin_zip_url, local_zip )

	# UNPACK
	if zipfile.is_zipfile( local_zip ):
		zip_ref = zipfile.ZipFile( local_zip, 'r' )
		zip_ref.extractall( local_dir )
		zip_ref.close()
	else:
		print bcolors.FAIL + "Update Failed for " + plugins[x].rstrip("/") +  bcolors.ENDC

	# CLEANUP
	os.remove( local_zip )

if os.path.isfile(".partial"):
	os.remove(".partial")

# SCRIPT IS COMPLETE
print bcolors.BOLD + "Plugin Slurp Complete" + bcolors.ENDC
print ""
sys.exit()