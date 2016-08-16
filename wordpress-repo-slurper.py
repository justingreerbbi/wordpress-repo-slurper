#!/usr/bin/env python3

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
# - Figure out this dang one off error

import urllib.request
import re
import sys
import os.path
import zipfile
import shutil
import _thread
import argparse

parser = argparse.ArgumentParser(description='Which Repository to update')
parser.add_argument('-r','--repo', default='plugins')
parser.add_argument('-t','--treads', type=int, default=10)
args = parser.parse_args()

#
# DETURMINE PARTIAL AND REVISION FILE NAMES
#
if args.repo == 'plugins':
	partial_file = ".partial_plugins"
	revision_file = ".revision_plugins"
	output_dir = "plugins"
elif args.repo == "themes":
	partial_file = ".partial_themes"
	revision_file = ".revision_themes"
	output_dir = "themes"

#
# PLUGIN VERSION
#
slurp_version = "1.0.0"

last_revision = False;
plugins = False
total_plugin_count = 0
start = 0

#
# NUMEBR OF TRHEADS THE SCRIPT CAN USE
#
allowed_threads = args.treads

current_thread_count = 0 

#
# FONT COLORS
#
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
#
# SCRIPT INTRO
#
print ( bcolors.FAIL + "" + bcolors.ENDC )
print ( bcolors.FAIL + bcolors.BOLD + "WordPress Repository Slurper v." + slurp_version + bcolors.ENDC)
print ( bcolors.FAIL + "Slurp all the plugins from the WordPress Repository" + bcolors.ENDC )
print ( bcolors.FAIL + "Contribute to the project at https://github.com/justingreerbbi/plugin-slurper/" + bcolors.ENDC )
print ( bcolors.FAIL + "Please report all bugs and issues at https://github.com/justingreerbbi/plugin-slurper/issues" + bcolors.ENDC )
print ( bcolors.FAIL + "" + bcolors.ENDC )
print("")

# 
# TREADING FUNCTION THAT CAN BE CALLED USING AN INDEX
# 
def updatePlugin( x ):
	global current_thread_count

	# FEEBACK
	print ("Slurping on " + plugins[x].decode("utf-8").rstrip("/") )
 
	# SETUP
	local_zip = output_dir + "/" + plugins[x].decode("utf-8").rstrip("/") + ".zip"

	# DOWNLAOD
	if args.repo == 'themes':
		zip_url = "https://downloads.wordpress.org/theme/"+plugins[x].decode("utf-8").rstrip("/")+".latest-stable.zip?nostats=1"
	elif args.repo == 'plugins':
		zip_url = "http://downloads.wordpress.org/plugin/"+plugins[x].decode("utf-8").rstrip("/")+".latest-stable.zip?nostats=1"
	
	try:
		urllib.request.urlretrieve( zip_url, local_zip )
	except urllib.error.URLError as e:
		print (bcolors.FAIL + "Slurp failed for " + plugins[x].decode("utf-8").rstrip("/") +  bcolors.ENDC)
		current_thread_count-=1
		return

	# UNPACK
	if zipfile.is_zipfile( local_zip ):
		zip_ref = zipfile.ZipFile( local_zip, 'r' )
		zip_ref.extractall( output_dir )
		zip_ref.close()
	else:
		print (bcolors.FAIL + "Failed to unpack " + plugins[x].decode("utf-8").rstrip("/") +  bcolors.ENDC)

	# LOG AND CLEANUP
	rev_file = open(partial_file, "w+")
	rev_file.write( str( x ) )
	rev_file.close()
	os.remove( local_zip )
	current_thread_count-=1
			

#
# CHECK FOR PARTIAL DOWNLOAD
# ASK USER IF THEY WANT TO CONTINUE TO DOWNLOAD
#
if os.path.isfile(partial_file):
	user_input = input("Continue download? Yes or No: ")
	if user_input.lower() == "no":
		print ( bcolors.BOLD + "Deleting partial download data. Please wait..." + bcolors.ENDC )
		print ("")
		os.remove(partial_file)
		if os.path.isdir(output_dir):
			shutil.rmtree(output_dir)
		if os.path.isfile(revision_file):
			os.remove(revision_file)
	elif user_input.lower() == 'yes':
		partial = open(partial_file, "r")
		partial_content = partial.read()
		if partial_content.strip() != "":
			start = int( partial_content.strip() )
		else:
			start = 0

#
# DEPENDANT THINGYS
#
if not os.path.exists( output_dir ):
    os.makedirs( output_dir )

#
# GET THE CURRENT REVISION NUMBER
# 
if args.repo == "themes":
	changelog_url = "https://themes.trac.wordpress.org/log/?format=changelog&stop_rev=HEAD"
elif args.repo == "plugins":
	changelog_url = "https://plugins.trac.wordpress.org/log/?format=changelog&stop_rev=HEAD"

f = urllib.request.urlopen( changelog_url )
content = f.read()
svn_last_revision = re.search(b"\[([0-9]+)\]", content)

if svn_last_revision:
	print ("Remote at " + bcolors.BOLD + svn_last_revision.group(1).strip().decode('utf-8') + bcolors.ENDC)
else:
	print ("Could not determine remote revision. Perhaps the server is down?")


# IF THERE IS A REVISION
# - CHECK IF IT MATCHED THE REMOTE
# - IF THE REVISON DOES NOT MATCH THE REMOTE THEN GET THE DIFF IN VERSION NUMBERS
if os.path.isfile(revision_file):

	f = open(revision_file)
	f_text = f.read()
	rev = re.search("\[([0-9]+)\]", f_text)
	last_revision = rev.group(1)

	if int(last_revision) == int(svn_last_revision.group(1)):
		print (bcolors.OKGREEN + bcolors.BOLD + "Hooray! You are up-to-date." + bcolors.ENDC + bcolors.ENDC)
		print ("")
		sys.exit()
	else:
		print ("Local at " + bcolors.BOLD + last_revision + bcolors.ENDC + " (out-dated)")
		print ("") 
		print (bcolors.BOLD + "Retrieving changelog. Please wait..." + bcolors.ENDC)
		print ("")

		svn_diff = int(svn_last_revision.group(1).decode("UTF-8")) - int(last_revision)
		if args.repo == "themes":
			svn_changelog_url = "https://themes.trac.wordpress.org/log/?verbose=on&mode=follow_copy&format=changelog&rev="+str(svn_last_revision.group(1).decode("UTF-8"))+"&limit="+str(svn_diff)
		elif args.repo == "plugins":
			svn_changelog_url = "https://plugins.trac.wordpress.org/log/?verbose=on&mode=follow_copy&format=changelog&rev="+str(svn_last_revision.group(1).decode("UTF-8"))+"&limit="+str(svn_diff)

		try:
			changelog_content = urllib.request.urlopen(svn_changelog_url)
		except urllib.error.URLError as e:
			print (bcolors.FAIL + "The changelog does not seem to be reachable. (" + e.reason + ")" + bcolors.ENDC)
			sys.exit()

		changelog_content = changelog_content.read()
		plugins = re.findall(b'\s*\* ([^/A-Z ]+)', changelog_content)
		plugins = list(set(plugins))
		total_plugin_count = len(plugins)

else:
	print ("No local revision found. Sit tight because this could take a while.")
	print ("")

	if args.repo == "themes":
		plugin_url = urllib.request.urlopen("http://themes.svn.wordpress.org");
	elif args.repo == "plugins":
		plugin_url = urllib.request.urlopen("https://plugins.svn.wordpress.org");
	plugin_list = plugin_url.read()
	plugins = re.findall(b'<li><a href="(.+)">', plugin_list)
	total_plugin_count = len(plugins)


while start < total_plugin_count+1:
	if current_thread_count < allowed_threads:
		current_thread_count+=1
		_thread.start_new_thread( updatePlugin, (start, ) )
		start+=1

## SIMPLE TRICK TO KEEP THE SCRIPT ALIVE UNTIL ALL THE PLUGINS ARE DOWNLOADED
while start < total_plugin_count:
	pass

rev_file = open(revision_file, "w+")
rev_file.write( svn_last_revision.group(0).decode("UTF-8") )
rev_file.close();

# REMOVE PARTIAL FILE
if os.path.isfile(partial_file):
	os.remove(partial_file)

# SCRIPT IS COMPLETE
print ("")
print (bcolors.BOLD + "Complete" + bcolors.ENDC)

