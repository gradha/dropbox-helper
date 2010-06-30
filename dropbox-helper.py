#!/usr/bin/env python
# vim:tabstop=4 shiftwidth=4 encoding=utf-8
"""Dropbox helper.
"""

import logging
import optparse
import os
import os.path
import shutil
import subprocess
import sys
import unicodedata
import urllib


DROPBOX_BASE = os.path.expanduser(u"~/Dropbox/Public/")
PUBLIC_BASE = u"http://dl.dropbox.com/u/145894/"


def process_arguments(argv):
	"""f([string, ...]) -> (string, [string, ...])

	Returns the relative directory to put files and the files themselves.
	"""
	parser = optparse.OptionParser()
	parser.add_option("-m", "--move", dest="move", action="store_true",
		default = False, help = "delete source after successful copy")
	parser.add_option("-d", "--dir", dest="dir", default = u"t",
		help = "subdirectory where you want the files placed.")
	(options, args) = parser.parse_args()

	if not args:
		print "Specify some files, please."
		print "Base URL %s" % PUBLIC_BASE
		parser.print_help()
		sys.exit(1)

	encoding = sys.getfilesystemencoding()
	options.dir = unicodedata.normalize("NFC", options.dir.decode(encoding))
	return (options,
		[unicodedata.normalize("NFC", x.decode(encoding)) for x in args])


def copy_to_dropbox(relative_directory, source_path):
	"""f(string, string) -> string

	Copies the file to the specified relative directory and
	returns the uuencoded URL to copy&paste to the external
	world.
	"""
	assert isinstance(relative_directory, unicode)
	dest_path = os.path.normpath(os.path.join(DROPBOX_BASE, relative_directory,
		os.path.basename(source_path)))
	shutil.copyfile(source_path, dest_path)
	return path_to_url(dest_path)


def path_to_url(path):
	"""f(ustring) -> string

	Returns the local directory of a dropbox file as the public url escaped.
	Note that the returned string is 8-bit ascii, utf8 encoded.
	"""
	assert isinstance(path, unicode)
	assert is_already_in_dropbox(path)
	path = os.path.realpath(path)
	relative_url = urllib.quote(path[len(DROPBOX_BASE):].encode("utf-8"))
	return os.path.join(PUBLIC_BASE, relative_url)


def is_already_in_dropbox(path):
	"""f(string) -> bool

	Returns True if the file is already in the Dropbox folder.
	"""
	assert isinstance(path, unicode)
	real_path = os.path.realpath(path)
	if real_path[:len(DROPBOX_BASE)] == DROPBOX_BASE:
		return True
	else:
		return False


def main():
	"""f() -> None

	Main entry point of the application.
	"""
	options, to_process = process_arguments(sys.argv)
	to_clipboard = []
	for path in map(os.path.realpath, to_process):
		if not os.path.isfile(path):
			print "Error, invalid file %r" % (path)
			continue

		if is_already_in_dropbox(path):
			url = path_to_url(path)
		else:
			url = copy_to_dropbox(options.dir, path)
			if options.move:
				os.unlink(path)

		to_clipboard.append(url)
		print url

	# Also copy the urls to the macosx pasteboard.
	if to_clipboard:
		clipboard = subprocess.Popen(["pbcopy"], stdin = subprocess.PIPE)
		clipboard.communicate("\n".join(to_clipboard))


if "__main__" == __name__:
	logging.basicConfig(level = logging.INFO)
	#logging.basicConfig(level = logging.DEBUG)
	main()
