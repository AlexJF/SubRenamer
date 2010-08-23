#! /usr/bin/env python

"""
File: frmMain.py
Author: Revolt
Date: 15-08-2010
--------------------------
Desc:
    This file contains the definition and implementation of the main
    frame of the application
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


import wx, os
from func import *
from wx import xrc

# --------------------- frame Class -----------------------

class frmMain:
    """ The main frame of the application """

    # Saves the last used location to prevent excessive browsing by the user 
    lastVidLocation = ""
    lastSubLocation = ""

    # These lists are at the heart of the undo/redo system
    undoStack = []
    redoStack = []

    def __init__(self):
        """ Constructor """

        # -- XRC and Frame Loading
        self.res = xrc.XmlResource("gui.xrc")
        self.frm = self.res.LoadFrame(None, 'frmMain')

        # -- Control referencing --
        self.lstVideos = xrc.XRCCTRL(self.frm, 'lstVideos')
        self.lstSubs = xrc.XRCCTRL(self.frm, 'lstSubs')

        self.btnUndo = xrc.XRCCTRL(self.frm, 'btnUndo')
        self.btnRedo = xrc.XRCCTRL(self.frm, 'btnRedo')
        self.btnRenameRight = xrc.XRCCTRL(self.frm, 'btnRenameRight')
        self.btnRenameLeft = xrc.XRCCTRL(self.frm, 'btnRenameLeft')
        self.btnClear = xrc.XRCCTRL(self.frm, 'btnClear')

        # -- Event Binding -- 
        self.frm.Bind(wx.EVT_TOOL, self.OnVidAdd, id=xrc.XRCID('tlbItemVidAdd'))
        self.frm.Bind(wx.EVT_TOOL, self.OnVidRem, id=xrc.XRCID('tlbItemVidRem'))
        self.frm.Bind(wx.EVT_TOOL, self.OnVidUp, id=xrc.XRCID('tlbItemVidUp'))
        self.frm.Bind(wx.EVT_TOOL, self.OnVidDown, id=xrc.XRCID('tlbItemVidDown'))

        self.frm.Bind(wx.EVT_TOOL, self.OnSubAdd, id=xrc.XRCID('tlbItemSubAdd'))
        self.frm.Bind(wx.EVT_TOOL, self.OnSubRem, id=xrc.XRCID('tlbItemSubRem'))
        self.frm.Bind(wx.EVT_TOOL, self.OnSubUp, id=xrc.XRCID('tlbItemSubUp'))
        self.frm.Bind(wx.EVT_TOOL, self.OnSubDown, id=xrc.XRCID('tlbItemSubDown'))

        self.btnUndo.Bind(wx.EVT_BUTTON, self.OnUndo)
        self.btnRedo.Bind(wx.EVT_BUTTON, self.OnRedo)
        self.btnRenameRight.Bind(wx.EVT_BUTTON, self.OnRenameRight)
        self.btnRenameLeft.Bind(wx.EVT_BUTTON, self.OnRenameLeft)
        self.btnClear.Bind(wx.EVT_BUTTON, self.OnClear)

    def Show(self, show):
        """ Wrapper around the real frame show """
        self.frm.Show(show)

    def InsertUndo(self, undoObj, newAction = True):
        """ 
        Inserts an undo object in the undoStack.
        If this new undo was the result of a new action, clear the redo stack.
        Otherwise leave it be.
        """

        self.undoStack.append(undoObj)
        self.btnUndo.Enable()
        if newAction:
            self.btnRedo.Disable()
            self.redoStack = []

    def PopUndo(self):
        """ Removes the newest undo object from the undoStack """
        if len(self.undoStack) == 1:
            self.btnUndo.Disable()

        return self.undoStack.pop()

    def InsertRedo(self, redoObj):
        """ Inserts a redo object in the redoStack """
        self.redoStack.append(redoObj)
        self.btnRedo.Enable()

    def PopRedo(self):
        """ Removes the newest redo object from the redoStack """
        if len(self.redoStack) == 1:
            self.btnRedo.Disable()

        return self.redoStack.pop()

    def OnVidAdd(self, event):
        """ Adds user-selected videos to the video listbox """

        dlg = wx.FileDialog(self.frm, "Choose the video files", self.lastVidLocation, "", "Video files (*.avi;*.mov;*.mkv;*.mpg;*.mpeg)|*.avi;*.mov;*.mkv;*.mpg;*.mpeg|All files|*.*", wx.OPEN | wx.MULTIPLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.lastVidLocation = dlg.GetDirectory()
            undoObj = lst_populateWithFiles(self.lstVideos, dlg.GetPaths())
            self.InsertUndo(undoObj)

    def OnVidRem(self, event):
        """ Removes selected videos from the video listbox """
        
        undoObj = lst_removeSelection(self.lstVideos)
        self.InsertUndo(undoObj)

    def OnVidUp(self, event):
        """ Moves selected videos one place up the listbox """

        undoObj = lst_moveSelectionUp(self.lstVideos)
        self.InsertUndo(undoObj)

    def OnVidDown(self, event):
        """ Moves selected videos one place down the listbox """

        undoObj = lst_moveSelectionDown(self.lstVideos)
        self.InsertUndo(undoObj)

    def OnSubAdd(self, event):
        """ Adds user-selected subs to the subs listbox """

        dlg = wx.FileDialog(self.frm, "Choose the subtitle files", self.lastSubLocation, "", "Subtitle files (*.srt;*.sub)|*.srt;*.sub|All files|*.*", wx.OPEN | wx.MULTIPLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.lastSubLocation = dlg.GetDirectory()
            undoObj = lst_populateWithFiles(self.lstSubs, dlg.GetPaths())
            self.InsertUndo(undoObj)

    def OnSubRem(self, event):
        """ Removes selected subs from the subs listbox """

        undoObj = lst_removeSelection(self.lstSubs)
        self.InsertUndo(undoObj)

    def OnSubUp(self, event):
        """ Moves selected subs one place up the subs listbox """

        undoObj = lst_moveSelectionUp(self.lstSubs)
        self.InsertUndo(undoObj)

    def OnSubDown(self, event):
        """ Moves selected subs one place down the subs listbox """

        undoObj = lst_moveSelectionDown(self.lstSubs)
        self.InsertUndo(undoObj)

    def OnClear(self, event):
        """ Clears both listboxes """

        removedVideos = []
        removedSubs = []

        # Save all removed files to allow undo operation
        for index in range(self.lstVideos.GetCount()):
            rmItem = listItem(index, self.lstVideos.GetString(index), self.lstVideos.GetClientData(index))
            removedVideos.append(rmItem)

        for index in range(self.lstSubs.GetCount()):
            rmItem = listItem(index, self.lstSubs.GetString(index), self.lstSubs.GetClientData(index))
            removedSubs.append(rmItem)

        self.lstVideos.Clear()
        self.lstSubs.Clear()

        undoObj = undoClearFiles(self.lstVideos, removedVideos, self.lstSubs, removedSubs)

        self.InsertUndo(undoObj)

    def OnRenameRight(self, event):
        """ Renames the subtitles according to the video files """

        newFileList = []

        for index in range(self.lstVideos.GetCount()):
            newFileList.append(self.lstVideos.GetClientData(index))
        undoObj = renameFiles(newFileList, self.lstSubs)

        self.InsertUndo(undoObj)

    def OnRenameLeft(self, event):
        """ Renames the videos according to the subtitle files """

        newFileList = []

        for index in range(self.lstSubs.GetCount()):
            newFileList.append(self.lstSubs.GetClientData(index))
        undoObj = renameFiles(newFileList, self.lstVideos)

        self.InsertUndo(undoObj)

    def OnUndo(self, event):
        """ Undoes the last operation """

        undoObj = self.PopUndo()
        undoObj.undo()
        self.InsertRedo(undoObj)

    def OnRedo(self, event):
        """ Redoes the last undone operation """

        redoObj = self.PopRedo()
        redoObj.redo()
        self.InsertUndo(redoObj, False)

