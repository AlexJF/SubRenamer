#! /usr/bin/env python

"""
File: func.py
Author: Revolt
Date: 15-08-2010
--------------------------
Desc:
    This file contains all auxiliary functions and undo/redo objects
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

# ------------------ Misc. Functions ---------------------- #

def lst_populateWithFiles(listbox, files):
    """
    Given a pointer to a listbox and a list of files, inserts the files as
    items in the listbox so that the item string represents the filename
    and the item's client data represents the full path to the file.
    """

    for f in files:
        listbox.Append(os.path.basename(f), f)

    undoObj = undoAddFiles(listbox, files)
    return undoObj


class listItem:
    """ Container for items of a listbox """

    def __init__(self, index, name, data):
        self.index = index
        self.name = name
        self.data = data

def getListItem(listbox, index):
    """ 
    Given a listbox and an index, creates a listItem representing the
    listbox's item at that location
    """

    item = listItem(index, listbox.GetString(index), listbox.GetClientData(index))
    return item

def lst_removeSelection(listbox):
    """ Given a listbox, removes all selected items in it """

    removedItems = []
    for index in reversed(listbox.GetSelections()):
        removedItems.insert(0, getListItem(listbox, index))
        listbox.Delete(index)

    undoObj = undoRemoveFiles(listbox, removedItems)
    return undoObj

def lst_moveSelectionUp(listbox):
    """ Moves all selected items in a listbox up by 1 position """

    indexLimit = 0

    selectedIndexes = listbox.GetSelections()
    # A list that will contain all affected indexes
    resultingIndexes = []
    for index in selectedIndexes:
        # If current index allows an upward movement, perform it and
        # save index in the resultingIndexes list
        if index > indexLimit:
            itemString = listbox.GetString(index)
            itemData = listbox.GetClientData(index)
            listbox.Delete(index)
            listbox.Insert(itemString, index - 1, itemData)
            listbox.SetSelection(index - 1)
            # Old index (before movement) becomes the new upper
            # limit for movement
            indexLimit = index
            resultingIndexes.append(index - 1)
        # If not, current index is at the upper limit of movement
        # therefore no movement is made and next index becomes the
        # new upper limit
        else:
            indexLimit += 1

    undoObj = undoMoveSelectionUp(listbox, resultingIndexes)
    return undoObj

def lst_moveSelectionDown(listbox):
    """ Moves all selected items in a listbox down by 1 position """

    indexLimit = listbox.GetCount() - 1

    selectedIndexes = listbox.GetSelections()
    # A list that will contain all affected indexes
    resultingIndexes = []
    for index in reversed(selectedIndexes):
        # If current index allows a downward movement, perform it and
        # save index in the resultingIndexes list
        if index < indexLimit:
            itemString = listbox.GetString(index)
            itemData = listbox.GetClientData(index)
            listbox.Delete(index)
            listbox.Insert(itemString, index + 1, itemData)
            listbox.SetSelection(index + 1)
            # Old index (before movement) becomes the new lower
            # limit for movement
            indexLimit = index
            resultingIndexes.append(index + 1)
        # If not, current index is at the lower limit of movement
        # therefore no movement is made and previous index becomes the
        # new lower limit
        else:
            indexLimit -= 1
    undoObj = undoMoveSelectionDown(listbox, resultingIndexes)
    return undoObj

def lst_selectItems(listbox, indexes):
    """ Selects all items with the specified indexes in the specified listbox """
    selectedItemIndexes = listbox.GetSelections()

    # First we deselect all currently selected items
    for index in selectedItemIndexes:
        listbox.Deselect(index)

    # And then select the new ones
    for index in indexes:
        listbox.SetSelection(index)

def renameFiles(newFileList, destListBox):
    """ 
    Given a file list that represents the new full path of the files in the
    specified listbox, performs the rename operation for each one of these until
    either we run out of new file paths or we run out of target files in the list
    box.
    """

    # We need to save a list with the old paths to allow the undo operation
    oldFileList = []

    for index in range(min(len(newFileList), destListBox.GetCount())):
        # If a path is null it means there was some kind of error so
        # we jump to the next one. However, we have to add it to the
        # old file list so that the undo operation also skips this
        # file
        if newFileList[index] == "":
            oldFileList.append("")
            continue

        # Using the filename of the files in newFileList and the original extension of
        # the target file, we rename it
        oldFilePath = destListBox.GetClientData(index)
        newFilePath = os.path.join(os.path.dirname(oldFilePath), os.path.splitext(os.path.basename(newFileList[index]))[0] + os.path.splitext(oldFilePath)[1])
        try:
            print("Renaming '" + oldFilePath + "' to '" + newFilePath + "'")
            os.rename(oldFilePath, newFilePath)
        except Exception as error:
            print("Rename of '" + oldFilePath + "' to '" + newFilePath + "' failed: " + str(error))
            oldFileList.append("")
        else:
            # If successful we make the change in the interface aswell
            destListBox.SetString(index, os.path.basename(newFilePath))
            destListBox.SetClientData(index, newFilePath)
            oldFileList.append(oldFilePath)

    undoObj = undoRename(destListBox, oldFileList, newFileList)
    return undoObj


# ------------------------------ UNDO CLASSES ----------------------

class undoAddFiles:
    """ Allows the undo/redo of a AddFiles operation """

    def __init__(self, listbox, files):
        self.listbox = listbox
        self.filesAdded = files
    
    def undo(self):
        """ Removes all added files from the listbox """
        numberOfFilesAdded = len(self.filesAdded)
        numberOfFilesList = self.listbox.GetCount()

        for index in reversed(range(numberOfFilesList - numberOfFilesAdded, numberOfFilesList)):
            self.listbox.Delete(index)

    def redo(self):
        """ Readds all removed files to the listbox """
        lst_populateWithFiles(self.listbox, self.filesAdded)
        

class undoRemoveFiles:
    """ Allows the undo/redo of a RemoveFiles operation """

    def __init__(self, listbox, files):
        self.listbox = listbox
        self.filesRemoved = files

    def undo(self):
        """ Readds all removed files to the listbox and selects them """
        for f in self.filesRemoved:
            self.listbox.Insert(f.name, f.index, f.data)
            self.listbox.SetSelection(f.index)

    def redo(self):
        """ Removes all the readded files from the listbox """
        for f in reversed(self.filesRemoved):
            self.listbox.Delete(f.index)

class undoClearFiles:
    """ Allows the undo/redo of a ClearFiles operation """

    def __init__(self, lstVideos, removedVideos, lstSubs, removedSubs):
        self.lstVideos = lstVideos
        self.lstSubs = lstSubs
        self.removedVideos = removedVideos
        self.removedSubs = removedSubs

    def undo(self):
        """ Readds all the removed videos and subs to their listboxes """

        for video in self.removedVideos:
            self.lstVideos.Append(video.name, video.data)
        for sub in self.removedSubs:
            self.lstSubs.Append(sub.name, sub.data)

    def redo(self):
        """ Clears both video's and subs' listboxes """
        self.lstVideos.Clear()
        self.lstSubs.Clear()


class undoMoveSelectionUp:
    """ Allows the undo/redo of a MoveSelectionUp operation """

    def __init__(self, listbox, indexes):
        self.listbox = listbox
        self.indexes = indexes

    def undo(self):
        """ 
        Selects all the previously affected items and moves them down
        setting the selection to the new positions.
        """

        lst_selectItems(self.listbox, self.indexes)
        lst_moveSelectionDown(self.listbox)
        self.indexes = [x+1 for x in self.indexes]
        lst_selectItems(self.listbox, self.indexes)

    def redo(self):
        """
        Selects all the previously affected items and moves them up
        setting the selection to the new positions.
        """

        lst_selectItems(self.listbox, self.indexes)
        lst_moveSelectionUp(self.listbox)
        self.indexes = [x-1 for x in self.indexes]
        lst_selectItems(self.listbox, self.indexes)

class undoMoveSelectionDown:
    """ Allows the undo/redo of a MoveSelectionDown operation """

    def __init__(self, listbox, indexes):
        self.listbox = listbox
        self.indexes = indexes 

    def undo(self):
        """
        Selects all the previously affected items and moves them up
        setting the selection to the new positions.
        """
        lst_selectItems(self.listbox, self.indexes)
        lst_moveSelectionUp(self.listbox)
        self.indexes = [x-1 for x in self.indexes]
        lst_selectItems(self.listbox, self.indexes)

    def redo(self):
        """ 
        Selects all the previously affected items and moves them down
        setting the selection to the new positions.
        """
        lst_selectItems(self.listbox, self.indexes)
        lst_moveSelectionDown(self.listbox)
        self.indexes = [x+1 for x in self.indexes]
        lst_selectItems(self.listbox, self.indexes)

class undoRename:
    """ Allows the undo/redo of a Rename operation """

    def __init__(self, listbox, oldFileList, newFileList):
        self.listbox = listbox
        self.oldFileList = oldFileList
        self.newFileList = newFileList

    def undo(self):
        """ Renames all files to their old names """
        renameFiles(self.oldFileList, self.listbox)

    def redo(self):
        """ Renames all files to their new names """
        renameFiles(self.newFileList, self.listbox)


