#!/usr/bin/env python

# Copyright (C) 2006-2010, University of Maryland
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/ or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Author: James Krycka

"""
This script uses py2exe to create dist\refl1d.exe for Windows.

The resulting executable bundles the Refl1d application, the python runtime
environment, and other required python packages into a single file.  Additional
resource files that are needed when Refl1d is run are placed in the dist
directory tree.  On completion, the contents of the dist directory tree can be
used by the Inno Setup Compiler (via a separate script) to build a Windows
installer/uninstaller for deployment of the Refl1d application.  For testing
purposes, refl1d.exe can be run from the dist directory.
"""

import os
import sys

root = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(root, "dream"))
print "*** Python path is:"
for i, p in enumerate(sys.path):
    print "%5d  %s" %(i, p)

from distutils.core import setup

# Augment the setup interface with the py2exe command and make sure the py2exe
# option is passed to setup.
import py2exe

if len(sys.argv) == 1:
    sys.argv.append('py2exe')

import matplotlib
import periodictable

# Retrieve the application version string.
from version import version

# Create a manifest for use with Python 2.5 on Windows XP.  This manifest is
# required to be included in a py2exe image (or accessible as a file in the
# image directory) when wxPython is included so that the Windows XP theme is
# used when rendering wx widgets.  The manifest below is adapted from the
# Python manifest file (C:\Python25\pythonw.exe.manifest).
#
# Note that a different manifest is required if using another version of Python.

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="0.64.1.0"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>DiRefl</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
"""

# Create a list of all files to include along side the executable being built
# in the dist directory tree.  Each element of the data_files list is a tuple
# consisting of a path (relative to dist\) and a list of files in that path.
data_files = []

# Add data files from the matplotlib\mpl-data folder and its subfolders.
# For matploblib prior to version 0.99 see the examples at the end of the file.
data_files = matplotlib.get_py2exe_datafiles()

# Add data files from the periodictable\xsf folder.
data_files += periodictable.data_files()

# Add resource files that need to reside in the same directory as the image.
#data_files.append( ('.', [os.path.join('.', 'refl1d.ico')]) )
#data_files.append( ('.', [os.path.join('.', 'LICENSE.txt')]) )
#data_files.append( ('.', [os.path.join('.', 'README.txt')]) )

# Specify required packages to bundle in the executable image.
packages = ['numpy', 'scipy', 'matplotlib', 'pytz', 'pyparsing', 'wx',
            'periodictable', 'refl1d.names']

# Specify files to include in the executable image.
includes = []

# Specify files to exclude from the executable image.
# - We can safely exclude Tk/Tcl and Qt modules because our app uses wxPython.
# - We do not use ssl services so they are omitted.
# - We can safely exclude the TkAgg matplotlib backend because our app uses
#   "matplotlib.use('WXAgg')" to override the default matplotlib configuration.
# - On the web it is widely recommended to exclude certain lib*.dll modules
#   but this does not seem necessary any more (but adding them does not hurt).
# - Python25 requires mscvr71.dll, however, Win XP includes this file.
# - Since we do not support Win 9x systems, w9xpopen.dll is not needed.
# - For some reason cygwin1.dll gets included by default, but it is not needed.

excludes = ['Tkinter', 'PyQt4', '_ssl', '_tkagg']

dll_excludes = ['libgdk_pixbuf-2.0-0.dll',
                'libgobject-2.0-0.dll',
                'libgdk-win32-2.0-0.dll',
                'tcl84.dll',
                'tk84.dll',
                'QtGui4.dll',
                'QtCore4.dll',
                'msvcr71.dll',
                'w9xpopen.exe',
                'cygwin1.dll']

class Target():
    """This class stores metadata about the distribution in a dictionary."""

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = version

client = Target(
    name = 'refl1d',
    description = 'Refl1d command line application',
    script = 'bin/reflfit',  # module to run on application start
    dest_base = 'refl1d',  # file name part of the exe file to create
    #icon_resources = [(1, 'refl1d.ico')],  # also need to specify in data_files
    bitmap_resources = [],
    other_resources = [(24, 1, manifest)])

# Now do the work to create a standalone distribution using py2exe.
# Specify either console mode or windows mode build.
#
# When the application is run in console mode, a console window will be created
# to receive any logging or error messages and the application will then create
# a separate GUI application window.
#
# When the application is run in windows mode, it will create a GUI application
# window and no console window will be provided.
setup(
      console=[client],
      #windows=[client],
      options={'py2exe': {
                   'packages': packages,
                   'includes': includes,
                   'excludes': excludes,
                   'dll_excludes': dll_excludes,
                   ###'compressed': 1,   # standard compression
                   'compressed': 0,   # standard compression
                   'optimize': 0,     # no byte-code optimization
                   'dist_dir': "dist",# where to put py2exe results
                   'xref': False,     # display cross reference (as html doc)
                   ###'bundle_files': 1  # bundle python25.dll in executable
                   'bundle_files': 3  # bundle python25.dll in executable
                         }
              },
      ###zipfile=None,                   # bundle files in exe, not in library.zip
      data_files=data_files           # list of files to copy to dist directory
     )
