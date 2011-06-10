#! /usr/bin/env python2

"""
File: main.py
Author: Revolt
Date: 15-08-2010
--------------------------
Desc:
    This file initializes the wx application and starts the main
    application loop.
--------------------------
Copyright (C) 2010 Revolt 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx, os, sys
from frmMain import *

scriptFolder = os.path.dirname(sys.argv[0])

if scriptFolder != '':
    os.chdir(scriptFolder)

try:
    sys.stdout = open("out.txt", "w")
    sys.stderr = open("err.txt", "w")
except:
    pass

app = wx.App(False)
frame = frmMain()
frame.Show(True)
app.MainLoop()
