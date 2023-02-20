#!/usr/bin/env python3

#------------------------------------------------------------------------
# Pull Pattern subclass descriptions from their pycode formatting
#------------------------------------------------------------------------

import re
import os
import glob
import argparse

# Look for arguments to output as markdown
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--markdown", action="store_true")
args = parser.parse_args()

# Get all pattern files, excluding __init__'s
pattern_files = list(sorted(glob.glob("isobar/pattern/[!_]*.py", recursive=True)))

classnames = []
classdescs = []

for fname in pattern_files:
    print(fname)

    contents = open(fname, "r").read()

    # Regex for a class and its description
    cmatch = re.search('class\s[^"]*"""((?!""").)*"""', contents, re.S)

    # Loop through for each class in the file
    while cmatch != None:
        name = re.search('(?<=class\s)[^(:]+', cmatch.group(), re.S).group()
        desc = re.search('(?<=""")((?!""").)*', cmatch.group(), re.S).group()
        # Format whitespace for easier output
        desc = re.sub("\n[^\S\r\n]+", " ", desc)
        desc = re.sub("\n\s","\n", desc).strip()
        classnames.append(name)
        classdescs.append(desc)
        # Crop this section out, look for a new match
        contents = contents[cmatch.end():]
        cmatch = re.search('class\s[^"]*"""((?!""").)*"""', contents, re.S)

# Format and print all class names into markdown
