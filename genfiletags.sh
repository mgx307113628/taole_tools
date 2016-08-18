#!/bin/sh
# generate tag file for lookupfile plugin

echo $1"......"
echo -e "!_TAG_FILE_SORTED\t2\t/2=foldcase/"> $2
D:/cygwin64/bin/find $1 -not -regex '.*\.\(png\|gif\|pyo\|swp\|pyc\|o$\|project\|pydevproject\)' ! -path "*git*" ! -path "*svn*" ! -path "*idea*" ! -path "*komodotools*" -type f -printf "%f\t%p\t1\n" | D:/cygwin64/bin/sort -f >> $2

