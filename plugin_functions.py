# -*- coding: utf-8 -*-
"""
#############################################################################
##                                                                         ##
##  This file contains the specialized code to enable the functions of the ##
##  QGIS BlueM Interface Plugin    (Masterthesis Martin Großhaus Feb 2022) ##
##                                                                         ##
#############################################################################

   ____     _____   _____    _____
  / __ \   / ____| |_   _|  / ____|
 | |  | | | |  __    | |   | (___      ______
 | |  | | | | |_ |   | |    \___ \    |______|
 | |__| | | |__| |  _| |_   ____) |
  \___\_\  \_____| |_____| |_____/

  _____           _                    __
 |_   _|         | |                  / _|
   | |    _ __   | |_    ___   _ __  | |_    __ _    ___    ___
   | |   | '_ \  | __|  / _ \ | '__| |  _|  / _` |  / __|  / _ \
  _| |_  | | | | | |_  |  __/ | |    | |   | (_| | | (__  |  __/
 |_____| |_| |_|  \__|  \___| |_|    |_|    \__,_|  \___|  \___|

   __                        ____    _                  __  __
  / _|                      |  _ \  | |                |  \/  |
 | |_    ___    _ __        | |_) | | |  _   _    ___  | \  / |
 |  _|  / _ \  | '__|       |  _ <  | | | | | |  / _ \ | |\/| |
 | |   | (_) | | |          | |_) | | | | |_| | |  __/ | |  | |
 |_|    \___/  |_|          |____/  |_|  \__,_|  \___| |_|  |_|


#---------------------------------------------------------------------------#
|                                                                           |
|   Connect this file to the general code of the QGIS PluginBuilder by:     |
|                                                                           |
|   1) Copy this into the import section of "create_bluem_input_files.py":  |
|       from .plugin_functions import *                                     |
|                                                                           |
|   2) Replace the code IN the function "def run(self)" (same file) with:   |
|       prepare_plugin(self, self.first_start)                              |
|                                                                           |
|   3) In file "create_bluem_input_files_dialog.py":                        |
|       double the code for class & FORM_CLASS; "...Dialog" for "...Dialog2"|
|                                                                           |
#---------------------------------------------------------------------------#
/***************************************************************************
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 ***************************************************************************/
"""


#############################################################################


# IMPORTS

import csv  # to import csv data
import numpy as np  # for arrays
import os  # to verify file paths, open explorer etc.
import math  # for rounding up
import shutil  # to copy pdf files (manual)

# for date and time
from datetime import datetime

# used to change alignment of labels in warning
#  (only used in eval, therefore called "unused" by IDE)
from PyQt5.QtCore import Qt

from qgis import processing

# used for validation of text and setting type of new layer fields
from PyQt5.QtCore import QRegExp, QVariant
from PyQt5.QtGui import QRegExpValidator

# IDE (e.g. PyCharm) calls imports below unresolved, but QGIS knows them
from qgis.core import QgsMapLayer, QgsMapLayerProxyModel, QgsFeature, \
    QgsSettings, QgsField, QgsVectorLayer, \
    QgsEditorWidgetSetup, QgsProject, edit

# import dialog windows
from .create_bluem_input_files_dialog import CreateBlueMInputFilesDialog
from .create_bluem_input_files_dialog import CreateBlueMInputFilesDialog2


#############################################################################


# DEFINE GLOBAL VARIABLES

# globals for array and its indices
global inputfiles_overview
global index_name_short
global index_name_long
global index_comment_for_dlg2
global index_attr_count
global index_example
global index_headlines
global index_add_lines_1
global index_add_lines_2
global index_add_lines_3
global index_add_lines_4
global index_add_lines_5
global index_add_lines_6
global index_add_lines_7
global index_last_line
global index_pattern

# global lists and dictionaries
global list_inputfile_types
global list_number_attr_file_max
global list_inputfile_types_standard
global list_filetypes_not_standard
global dict_indices_file_attr_names
global dict_indices_file_attr_types
global list_filetypes_for_export

# for current filetype in second window
global current_filetype_second_window
global current_list_file_attr_names
global current_list_number_attr_file
global current_number_attr_layer
global current_number_attr_file

# other globals
global self
global max_number_attr_file
global list_valid_chars_not_space
global val_rep_char


#############################################################################
#   GENERAL FUNCTIONS  -  Allgemeine Funktionen (Kapitel 5.1)               #
#############################################################################


# This function prepares the first window and general plugin functions
def prepare_plugin(add_self, first_start):

    # set self for the following functions as a global, so that it does not
    # need to be passed on all the time (easier for eval()-functions)
    global self
    self = add_self

    # define dialog windows
    self.dlg = CreateBlueMInputFilesDialog()
    self.dlg2 = CreateBlueMInputFilesDialog2()

    # show the dialog
    self.dlg.show()

    # set info about plugin version in both dialog windows
    version_info = "version 1.2"
    self.dlg.lb_version_info.setText(version_info)
    self.dlg2.lb_version_info.setText(version_info)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # EXECUTION

    # import information about BlueM input file types from csv into array
    with open(os.path.join(os.path.dirname(__file__), "inputfiles_overview.csv"), 'r', encoding="ANSI") as file:
        inputfiles_overview_data = list(csv.reader(file, delimiter=";"))

    # put all information into array
    global inputfiles_overview
    inputfiles_overview = np.array(inputfiles_overview_data)

    # check for correct indices of information in the array
    #  in case the columns got mixed up
    global index_name_short
    index_name_short = np.where(inputfiles_overview == "name_short")[1]
    global index_name_long
    index_name_long = np.where(inputfiles_overview == "name_long")[1]

    global index_comment_for_dlg2
    index_comment_for_dlg2 = \
        np.where(inputfiles_overview == "comment_for_dlg2")[1]
    global index_attr_count
    index_attr_count = np.where(inputfiles_overview == "attr_count")[1]
    global index_example
    index_example = np.where(inputfiles_overview == "example")[1]

    global index_headlines
    index_headlines = np.where(inputfiles_overview == "headlines")[1]
    global index_add_lines_1
    index_add_lines_1 = np.where(inputfiles_overview == "add_lines_1")[1]
    global index_add_lines_2
    index_add_lines_2 = np.where(inputfiles_overview == "add_lines_2")[1]
    global index_add_lines_3
    index_add_lines_3 = np.where(inputfiles_overview == "add_lines_3")[1]
    global index_add_lines_4
    index_add_lines_4 = np.where(inputfiles_overview == "add_lines_4")[1]
    global index_add_lines_5
    index_add_lines_5 = np.where(inputfiles_overview == "add_lines_5")[1]
    global index_add_lines_6
    index_add_lines_6 = np.where(inputfiles_overview == "add_lines_6")[1]
    global index_add_lines_7
    index_add_lines_7 = np.where(inputfiles_overview == "add_lines_7")[1]
    global index_last_line
    index_last_line = np.where(inputfiles_overview == "last_line")[1]

    global index_pattern
    index_pattern = np.where(inputfiles_overview == "pattern")[1]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # get a global list of input file types
    global list_inputfile_types
    list_inputfile_types = []
    for row in inputfiles_overview:
        # only in this column
        list_inputfile_types.append(row[int(index_name_short)])
    # remove header
    list_inputfile_types.remove("name_short")
    # remove empty entry if necessary
    while '' in list_inputfile_types:
        list_inputfile_types.remove('')

    # set a maximum number of attributes for all filetypes and make it a list
    global max_number_attr_file
    max_number_attr_file = 80  # limited by number of frames in current GUI
    global list_number_attr_file_max
    list_number_attr_file_max = []
    for i in range(1, max_number_attr_file + 1):
        if len(str(i)) == 1:
            i = "0" + str(i)
        list_number_attr_file_max.append(str(i))

    # define a global dictionary of the indices of all file attributes
    global dict_indices_file_attr_names
    dict_indices_file_attr_names = {}
    # fill a global dictionary of the indices of all file attributes
    for i in list_number_attr_file_max:
        dict_indices_file_attr_names[str("index_attr_" + i)] = \
            np.where(inputfiles_overview == str("attr_" + i))[1]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # create global list for every filetype with its attribute names
    for i in list_inputfile_types:  # go through every filetype
        current_list = []  # make temporary variable for filetype
        # go through all attribute numbers of current filetype
        for j in range(1, int(inputfiles_overview
                              # raise by 1 because its from list (no header)
                              [int(list_inputfile_types.index(i) + 1)]
                              [int(index_attr_count)])
                              # raise by 1 because of how "range" works
                              + 1):
            if len(str(j)) == 1:  # give j a leading zero if necessary
                j = "0" + str(j)
            current_list.append(str(inputfiles_overview
                                    # raise by 1 because its from list
                                    # (with no header)
                                    [int(list_inputfile_types.index(i) + 1)]
                                    [int(dict_indices_file_attr_names
                                         ["index_attr_" + str(j)])]))

        # create global list for every filetype from temporary variable
        globals()[i.lower() + "_file_attr_list"] = current_list

    # get a dictionary of the indices of all file attributes types
    global dict_indices_file_attr_types
    dict_indices_file_attr_types = {}
    for i in list_number_attr_file_max:
        dict_indices_file_attr_types[str("index_attr_" + i + "_type")] = \
            np.where(inputfiles_overview == str("attr_" + i + "_type"))[1]

    # create global dictionary for every filetype with its attribute types
    for i in list_inputfile_types:  # go through every filetype
        current_dict = {}  # make temporary variable for filetype
        # go through all attribute numbers of current filetype
        for j in range(1, int(inputfiles_overview
                              # raise by 1 because its from list (no header)
                              [int(list_inputfile_types.index(i) + 1)]
                              [int(index_attr_count)]
                              # raise by 1 because of how "range" works
                              ) + 1):
            if len(str(j)) == 1:  # give j a leading zero if necessary
                j = "0" + str(j)
            current_dict["attr_" + str(j) + "_type"] = \
                str(inputfiles_overview
                    # raise by 1 because its from list (no header)
                    [int(list_inputfile_types.index(i) + 1)]
                    [int(dict_indices_file_attr_types
                         ["index_attr_" + str(j) + "_type"])])

        # create global dictionary for every filetype from temporary variable
        globals()[i.lower() + "_file_attr_type_dict"] = current_dict

    # Control input validation of line edit in second tab of first window.
    # Only allow: standard letters (no "ä" etc), numbers and "_"
    validator = QRegExpValidator(QRegExp("[A-Z-a-z-0-9_]+"))
    self.dlg.le_project_name.setValidator(validator)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # LAYER ADAPTION (in second tab of first dialog)

    # sort layer-combobox (remove unwanted layer types)
    suitable_types_layer_adaption = (QgsMapLayerProxyModel.VectorLayer
                                     or QgsMapLayerProxyModel.NoGeometry)
    self.dlg.cb_layer_adaption_selection \
        .setFilters(suitable_types_layer_adaption)

    # fill filetype selection combobox with empty item and all filetypes
    self.dlg.cb_filetype_combobox.addItem(str(""))
    self.dlg.cb_filetype_combobox.addItems(list_inputfile_types)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # GENERAL HOUSEKEEPING

    # create empty list of files for export
    global list_filetypes_for_export
    list_filetypes_for_export = []

    # set a global list of valid characters, that are not a whitespace (" ")
    global list_valid_chars_not_space
    list_valid_chars_not_space = \
        ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f',
         'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K', 'k', 'L', 'l',
         'M', 'm', 'N', 'n', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r',
         'S', 's', 'T', 't', 'U', 'u', 'V', 'v', 'W', 'w', 'X', 'x',
         'Y', 'y', 'Z', 'z',
         'Ä', 'ä', 'Ö', 'ö', 'Ü', 'ü', 'ß', '_', '!', '¿', '?', '&',
         '%', '$', '€', '#', '+', '-', '*', '/', '~', '§',
         '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    # a list of filetypes that are currently not working
    list_filetypes_not_working = []  # non, juhu! :-)

    # disable functions for filetypes that are not working
    for i in list_inputfile_types:
        if i in list_filetypes_not_working:
            # disable this combobox and set a warning
            eval("self.dlg.cb_xxx_layerselection.setEnabled(False)"
                 .replace("xxx", i.lower()))
            eval("self.dlg.lb_xxx_eng.setText('NOT WORKING')"
                 .replace("xxx", i.lower()))
            eval("self.dlg.lb_xxx_eng.setAlignment(Qt.AlignRight)"
                 .replace("xxx", i.lower()))

    # get a list of "not standard" filetypes
    global list_filetypes_not_standard
    list_filetypes_not_standard = [
        "TAL"  # has its own export function
    ]

    # get a global list of "standard" filetypes by removing non standard
    #  filetypes from list of all filetypes
    global list_inputfile_types_standard
    list_inputfile_types_standard = list_inputfile_types.copy()
    for i in list_filetypes_not_standard:
        list_inputfile_types_standard.remove(i.upper())

    # check the value replacement character
    check_val_rep_char()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # GUI CONNECTIONS

    # establish GUI connections only once due to "first_start"-variable
    if first_start is True:
        first_start = False  # set first_start to FALSE for next round

        general_gui_functions()
        set_tab_order()


#############################################################################


# Creates a second window and fills it with the necessary information
#  for the selected input file type
def open_second_window(filetype):

    # differentiate between a and an depending on first letter
    #  of the file type name (Vowels must be in a tuple)
    vowels = ("A", "E", "I", "O", "U", "a", "e", "i", "o", "u")
    if filetype.startswith(vowels):
        a_an = "an"
    else:
        a_an = "a"

    # get filetype index from function
    filetype_index = get_filetype_index(filetype)

    # get the example for the filetype from the array of csv data
    self.dlg2.lb_example.setText(
        str(inputfiles_overview[int(filetype_index)][int(index_example)]))

    # set tool tip for example
    self.dlg2.lb_example.setToolTip(
        "example of " + a_an + " " + filetype.upper() + "-file")

    # get the selected layer
    selected_layer = \
        eval("self.dlg.cb_xxx_layerselection.currentLayer()"
             .replace("xxx", str(filetype.lower())))

    # get the name of the selected layer
    selected_layer_name = \
        eval("self.dlg.cb_xxx_layerselection.currentText()"
             .replace("xxx", str(filetype.lower())))

    # get the long name of the filetype
    name_long = str(inputfiles_overview[int(filetype_index)]
                                       [int(index_name_long)])

    # get the comment for the filetype and format it
    comment = str(inputfiles_overview[int(filetype_index)]
                                     [int(index_comment_for_dlg2)])
    comment = comment.replace(r"\n", "\n")

    # get the number of attributes for the filetype
    number_attr_filetype = int(inputfiles_overview[int(filetype_index)]
                                                  [int(index_attr_count)])

    # get list of attributes of the layer
    layer_attr = []
    for field in selected_layer.fields():
        layer_attr.append(field.name())

    # get the number of attributes of the layer
    number_attr_layer = len(layer_attr)

    # create list of numbers of attributes for this filetype
    list_number_attr_file = []
    for i in range(1, number_attr_filetype+1):
        # give i a leading zero if necessary
        if len(str(i)) == 1:
            i = "0"+str(i)
        list_number_attr_file.append(str(i))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # ATTRIBUTE FRAMES

    # make all attribute frames visible for the moment
    for i in list_number_attr_file_max:
        eval("self.dlg2.frame_attr_XX.show()".replace("XX", i))

    # get max number of row frames (5 attributes per row frame; round UP)
    max_number_row_frames = math.ceil(max_number_attr_file / 5)
    # make all attribute row frames invisible for the moment
    for i in range(1, max_number_row_frames + 1):
        eval("self.dlg2.frame_row_XX.hide()".replace("XX", str(i)))

    # make a list of all superfluous attribute numbers
    superfluous_attr_numbers = []
    for i in list_number_attr_file_max:
        if i not in list_number_attr_file:
            superfluous_attr_numbers.append(i)

    # hide all superfluous attribute frames
    for i in superfluous_attr_numbers:
        eval("self.dlg2.frame_attr_XX.hide()".replace("XX", i))

    # get needed number of row frames (5 attributes per row frame; round UP)
    needed_number_row_frames = math.ceil(len(list_number_attr_file) / 5)
    # make needed attribute row frames visible
    for i in range(1, needed_number_row_frames + 1):
        eval("self.dlg2.frame_row_XX.show()".replace("XX", str(i)))

    # clear all comboboxes before filling them new when a new version
    #  of the second window is opened
    for i in list_number_attr_file_max:
        # iterates through a list of all comboboxes (max)
        eval("self.dlg2.cb_attr_XX.clear()".replace("XX", i))

    # list of file attribute names for current filetype
    current_file_attr_list = eval("xxx_file_attr_list"
                                  .replace("xxx", filetype.lower()))

    # fill the labels above the comboboxes with the file attribute names
    for (i, j) in zip(list_number_attr_file, current_file_attr_list):
        eval("self.dlg2.lb_attr_XX.setText(j)".replace("XX", i))

    # fill comboboxes with layer attributes
    for i in list_number_attr_file:
        # empty item at the top
        eval("self.dlg2.cb_attr_XX.addItem(str(""))".replace("XX", i))
        # fill from list
        eval("self.dlg2.cb_attr_XX.addItems(layer_attr)".replace("XX", i))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # SET TEXTS

    # set header in second window for the selected filetype
    self.dlg2.lb_header.setText(
        "Create " + a_an + " " + filetype.upper() + "-file manually")

    # set long name of filetype in second window
    self.dlg2.lb_name_long.setText(
        'aka "' + name_long + '" ')

    # set info_1 in second window for the selected filetype
    self.dlg2.lb_info_1.setText(
        "You can create a BlueM " + filetype.upper() +
        "-file that looks like\nthe example on the left with the "
        "data from your\n" + '"' + selected_layer_name + '"' + "-layer.")

    # set info_2 in second window for the selected filetype
    self.dlg2.lb_info_2.setText(
        "Just match the attributes you want (up to "
        + str(number_attr_filetype) + ")\n for the "
        + filetype.upper() + "-file with one of the "
        + str(number_attr_layer)
        + " field names\nof the layer (in the dropdown menus).")

    # set title for comment box
    self.dlg2.gb_comment.setTitle(
        " Comment for " + filetype.upper() + "-file:")

    # set comment
    self.dlg2.lb_comment.setText(comment)

    # hide comment box if comment is empty, and show if not empty
    if comment == "":
        self.dlg2.gb_comment.hide()
    else:
        self.dlg2.gb_comment.show()

    # handle button for "correct field names"
    self.dlg2.pb_correct_field_names.hide()
    # only show button if necessary (field name 1 = "Field1")
    if self.dlg2.cb_attr_01.itemText(1) == "Field1":
        self.dlg2.pb_correct_field_names.show()

    # check if a previous selection exists and set if available
    previous_selection(filetype)
      
    # open second window
    self.dlg2.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # set global variables accordingly for use in other functions
    #  (e.g. correcting field names of faulty layer, etc.)

    # set current filetype of second window as global
    global current_filetype_second_window
    current_filetype_second_window = filetype

    # set current list of attribute numbers of file as global
    global current_list_number_attr_file
    current_list_number_attr_file = list_number_attr_file

    # set current list of attribute names of file as global
    global current_list_file_attr_names
    current_list_file_attr_names = current_file_attr_list

    # set number of layer attributes of second window as global
    global current_number_attr_layer
    current_number_attr_layer = number_attr_layer

    # set number of file attributes of second window as global
    global current_number_attr_file
    current_number_attr_file = number_attr_filetype


#############################################################################


# Function for "Cancel"-button in second window
def reject_second_window():
    # get filetype from open_second_window via global variable
    filetype = current_filetype_second_window

    # enables the layerselection, because "manually" is not checked
    eval("self.dlg.cb_xxx_layerselection.setEnabled(True)"
         .replace("xxx", str(filetype.lower())))


#############################################################################


# Function for "OK"-button in second window
def execute_second_window():

    # get filetype from open_second_window via global variable
    filetype = current_filetype_second_window

    # checks the "manually"-button, which had opened the second window
    eval("self.dlg.pb_xxx_manually.setChecked(True)"
         .replace("xxx", str(filetype.lower())))

    # put filename in list for export
    list_filetypes_for_export.append(filetype.upper())

    # disables the layerselection for this filetype so that it
    #  can not be changed unless the buttons are unchecked
    eval("self.dlg.cb_xxx_layerselection.setEnabled(False)"
         .replace("xxx", str(filetype.lower())))

    # saves the selections from all attributes of the second window
    #  in a file specific global dictionary
    exec("global xxx_attr_dict; xxx_attr_dict = {}"
         .replace("xxx", filetype.lower()))
    for xx in current_list_number_attr_file:
        eval("xxx_attr_dict"
             .replace("xxx", filetype.lower()))[str("attr_"+xx)] = \
            eval("self.dlg2.cb_attr_"+xx).currentText()


#############################################################################
#   SORTING FUNCTIONS  -  Sortier-Funktionen (Kapitel 5.2)                  #
#############################################################################


# Create a dictionary for this file type and match the layer fields to the
#  required file attributes by their names
def create_dict_by_name(filetype):

    # get filetype index from function
    filetype_index = get_filetype_index(filetype)

    # get the number of attributes for the filetype
    number_attr_filetype = \
        int(inputfiles_overview[int(filetype_index)]
                               [int(index_attr_count)])

    # create list of numbers of attributes for this filetype
    list_number_attr_file = []
    for i in range(1, number_attr_filetype + 1):
        if len(str(i)) == 1:  # give i a leading zero if necessary
            i = "0" + str(i)
        list_number_attr_file.append(str(i))

    # get list of file attribute names from global variable
    list_names_attr_file = eval(filetype.lower()+"_file_attr_list")

    # get the selected layer
    selected_layer = \
        eval("self.dlg.cb_xxx_layerselection.currentLayer()"
             .replace("xxx", str(filetype.lower())))

    # get list of layer attribute names
    list_names_attr_layer = []
    for field in selected_layer.fields():
        list_names_attr_layer.append(field.name())

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # CREATE NEW DICT

    # create current dictionary and fill it with all the necessary
    #  keys (with empty values) for this filetype
    current_dict = {}
    for number in list_number_attr_file:
        current_dict["attr_" + number] = ""

    # go through all attribute names of layer
    for name_attr_layer in list_names_attr_layer:
        # check if these names are used in the file
        # (make everything temporary upper case, to ignore case)
        if name_attr_layer.upper() in \
                [x.upper() for x in list_names_attr_file]:

            # get the index of that name in file attribute list
            # (make everything temporary upper case, to ignore case)
            index_attr_in_file = \
                [x.upper() for x in list_names_attr_file].index(
                    name_attr_layer.upper())

            # raise by one because the index comes from
            #  a list (starts at 0) but we start at "01"
            index_attr_in_file += 1

            # make it a string and add a leading zero if necessary
            index_attr_in_file = str(index_attr_in_file)
            if len(index_attr_in_file) == 1:
                index_attr_in_file = "0" + index_attr_in_file

            # write name of the layer attribute with the correct key in the
            #  current dictionary
            current_dict["attr_" + index_attr_in_file] = str(name_attr_layer)

    # transfer data from current dict into specific global dict
    globals()[filetype.lower() + "_attr_dict"] = current_dict


#############################################################################


# fill second window with previous attribute selection if available
def previous_selection(filetype):

    # check if a dict with a previous attribute selections is available
    if str(filetype.lower() + "_attr_dict") in globals():
        previous_dict = eval(filetype.lower() + "_attr_dict")

        # for every entry in the previous dictionary
        for attr_xx in previous_dict.keys():

            # get index of previously selected layer attribute
            prev_attr_index = eval("self.dlg2.cb_attr_xx.findText('yy')"
                                   .replace("attr_xx", attr_xx)
                                   .replace("yy", previous_dict[attr_xx]))

            # set combobox to previous selection
            eval("self.dlg2.cb_attr_xx.setCurrentIndex(yy)"
                 .replace("attr_xx", attr_xx)
                 .replace("yy", str(prev_attr_index)))


#############################################################################


# Matches attributes in second window by name if possible
def match_attributes_by_name_if_possible():

    # for all attribute numbers and names of current file in second window
    for xx, yy in zip(current_list_number_attr_file,
                      current_list_file_attr_names):
        # try to find matching attribute name in every combobox
        index = eval("self.dlg2.cb_attr_xx.findText('yy', "
                     "Qt.MatchFixedString)"
                     .replace("xx", xx).replace("yy", yy))
        # if attribute name is not in combobox -> index is -1, therefore:
        if index != -1:
            # set index of combobox to the index of the found attribute name
            eval("self.dlg2.cb_attr_xx.setCurrentIndex(index)"
                 .replace("xx", xx))


#############################################################################


# Matches attributes in order of fields of layer
def match_attributes_by_order():

    # for all fields in layer for filetype in second window
    for xx in range(1, current_number_attr_layer + 1):
        # copy number, because one needs leading zero, the other does not
        xx = str(xx)
        yy = xx
        # give leading zero if necessary
        if len(str(xx)) < 2:
            yy = str("0" + yy)
        # set index of combobox to the number of layer attribute name
        eval("self.dlg2.cb_attr_yy.setCurrentIndex(int(xx))"
             .replace("yy", yy).replace("xx", xx))


#############################################################################


# Clears all attribute matches in second window
def clear_all_matches():

    # for all attribute numbers of current file in second window
    for xx in current_list_number_attr_file:
        # set index of combobox to 0 i.e. first value (empty)
        eval("self.dlg2.cb_attr_xx.setCurrentIndex(0)".replace("xx", xx))


#############################################################################
#   GENERATE & EXPORT BLUEM-FILES                                           #
#       Erzeugen & Export von BlueM-Dateien (Kapitel 5.3)                   #
#############################################################################


# When the user clicks on "export"
def export_clicked():

    # check how many files need to be exported
    number_files_to_export = len(list_filetypes_for_export)

    if number_files_to_export == 0:

        # show message in message bar
        self.iface.messageBar().pushMessage(
            "NO FILES FOR EXPORT SELECTED",
            "Please check the buttons to export BlueM files.",
            duration=10)

    else:

        # show message in message bar
        self.iface.messageBar().pushMessage(
            "Exporting BlueM files: " + str(number_files_to_export) +
            " - Types: " + str(list_filetypes_for_export))

        # open explorer window if checked in settings (GUI)
        open_explorer_window()

        # investigate which buttons are checked
        #  and call corresponding functions
        for i in list_inputfile_types_standard:
            if eval("self.dlg.pb_xxx_manually.isChecked()"
                    .replace("xxx", i.lower())):
                export_file(i)
            if eval("self.dlg.pb_xxx_byname.isChecked()"
                    .replace("xxx", i.lower())):
                export_file(i)

        # check if TAL has to be exported
        if self.dlg.pb_tal_manually.isChecked():
            export_tal_file()
        if self.dlg.pb_tal_byname.isChecked():
            export_tal_file()

        # export file with information about all file exports if
        #  checked in GUI
        if self.dlg.cb_separate_file.checkState():
            export_file_export_information()

        # close plugin dialog after export
        #  only if checked in settings (GUI, dlg, tab2)
        if self.dlg.cb_close_after_export.isChecked():
            self.dlg.accept()


#############################################################################


# Export a file for a standard filetype
def export_file(filetype):

    # get info about this file type from csv i.e. array via function
    (current_layer, list_number_attr_file,
     pattern, headlines, last_line,
     add_lines_1, add_lines_2, add_lines_3,
     add_lines_4, add_lines_5, add_lines_6,
     add_lines_7) = \
        get_type_info(filetype)

    # get dictionaries for current file type
    current_dict_name = eval(filetype.lower() + "_attr_dict")
    current_dict_type = eval(filetype.lower() + "_file_attr_type_dict")

    # get information about dictionaries
    number_of_attr_in_file = len(current_dict_name)
    number_of_matches = 0
    list_attrs_not_matched = []
    for attr_nr in current_dict_name.keys():
        if current_dict_name[attr_nr] == "":
            list_attrs_not_matched.append(attr_nr)
        else:
            number_of_matches += 1

    # get file name from function
    filename, time_of_export = construct_filename(filetype)

    # create empty list for the value warnings of this file
    current_file_value_warnings_list = []

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # WRITE THE FILE

    # "write" file with "ANSI" encoding
    with open(filename, 'w', encoding='ANSI') as file:

        # write headlines in file
        file.write(headlines)

        feature_counter = 0
        # go through every feature of layer
        for feature in current_layer.getFeatures():
            feature_counter += 1

            # create empty list for current row
            current_row = []
            # go through every attribute of filetype
            for xx in list_number_attr_file:

                # get the required attribute data type
                req_type = current_dict_type["attr_" + xx + "_type"]
                # replace possible \xa0 with real spaces
                req_type = req_type.replace(r'\xa0', " ")
                # get required length of output
                req_length = len(str(req_type))

                # check if there is an entry for this attribute
                if current_dict_name["attr_"+xx] == "":
                    # if no match in feature: fill with enough " "
                    current_row.append(str(" " * req_length))
                else:
                    # handle the corresponding value

                    # get the feature value for attribute from layer
                    value = feature[current_dict_name["attr_" + xx]]

                    # check the value in another function
                    #  and get potential warning
                    value, value_warning = \
                        check_value(value, req_length, req_type)

                    # put value as string in list for current feature
                    current_row.append(str(value))

                    # if there is a value warning
                    if value_warning != "":
                        # add column and row to value warning
                        value_warning = str(xx + ";" +
                                            str(feature_counter)
                                            + ";" + value_warning)

                        # add the warning to the list for this file
                        current_file_value_warnings_list\
                            .append(value_warning)

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # IMPLEMENT FILETYPE SPECIFIC FORMATS

            if filetype == "FKT":
                # FKT has 3 types of lines to make the table
                #  easier to read

                # line above new "Bez"
                if current_row[0][0] != " ":
                    file.write(add_lines_1 + "\n")

                # line above new "Funktion"
                if current_row[0][0] == " " \
                        and current_row[1][0] != " ":
                    file.write(add_lines_2 + "\n")

                # line above new "Fkt_Nam"
                if current_row[0][0] == " " \
                        and current_row[1][0] == " " \
                        and current_row[2][0] != " ":
                    file.write(add_lines_3 + "\n")

            if filetype == "KTR":
                # KTR is divided into two tables

                if current_row[0][0] == "K":
                    # if "Bez" starts with "K" like in
                    #  KGRP (Kontrollgruppen), insert new
                    #  table header for it only once

                    try:
                        if kgrp_count in locals():
                            pass
                    # KGRP_count should not exist at first and even the
                    #  check provokes an error, therefore:
                    except UnboundLocalError:
                        kgrp_count = 1
                        # Create KGRP_count variable, so next is "pass".
                        # Could have been solved differently (define
                        # variable earlier), but in this way all KTR-
                        #  specific code is contained here.
                        file.write(add_lines_1 + "\n")
                        # Hopefully the table was sorted by the user,
                        #  so that there is only KGRP in the second table.
                        # The table should not be sorted by python, because
                        #  that would cause more trouble than its worth due
                        #  to the empty values in the first column.

            if filetype == "ALL" and feature_counter > 1:
                pass
                # only one feature / "row" is needed for an ALL-file
            else:
                # precede with writing row in file

                # check if current row contains field names
                #  (maybe check every attribute, could be valid though)
                # only if first attribute has a match
                if current_dict_name["attr_01"] != "":
                    # is original first entry of first row identical
                    #  to first field name?
                    if current_dict_name["attr_01"] == \
                       feature[current_dict_name["attr_01"]]:
                        # do not write row in file (it is field names)
                        # reduce feature counter
                        feature_counter -= 1
                    else:
                        # write list for current feature with
                        #  file-specific pattern in file
                        file.write(pattern.format(*current_row))
                else:
                    # write list for current feature with
                    #  file-specific pattern in file
                    file.write(pattern.format(*current_row))

        # write last line(s) of the table into the file
        file.write(last_line)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # GET THE EXPORT INFORMATION INTO THE FILE

        # construct the export information for this file
        current_file_export_info = \
            str("* This " + filetype.upper() + "-file was created by "
                "the 'QGIS BlueM Interface Plugin'\n"
                "*   with data from the '" + current_layer.name() +
                "'-layer\n*   on the " + time_of_export + ".\n*\n" +
                "* Of the " + str(number_of_attr_in_file) +
                " file attributes, " + str(number_of_matches) +
                " found a matching field name in the layer.\n")

        # add another line to element-files
        if filetype in ["BEK", "EIN", "EZG", "FKA", "HYA",
                        "RUE", "TAL", "TRS", "URB", "VER"]:
            current_file_export_info = \
                str(current_file_export_info +
                    "* (including the not printed 'Output_to')\n")

        # if some attributes did not find a match
        if number_of_attr_in_file > number_of_matches:
            current_file_export_info = \
                str(current_file_export_info +
                    "* These attributes found no match: "
                    + str(list_attrs_not_matched) + "\n")

        # if there are value warnings
        nr_warnings = len(current_file_value_warnings_list)

        if nr_warnings == 0:
            current_file_export_info = \
                str(current_file_export_info + "*\n* " +
                    "No values had to be changed or were not "
                    "suitable at all.\n*\n")

        if nr_warnings > 0:
            if nr_warnings == 1:
                current_file_export_info = \
                    str(current_file_export_info + "*\n* " +
                        "1 value had to be changed or was not "
                        "suitable at all.\n")
            if nr_warnings > 1:
                current_file_export_info = \
                    str(current_file_export_info + "*\n* " +
                        str(len(current_file_value_warnings_list)) +
                        " values had to be changed or were not "
                        "suitable at all:\n*\n")

            # write value warnings in file
            for warnings in current_file_value_warnings_list:
                warnings = warnings.split(";")
                current_file_export_info = \
                    str(current_file_export_info +
                        "*  -> For attribute number "
                        + str(warnings[0]) + " of feature "
                        + str(warnings[1]).zfill(3) + ":  "
                        + str(warnings[2]) + "\n")

        # write information into file if checked in GUI
        if self.dlg.cb_bottom_every_file.checkState():
            file.write("\n*\n*\n*\n*\n*\n*\n"
                       + current_file_export_info)

    # set current file export info as global for filetype
    globals()[filetype.lower() + "_file_export_info"] = \
        current_file_export_info


#############################################################################


# Check if value is possible in output data type and reformat if necessary
def check_value(value, req_length, req_type):

    # create empty "value warning" for changes
    value_warning = ""

    # get data type of attribute output
    if str(req_type)[0] == "s":
        attr_type = "string"
    elif str(req_type)[0] == "i":
        attr_type = "integer"
    elif str(req_type)[0] == "f":
        attr_type = "float"
    elif str(req_type)[0] == "Y":
        attr_type = "Y"  # yes(J) or no(N)
    elif str(req_type) == "TT.MM":
        attr_type = "TT.MM"
    elif str(req_type) == "hh:mm":
        attr_type = "hh:mm"
    elif str(req_type) == "TT.MM hh:mm":
        attr_type = "TT.MM hh:mm"
    elif str(req_type) == "TT.MM.JJJJ hh:mm":
        attr_type = "TT.MM.JJJJ hh:mm"
    else:
        attr_type = ""

    # "try" if conversion is possible
    try:
        # handle string
        if attr_type == "string":
            value = str(value)
            # crop both ends of string
            value = value.lstrip("['").rstrip("']")
            value = value.lstrip(" ").rstrip(" ")
            value = value.lstrip("(").rstrip(")")
            # remove "NULL" and "None"
            value = value.replace("NULL", "    ")
            value = value.replace("None", "    ")
            # cut value to appropriate length if necessary
            if len(value) > req_length:
                value = value[0:req_length]
                value_warning = "    string was shortened"
            # fill up with " " if string too short
            while len(value) < req_length:
                value = value + " "

        # in value replace "," with "." for numbers
        if attr_type == "integer" or attr_type == "float":
            value = str(value).replace(",", ".")

        # handle integer
        if attr_type == "integer":
            # accept floats and make them integer
            value = float(value)
            # need to round, because int() just cuts off
            value_r = round(value, 0)
            value_r = int(value_r)
            # check if float was rounded to integer
            if value != value_r:
                value_warning = "    float was rounded to work as integer"

            value = str(value_r)
            # check if number is too big
            if len(value) > req_length:
                value = str(val_rep_char * req_length)
                value_warning = "!!! integer was to long to fit"
            # fill up with " " if integer is too small
            while len(value) < req_length:
                value = " " + value

        # handle float
        if attr_type == "float":
            value = float(value)
            # check length before "."
            len_int = len(str(int(value)))
            # if integer part of float to big: cut it out
            if len_int > req_length:
                value = str(val_rep_char * req_length)
                value_warning = \
                    "!!! integer part of float was to long to fit"
            # if "." would be last character
            elif len_int == (req_length - 1):
                value = str(" " + str(int(round(value, 0))))
                value_warning = "    float was changed to integer"
            # if value has to many characters after "."
            elif len(str(value)) > req_length:
                value_warning = "    float rounded to fit"
                # get max character count after point
                len_after_point = req_length - 1 - len_int
                # round appropriately
                value = round(value, len_after_point)
                value = str(value)
                # convert to integer if last char ".0"
                if value[-2:] == ".0":
                    value = value[:-2]

            value = str(value)
            # fill up with " " if float is too small
            while len(value) < req_length:
                value = " " + value

        # handle YES or NO output
        if attr_type == "Y":
            value = str(value)
            # check for different versions
            yes_list = ["J", "j", "Ja", "JA", "ja",
                        "Y", "y", "Yes", "YES", "Yes",
                        "a", "oui", "etiam", "sic", "да"]
            no_list = ["N", "n", "Nein", "NEIN", "nein",
                       "No", "NO", "no",
                       "r", "non", "нет"]
            if value in yes_list:
                value = "J"
            elif value in no_list:
                value = "N"
            else:
                value = str(val_rep_char * req_length)
                # does not accept " " as replacement... therefore:
                #  fill up with " " if value is too short
                while len(value) < req_length:
                    value = " " + value
                value_warning = "!!! Y/N value was not recognized"

        # handle date and time outputs
        datetime_list = ["TT.MM.JJJJ hh:mm",
                         "TT.MM hh:mm",
                         "TT.MM",
                         "hh:mm"]
        if attr_type in datetime_list:
            value = str(value)
            # crop both ends of string
            value = value.lstrip("['").rstrip("']")
            value = value.lstrip(" ").rstrip(" ")
            # if value entry is empty: fill up
            if value == "" or \
                    value == "NULL" or \
                    value == "None" or \
                    value is None:
                value = str(" " * req_length)

            if len(value) > 16:
                # -> the value automatically turned into
                #  a QDateTime-format, e.g.: value =
                #  "PyQt5.QtCore.QDateTime(2021, 11, 1, 8, 15)"

                # now reformat into something useful
                value = value.lstrip("PyQt5.QtCore.QDateTime(")
                value = value.rstrip(")")
                value = value.replace(" ", "")
                value = value.split(",")

                year = int(value[0])
                month = int(value[1])
                day = int(value[2])
                hour = int(value[3])
                minute = int(value[4])

                # format every string as required
                if attr_type == "TT.MM.JJJJ hh:mm":
                    value = "{:02d}.{:02d}.{:04d} {:02d}:{:02d}" \
                        .format(day, month, year, hour, minute)
                if attr_type == "TT.MM hh:mm":
                    value = "{:02d}.{:02d} {:02d}:{:02d}" \
                        .format(day, month, hour, minute)
                if attr_type == "TT.MM":
                    value = "{:02d}.{:02d}".format(day, month)
                if attr_type == "hh:mm":
                    value = "{:02d}:{:02d}".format(hour, minute)

            else:
                value = str(value)
                # sadly use of parser not possible
                #  due to unrecognizable format "TT.MM"

                # check if length is suitable
                if len(value) != req_length:
                    value = str(val_rep_char * req_length)
                    value_warning = "!!! date/time value was not recognized"

            # does not accept " " as replacement... therefore:
            #  fill up with " " if value is too short
            while len(value) < req_length:
                value = " " + value

        # should not happen, if csv is complete
        if attr_type == "":
            value = str(val_rep_char * req_length)
            value_warning = "!!! value type not recognized"

    # if not possible to convert to required data type:
    except ValueError:
        # if value entry was empty all along: fill up
        if value == "" or \
                value == "NULL" or \
                value is None:
            value = str(" " * req_length)
        # if entry is somehow unsuitable: write replacement character
        else:
            value = str(val_rep_char * req_length)
            value_warning = "!!! value did not match required data type"

    # give it back
    return value, value_warning


#############################################################################


# Checks if TAL-file can be exported correctly
#  (This could have been done in main TAL function, but make it too "wide".)
def export_tal_file():

    # set name of filetype
    filetype = "TAL"

    # get current layer from specific combobox
    current_layer = \
        eval("self.dlg.cb_xxx_layerselection.currentLayer()"
             .replace("xxx", filetype.lower()))

    # get name dictionary for current file type
    current_dict_name = eval(filetype.lower() + "_attr_dict")

    # check if main attribute field name is defined
    if current_dict_name["attr_01"] != "":

        # get field name of layer for first / main file attribute
        main_attr_field_name = current_dict_name["attr_01"]

        # get a list of main attributes ("Talsperren"/"Dams") in layer
        main_attr_list_with_duplicates = []
        # go through all features of current layer
        for feature in current_layer.getFeatures():
            main_attr_list_with_duplicates.\
                append(feature[main_attr_field_name])

        # get list without duplicates
        main_attr_list = []
        for n in main_attr_list_with_duplicates:
            if n not in main_attr_list:
                # only "T"-element
                if str(n).startswith("T"):
                    main_attr_list.append(n)

        # check if main attribute list contains any T-functions
        if len(main_attr_list) != 0:
            # raise "export possible"-function for TAL
            export_tal_file_possible()

        else:
            # raise "export failed"-function for TAL with "reason"
            export_tal_file_failed("T-FUNCTION NAME FAIL")

    else:
        # raise "failed" function for TAL with "reason"
        export_tal_file_failed("DICTIONARY FAIL")


#############################################################################


# Export of TAL-file failed
def export_tal_file_failed(reason):

    # differentiate the reasons for failure
    reason_long = []
    if reason == "DICTIONARY FAIL":
        reason_long = "The TAL-file could not be exported, " \
                      "because no layer field name was matched " \
                      "to the main attribute ('ID')."

    if reason == "T-FUNCTION NAME FAIL":
        reason_long = "The TAL-file could not be exported, " \
                      "because no T-functions ('TXXX') could " \
                      "be found in assigned column of source layer."

    # remove exporting message from message bar
    self.iface.messageBar().popWidget()

    # send a message to user
    self.iface.messageBar().pushWarning(reason, reason_long)

    # get export path
    export_path = self.dlg.fw_export_path.filePath()

    # construct filename
    filename = os.path.join(export_path, "_TAL_export_failed.tal")

    # write file with warning and explanation
    with open(filename, 'w', encoding='ANSI') as file:
        file.write(reason + "\n" + reason_long)

    # set correct file export info as global for TAL
    globals()["tal_file_export_info"] = str("* " + reason_long + "\n")


#############################################################################


# Export a TAL-file, which is different from the standard filetype
#  (it has 1 main table and 6 tables for every main attribute (here: Dams))
def export_tal_file_possible():
    # (function is mostly kept universal, to enable use for other / future
    #  complicated filetypes with 1 + 6x different tables)

    # set name of filetype
    filetype = "TAL"

    # get info about this file type from csv i.e. array via function
    (current_layer, list_number_attr_file,
     pattern, headlines, last_line,
     add_lines_1, add_lines_2, add_lines_3,
     add_lines_4, add_lines_5, add_lines_6,
     add_lines_7) = \
        get_type_info(filetype)

    # get dictionaries for current file type
    current_dict_name = eval(filetype.lower() + "_attr_dict")
    current_dict_type = eval(filetype.lower() + "_file_attr_type_dict")

    # get information about dictionaries
    number_of_attr_in_file = len(current_dict_name)
    number_of_matches = 0
    list_attrs_not_matched = []
    for attr_nr in current_dict_name.keys():
        if current_dict_name[attr_nr] == "":
            list_attrs_not_matched.append(attr_nr)
        else:
            number_of_matches += 1

    # get file name from function
    filename, time_of_export = construct_filename(filetype)

    # create empty list for the value warnings of this file
    current_file_value_warnings_list = []

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # GET VARIABLES FOR ALL 7 SUB-TABLES
    #  (DIVIDE LAYER DATA HORIZONTALLY)

    # handle special file patterns
    pattern_list = pattern.split("\n")
    pattern_main = pattern_list[0]
    pattern_0 = pattern_list[1]
    pattern_1 = pattern_list[2]
    pattern_2 = pattern_list[3]
    pattern_3 = pattern_list[4]
    pattern_4 = pattern_list[5]
    pattern_5 = pattern_list[6]

    # get number of attributes in each pattern
    pattern_main_attr_count = pattern_main.count("{}")
    pattern_0_attr_count = pattern_0.count("{}")
    pattern_1_attr_count = pattern_1.count("{}")
    pattern_2_attr_count = pattern_2.count("{}")
    pattern_3_attr_count = pattern_3.count("{}")
    pattern_4_attr_count = pattern_4.count("{}")
    pattern_5_attr_count = pattern_5.count("{}")

    # get number ranges for attributes in each pattern
    pattern_main_attr_range = \
        range(1,
              1 + pattern_main_attr_count)

    pattern_0_attr_range = \
        range(1 + pattern_main_attr_count,
              1 + pattern_main_attr_count + pattern_0_attr_count)

    pattern_1_attr_range = \
        range(1 + pattern_main_attr_count + pattern_0_attr_count,
              1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count)

    pattern_2_attr_range = \
        range(1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count,
              1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count)

    pattern_3_attr_range = \
        range(1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count,
              1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count
              + pattern_3_attr_count)

    pattern_4_attr_range = \
        range(1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count
              + pattern_3_attr_count,
              1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count
              + pattern_3_attr_count + pattern_4_attr_count)

    pattern_5_attr_range = \
        range(1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count
              + pattern_3_attr_count + pattern_4_attr_count,
              1 + pattern_main_attr_count + pattern_0_attr_count
              + pattern_1_attr_count + pattern_2_attr_count
              + pattern_3_attr_count + pattern_4_attr_count
              + pattern_5_attr_count)

    # create attribute name dictionaries for specific parts
    pattern_main_attr_name_dict = {}
    pattern_0_attr_name_dict = {}
    pattern_1_attr_name_dict = {}
    pattern_2_attr_name_dict = {}
    pattern_3_attr_name_dict = {}
    pattern_4_attr_name_dict = {}
    pattern_5_attr_name_dict = {}

    # fill attribute name dictionaries for specific parts from name dict
    for count, attr_key in enumerate(current_dict_name, start=1):
        if count in pattern_main_attr_range:
            pattern_main_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]
        if count in pattern_0_attr_range:
            pattern_0_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]
        if count in pattern_1_attr_range:
            pattern_1_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]
        if count in pattern_2_attr_range:
            pattern_2_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]
        if count in pattern_3_attr_range:
            pattern_3_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]
        if count in pattern_4_attr_range:
            pattern_4_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]
        if count in pattern_5_attr_range:
            pattern_5_attr_name_dict[attr_key] = \
                current_dict_name[attr_key]

    # create attribute type dictionaries for specific parts
    pattern_main_attr_type_dict = {}
    pattern_0_attr_type_dict = {}
    pattern_1_attr_type_dict = {}
    pattern_2_attr_type_dict = {}
    pattern_3_attr_type_dict = {}
    pattern_4_attr_type_dict = {}
    pattern_5_attr_type_dict = {}

    # fill attribute type dictionaries for specific parts from name dict
    for count, attr_key in enumerate(current_dict_type, start=1):
        if count in pattern_main_attr_range:
            pattern_main_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]
        if count in pattern_0_attr_range:
            pattern_0_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]
        if count in pattern_1_attr_range:
            pattern_1_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]
        if count in pattern_2_attr_range:
            pattern_2_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]
        if count in pattern_3_attr_range:
            pattern_3_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]
        if count in pattern_4_attr_range:
            pattern_4_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]
        if count in pattern_5_attr_range:
            pattern_5_attr_type_dict[attr_key] = \
                current_dict_type[attr_key]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # DIVIDE LAYER FEATURES (ROWS) INTO MAIN ATTRIBUTES OF FILE
    #  (DIVIDE LAYER DATA VERTICALLY)

    # get field name of layer for first / main file attribute
    main_attr_field_name = current_dict_name["attr_01"]

    # get a list of main attributes ("Talsperren"/"Dams") in layer
    main_attr_list_with_duplicates = []
    # go through all features of current layer
    for feature in current_layer.getFeatures():
        main_attr_list_with_duplicates.append(feature[main_attr_field_name])
    # get list without duplicates
    main_attr_list = []
    for n in main_attr_list_with_duplicates:
        if n not in main_attr_list:
            # only "T"-element
            if str(n).startswith("T"):
                main_attr_list.append(n)

    # get dictionary of row indices of main attributes
    main_attr_row_index_dict = {}
    temp_list = []
    temp_previous = ""
    row_count_max = 0
    for row_count, feature in \
            enumerate(current_layer.getFeatures(), start=1):
        # check if this row has a main attribute
        if feature[main_attr_field_name] in main_attr_list:
            # check if main attribute is not in temp list (-> first time)
            if feature[main_attr_field_name] not in temp_list:
                # put main attr name in temp list, so it stays unique
                temp_list.append(feature[main_attr_field_name])
                # put main attr name with its start row index in dictionary
                main_attr_row_index_dict[
                    feature[main_attr_field_name]+"_start"] = \
                    row_count
                # it is not first main attribute, set end for previous
                if temp_previous != "":
                    main_attr_row_index_dict[
                        temp_previous + "_end"] = \
                        row_count - 1
                # set "previous" for next main attribute
                temp_previous = feature[main_attr_field_name]

        # count to max row count
        row_count_max = row_count

    # set end row index in dict for last main attribute (max row count)
    main_attr_row_index_dict[str(main_attr_list[-1]) + "_end"] =\
        row_count_max

    # get ranges for main attributes and put them in dictionary
    main_attr_ranges_dict = {}
    for attr in main_attr_list:
        main_attr_ranges_dict[attr] = \
            range(main_attr_row_index_dict[attr + "_start"],
                  main_attr_row_index_dict[attr + "_end"] + 1)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # WRITE FILE

    # "write" file with "ANSI" encoding
    with open(filename, 'w', encoding='ANSI') as file:

        # write headlines in file
        file.write(headlines)

        # write pattern main table
        feature_counter = 0
        # go through every feature of layer
        for feature in current_layer.getFeatures():
            feature_counter += 1

            # create empty list for current row
            current_row = []
            # go through every attribute pattern main
            for xx in pattern_main_attr_range:
                xx = str(xx)

                # give xx leading 0 if necessary
                if len(xx) < 2:
                    xx = "0" + xx

                # get the required attribute data type
                req_type = \
                    pattern_main_attr_type_dict["attr_" + xx + "_type"]
                # replace possible \xa0 with real spaces
                req_type = req_type.replace(r'\xa0', " ")
                # get required length of output
                req_length = len(str(req_type))

                # check if there is an entry for this attribute
                if pattern_main_attr_name_dict["attr_" + xx] == "":
                    # if no match in feature: fill with enough " "
                    current_row.append(str(" " * req_length))
                else:
                    # handle the corresponding value

                    # get the feature value for attribute from layer
                    value = feature[current_dict_name["attr_" + xx]]

                    # check the value in another function
                    #  and get potential warning
                    value, value_warning = \
                        check_value(value, req_length, req_type)

                    # put value as string in list for current feature
                    current_row.append(str(value))

                    # if there is a value warning
                    if value_warning != "":
                        # add column and row to value warning
                        value_warning = str(xx + ";" +
                                            str(feature_counter)
                                            + ";" + value_warning)

                        # add the warning to the list for this file
                        current_file_value_warnings_list \
                            .append(value_warning)

            # check if current row contains more than empty space
            checkmark = 0
            for char in list_valid_chars_not_space:
                if checkmark == 0 and char in str(current_row):
                    checkmark += 1
                    # write row in file
                    file.write(pattern_main.format(*current_row) + "\n")

        # write lines at end of main table
        file.write(last_line + "\n")

        # end of main table
        # ----------------------------------------------------------------- #
        # now loop for every main attribute

        for main_attr in main_attr_list:

            # get range for this main attribute
            current_range = main_attr_ranges_dict[main_attr]

            # set current text for "Funktion für XXXX in add lines 1"
            current_add_lines_1 = add_lines_1.replace("XXXX", str(main_attr))

            # write add lines 1
            file.write(current_add_lines_1 + "\n")

            # loop for the six sub-tables
            for xxx in [0, 1, 2, 3, 4, 5]:

                # go through every feature of layer
                for feature_count, feature in \
                        enumerate(current_layer.getFeatures(), start=1):

                    # only use feature in current range (this main attr)
                    if feature_count in current_range:

                        # create empty list for current row
                        current_row = []
                        # go through every attribute of this pattern
                        for xx in eval(
                                "pattern_xxx_attr_range"
                                .replace("xxx", str(xxx))):
                            xx = str(xx)

                            # give xx leading 0 if necessary
                            if len(xx) < 2:
                                xx = "0" + xx

                            # get the required attribute data type
                            req_type = \
                                eval("pattern_xxx_attr_type_dict"
                                     "['attr_' + xx + '_type']"
                                     .replace("xxx", str(xxx)))
                            # replace possible \xa0 with real spaces
                            req_type = req_type.replace(r'\xa0', " ")
                            # get required length of output
                            req_length = len(str(req_type))

                            # check if there is an entry for this attribute
                            if eval("pattern_xxx_attr_name_dict"
                                    "['attr_' + xx]"
                                    .replace("xxx", str(xxx))) == "":
                                # if no match in feature:
                                #  fill with enough " "
                                current_row.append(str(" " * req_length))
                            else:
                                # handle the corresponding value

                                # get the feature value for attribute
                                #  from layer
                                value = \
                                    feature[
                                        current_dict_name["attr_" + xx]]

                                # check the value in another function
                                #  and get potential warning
                                value, value_warning = \
                                    check_value(
                                        value, req_length, req_type)

                                # put value as string in list for
                                #  current feature
                                current_row.append(str(value))

                        # check if current row contains more
                        #  than empty space
                        checkmark = 0
                        for char in list_valid_chars_not_space:
                            if checkmark == 0 and char in str(current_row):
                                checkmark += 1
                                # write row in file
                                file.write(eval("pattern_" + str(xxx))
                                           .format(*current_row) + "\n")

                # write matching lines at end of this table table
                #  plus 2 due to different numbering of add lines
                file.write(eval("add_lines_" + str(xxx + 2)) + "\n")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # GET THE EXPORT INFORMATION INTO THE FILE

        # construct the export information for this file
        current_file_export_info = \
            str("* This " + filetype.upper() + "-file was created by "
                "the 'QGIS BlueM Interface Plugin'\n"
                "*   with data from the '" + current_layer.name() +
                "'-layer\n*   on the " + time_of_export + ".\n*\n" +
                "* Of the " + str(number_of_attr_in_file) +
                " file attributes, " + str(number_of_matches) +
                " found a matching field name in the layer.\n"
                "* (including the not printed 'Output_to')\n")

        # if some attributes did not find a match
        if number_of_attr_in_file > number_of_matches:
            current_file_export_info = \
                str(current_file_export_info +
                    "* These attributes found no match: "
                    + str(list_attrs_not_matched) + "\n")

        # if there are value warnings
        nr_warnings = len(current_file_value_warnings_list)

        if nr_warnings == 0:
            current_file_export_info = \
                str(current_file_export_info + "*\n* " +
                    "No values had to be changed or were not "
                    "suitable at all.\n")

        if nr_warnings > 0:
            if nr_warnings == 1:
                current_file_export_info = \
                    str(current_file_export_info + "*\n* " +
                        "1 value had to be changed or was not "
                        "suitable at all:\n*\n")
            if nr_warnings > 1:
                current_file_export_info = \
                    str(current_file_export_info + "*\n* " +
                        str(len(current_file_value_warnings_list)) +
                        " values had to be changed or were not "
                        "suitable at all:\n*\n")

            # write value warnings in file
            for warnings in current_file_value_warnings_list:
                warnings = warnings.split(";")
                current_file_export_info = \
                    str(current_file_export_info +
                        "*  -> For attribute number "
                        + str(warnings[0]) + " of feature "
                        + str(warnings[1]).zfill(3) + ":  "
                        + str(warnings[2]) + "\n")

        # write information into file if checked in GUI
        if self.dlg.cb_bottom_every_file.checkState():
            file.write("*\n*\n*\n*\n*\n*\n*\n"
                       + current_file_export_info)

    # set current file export info as global for filetype
    globals()[filetype.lower() + "_file_export_info"] = \
        current_file_export_info


#############################################################################
#   OTHER EXPORTS  -  Andere Exporte (Kapitel 5.4)                          #
#############################################################################


# Export of user manual into target directory
def export_user_manual():

    user_manual_filename = os.path.join("docs", "USER_MANUAL.pdf")
    source_path = os.path.dirname(__file__)
    target_directory = self.dlg.fw_export_path.filePath()

    # copy user manual from plugin files into target directory
    shutil.copy(os.path.join(source_path, user_manual_filename),
                target_directory)

    # open explorer window if checked in settings (GUI)
    open_explorer_window()


#############################################################################


# Create GeoPackage with layers for all filetypes
def create_geopackage():

    # open explorer window of target directory
    open_explorer_window()

    # display warning message for the "lengthy process" in QGIS
    self.iface.messageBar().pushMessage(
        "LENGTHY PROCESS",
        "Creating 23 Layers with specific fields in a new GeoPackage is "
        "going to take a while...", duration=10)

    # repaint main QGIS window, otherwise the message would only be
    #  displayed after the lengthy and "resource-thirsty" process
    self.iface.mainWindow().repaint()

    # get export path
    export_path = self.dlg.fw_export_path.filePath()

    # get a name for the GeoPackage (from project name if possible)
    if self.dlg.le_project_name.text() == "":
        gpkg_name = "GPKG_BlueM_Inputfiles"
    else:
        gpkg_name = str(self.dlg.le_project_name.text() + "_GPKG")

    # construct filename for the GeoPackage
    gpkg_file = os.path.join(export_path, gpkg_name + ".gpkg")

    # for all filetypes
    for count, filetype in enumerate(list_inputfile_types, start=1):

        # create a temporary layer with polygon geometry
        if filetype in [ "EZG", "FKA", "TAL", "EFL", "DIF"]:
            temp_layer = QgsVectorLayer("Polygon", "temp_layer", "memory")

        # create a temporary layer with multipolygon geometry
        elif filetype in ["BOA", "BOD", "LNZ"]:
            temp_layer = QgsVectorLayer(
                "Multipolygon", "temp_layer", "memory")
            
        # create a temporary layer with linestring geometry
        elif filetype in ["TRS"]:
            temp_layer = QgsVectorLayer(
                "Linestring", "temp_layer", "memory")

        # create a temporary layer with point geometry
        elif filetype in ["BEK", "RUE", "URB", "VER", "HYA", "EIN"]:
            temp_layer = QgsVectorLayer("Point", "temp_layer", "memory")

        # create a temporary layer without geometry
        #  (ALL, SYS, FKT, KTR, EXT, JGG, TGG, WGG)
        else:
            temp_layer = QgsVectorLayer("NoGeometry", "temp_layer", "memory")

        # add fields to the layer
        append_layer_generic(temp_layer, filetype)

        # create a name for the layer
        layer_name = filetype

        if count == 1:
            # save first layer to NEW GeoPackage (no "-update")
            parameters = {"INPUT": temp_layer,
                          "OPTIONS": str("-nln " + layer_name),
                          "OUTPUT": gpkg_file}
            processing.run("gdal:convertformat", parameters)

        else:
            # save following layers to EXISTING GeoPackage (with "-update")
            parameters = {"INPUT": temp_layer,
                          "OPTIONS": str("-update -nln " + layer_name),
                          "OUTPUT": gpkg_file}
            processing.run("gdal:convertformat", parameters)

    # add the GeoPackage to the project
    self.iface.addVectorLayer(
        gpkg_file, gpkg_name, 'ogr')


#############################################################################


# Export a CSV-file with all attribute names and formats
def export_standards():

    # open explorer window if checked in settings (GUI)
    open_explorer_window()

    # get export path
    export_path = self.dlg.fw_export_path.filePath()

    # construct filename
    filename = os.path.join(export_path, "_STANDARDS for Plugin Input.csv")

    with open(filename, 'w', encoding='ANSI') as file:

        # write headlines
        file.write("This table contains the standards regarding names and "
                   "formats of the layer attributes that can be used "
                   "in the BlueM Inputfiles Plugin for QGIS\n\n")

        # write explanations
        file.write("How to read the attribute types:\n"
                   "-> The maximum length of the attribute is the number "
                   "of the characters in its type\n"
                   "-> 's' stands for string (text)\n"
                   "-> 'f' stands for float (e.g. 12,345)\n"
                   "-> 'i' stands for integer (e.g. 12345)\n"
                   "-> 'Y' stands for a decision (e.g. Y or N, etc.)\n"
                   "-> 'TT.MM.JJJJ hh:mm' and similar are formats for date"
                   " and time values\n"
                   "      (T = day, M = month, J = year, h = hour, "
                   "m = minute)\n\n\n")

        # for every filetype
        for filetype in list_inputfile_types:

            # get list of attribute names
            list_attr_names = eval(filetype.lower() + "_file_attr_list")

            # get the number of attributes and make it a list
            number_attr = len(list_attr_names)
            list_number_attr = []
            for xx in range(1, number_attr + 1):
                xx = str(xx)
                if len(xx) < 2:
                    xx = "0" + xx
                list_number_attr.append(xx)

            # get a list of attribute types from global dict
            current_type_dict = \
                eval(filetype.lower() + "_file_attr_type_dict")
            list_attr_types = list(current_type_dict.values())

            # write a count for the attribute numbers
            current_row = str(filetype.upper() + "-file;")
            for xx in list_number_attr:
                current_row = current_row + filetype.upper() \
                              + "_attr_" + xx + ";"
            file.write(current_row + "\n")

            # prepare and write attribute names in file
            current_row = str(filetype.upper() + " attr names;")
            for attr_name in list_attr_names:
                current_row = current_row + attr_name + ";"
            file.write(current_row + "\n")

            # prepare and write attribute types in file
            current_row = str(filetype.upper() + " attr types;")
            for attr_type in list_attr_types:
                current_row = current_row + attr_type + ";"
            file.write(current_row + "\n\n")


#############################################################################


# Export a file with information about the filetypes that were just exported
def export_file_export_information():

    # get export path
    export_path = self.dlg.fw_export_path.filePath()

    # get time of export
    now = datetime.now()

    # construct filename
    filename = os.path.join(export_path, f"_EXPORT_LOG_{now:%Y%m%d_%H%M}.txt")

    # check how many files have been exported
    number_files_to_export = len(list_filetypes_for_export)

    # make it grammatically correct
    if number_files_to_export == 1:
        number_files_to_export = str("1 file that was")
    elif number_files_to_export > 1:
        number_files_to_export = str(str(number_files_to_export)
                                     + " files that were")

    # create file
    with open(filename, 'w', encoding='ANSI') as file:

        # write headlines
        file.write("* EXPORT LOG\n"
                   "* This file summarizes the export information for the "
                   + number_files_to_export + " exported on the "
                   + now.strftime("%Y/%m/%d at %H:%M") + ".\n*\n*\n" + 120*"*" + "\n")

        # for every exported file
        for exported_type in list_filetypes_for_export:
            # get current export info
            current_export_info = \
                eval(exported_type.lower() + "_file_export_info")

            # change wording
            current_export_info = current_export_info.replace("This", "The")

            # write info for this exported file
            file.write("*\n*\n" + current_export_info
                       + "*\n*\n" + 120*"*" + "\n")


#############################################################################
#   GUI FUNCTIONS  -  GUI-Funktionen (Kapitel 5.5)                          #
#############################################################################


# CONNECTIONS TO GUI (Graphical User Interface)
def general_gui_functions():

    # GUI FUNCTIONS

    # TAL (this filetype is used as an example,
    #  the others are handled in the exec-loops in the next section)

    # gui functions are marked as unused by IDE (e.g. PyCharm),
    #  but the connection is established later with eval()

    # enable buttons only if suitable layer is selected
    def tal_layerselection_used():
        if self.dlg.cb_tal_layerselection.currentLayer() is None:
            # uncheck both buttons if layerselection is empty
            self.dlg.pb_tal_byname.setChecked(False)
            self.dlg.pb_tal_manually.setChecked(False)
            # disable both buttons if layerselection is empty
            self.dlg.pb_tal_byname.setEnabled(False)
            self.dlg.pb_tal_manually.setEnabled(False)
        else:
            # enable both buttons if layerselection is not empty
            self.dlg.pb_tal_byname.setEnabled(True)
            self.dlg.pb_tal_manually.setEnabled(True)

    def tal_byname_clicked():
        if self.dlg.pb_tal_byname.isChecked():
            # uncheck other button if necessary
            self.dlg.pb_tal_manually.setChecked(False)
            # disable layerselection
            self.dlg.cb_tal_layerselection.setEnabled(False)
            # match attributes by name and fill dictionary
            create_dict_by_name("TAL")
            # put filename in list for export
            list_filetypes_for_export.append("TAL")
        else:
            # enable layerselection
            self.dlg.cb_tal_layerselection.setEnabled(True)
            # remove filename from list of exports
            list_filetypes_for_export.remove("TAL")

    def tal_manually_clicked():
        if self.dlg.pb_tal_manually.isChecked():
            # enable layer selection (disable in def accept)
            self.dlg.cb_tal_layerselection.setEnabled(True)
            # check if "TAL" is in export list, remove if it is
            if "TAL" in list_filetypes_for_export:
                list_filetypes_for_export.remove("TAL")
            # uncheck other button if necessary
            self.dlg.pb_tal_byname.setChecked(False)
            # uncheck "manually" until second window checks it
            self.dlg.pb_tal_manually.setChecked(False)
            open_second_window("TAL")  # open second window
        else:
            # enable layerselection
            self.dlg.cb_tal_layerselection.setEnabled(True)
            # remove filename from list of exports
            list_filetypes_for_export.remove("TAL")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Create variables of gui functions for later loop
    #  (check TAL-functions above for detailed comments)

    xxx_layerselection_used = \
        "def xxx_layerselection_used():\n" \
        "    if self.dlg.cb_xxx_layerselection.currentLayer() is None:\n" \
        "        self.dlg.pb_xxx_byname.setChecked(False)\n" \
        "        self.dlg.pb_xxx_manually.setChecked(False)\n" \
        "        self.dlg.pb_xxx_byname.setEnabled(False)\n" \
        "        self.dlg.pb_xxx_manually.setEnabled(False)\n" \
        "    else:\n" + \
        "        self.dlg.pb_xxx_byname.setEnabled(True)\n" \
        "        self.dlg.pb_xxx_manually.setEnabled(True)\n"

    xxx_byname_clicked = \
        "def xxx_byname_clicked():\n" \
        "    if self.dlg.pb_xxx_byname.isChecked():\n"\
        "        self.dlg.pb_xxx_manually.setChecked(False)\n" \
        "        self.dlg.cb_xxx_layerselection.setEnabled(False)\n" \
        "        create_dict_by_name('XXX')\n" \
        "        list_filetypes_for_export.append('XXX')\n" \
        "    else:\n" \
        "        self.dlg.cb_xxx_layerselection.setEnabled(True)\n" \
        "        list_filetypes_for_export.remove('XXX')"

    xxx_manually_clicked = \
        "def xxx_manually_clicked():\n" \
        "    if self.dlg.pb_xxx_manually.isChecked():\n" \
        "        self.dlg.cb_xxx_layerselection.setEnabled(True)\n" \
        "        if 'XXX' in list_filetypes_for_export:\n" \
        "            list_filetypes_for_export.remove('XXX')\n" \
        "        self.dlg.pb_xxx_byname.setChecked(False)\n" \
        "        self.dlg.pb_xxx_manually.setChecked(False)\n" \
        "        open_second_window('XXX')\n" \
        "    else:\n" \
        "        self.dlg.cb_xxx_layerselection.setEnabled(True)\n" \
        "        list_filetypes_for_export.remove('XXX')"

    # execute loop for all standard filetypes
    for i in list_inputfile_types_standard:

        # set filetype names correctly in strings
        i_layerselection_used = \
            xxx_layerselection_used.replace("xxx", i.lower())
        i_byname_clicked = \
            xxx_byname_clicked.replace("xxx", i.lower())\
            .replace("XXX", i.upper())
        i_manually_clicked = \
            xxx_manually_clicked.replace("xxx", i.lower())\
            .replace("XXX", i.upper())

        # make functions from string with exec()
        exec(i_layerselection_used)
        exec(i_byname_clicked)
        exec(i_manually_clicked)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # checks the inputs for appending fields to layer
    def append_layer_changed():
        if self.dlg.cb_layer_adaption_selection.currentIndex() != 0 and \
                self.dlg.cb_filetype_combobox.currentIndex() != 0:
            self.dlg.pb_append_layer.setEnabled(True)
            self.dlg.pb_append_layer.setText("APPEND")
        else:
            self.dlg.pb_append_layer.setEnabled(False)
            self.dlg.pb_append_layer.setText("what?")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # checks user input in filewidget (export path)
    def filewidget_changed():
        # check if there are spaces in selected path (not allowed)
        if " " in self.dlg.fw_export_path.filePath():
            # print warning in label and disable exports
            self.dlg.lb_path_info.setText("NO SPACES IN PATH")
            self.dlg.lb_path_info.setStyleSheet("color: rgb(200, 0, 0);")
            self.dlg.pb_export.setEnabled(False)
            self.dlg.pb_export_attr_names.setEnabled(False)
            self.dlg.pb_export_attr_names.setText("  no path")
            self.dlg.pb_export_user_manual.setEnabled(False)
            self.dlg.pb_export_user_manual.setText("  no path")
            self.dlg.pb_create_geopackage.setEnabled(False)
            self.dlg.pb_create_geopackage.setText("no path")

        else:
            # check if path exists (is valid)
            if os.path.exists(self.dlg.fw_export_path.filePath()):
                # remove warning from label and enable exports
                self.dlg.lb_path_info\
                    .setText("Export files to this directory:")
                self.dlg.lb_path_info\
                    .setStyleSheet("color: rgb(50, 50, 50);")
                self.dlg.pb_export.setEnabled(True)
                self.dlg.pb_export_attr_names.setEnabled(True)
                self.dlg.pb_export_attr_names.setText("  Export standards")
                self.dlg.pb_export_user_manual.setEnabled(True)
                self.dlg.pb_export_user_manual\
                    .setText("  Export user manual")
                self.dlg.pb_create_geopackage.setEnabled(True)
                self.dlg.pb_create_geopackage\
                    .setText("Create GeoPackage in target directory")

            # remove warning if path is empty, but disable exports
            elif self.dlg.fw_export_path.filePath() == "":
                self.dlg.lb_path_info \
                    .setText("Export files to this directory:")
                self.dlg.lb_path_info \
                    .setStyleSheet("color: rgb(50, 50, 50);")
                self.dlg.pb_export.setEnabled(False)
                self.dlg.pb_export_attr_names.setEnabled(False)
                self.dlg.pb_export_attr_names.setText("  no path")
                self.dlg.pb_export_user_manual.setEnabled(False)
                self.dlg.pb_export_user_manual.setText("  no path")
                self.dlg.pb_create_geopackage.setEnabled(False)
                self.dlg.pb_create_geopackage.setText("no path")

            else:
                # print warning in label and disable exports
                self.dlg.lb_path_info\
                    .setText("PATH DOES NOT EXIST")
                self.dlg.lb_path_info\
                    .setStyleSheet("color: rgb(200, 0, 0);")
                self.dlg.pb_export.setEnabled(False)
                self.dlg.pb_export_attr_names.setEnabled(False)
                self.dlg.pb_export_attr_names.setText("  no path")
                self.dlg.pb_export_user_manual.setEnabled(False)
                self.dlg.pb_export_user_manual.setText("  no path")
                self.dlg.pb_create_geopackage.setEnabled(False)
                self.dlg.pb_create_geopackage.setText("no path")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # SET TOOL TIPS (the non repetitive ones are set in Qt Designer)

    # set tool tips for layerselection comboboxes
    for xxx in list_inputfile_types:
        eval('self.dlg.cb_xxx_layerselection'
             '.setToolTip("select layer with data for XXX-file")'
             .replace("xxx", xxx.lower()).replace("XXX", xxx.upper()))

    # set tool tips for "by name"-buttons
    for xxx in list_inputfile_types:
        eval('self.dlg.pb_xxx_byname'
             '.setToolTip("match attributes for the XXX-file by name")'
             .replace("xxx", xxx.lower()).replace("XXX", xxx.upper()))

    # set tool tips for "manually"-buttons
    for xxx in list_inputfile_types:
        eval('self.dlg.pb_xxx_manually'
             '.setToolTip("match attributes for the XXX-file manually")'
             .replace("xxx", xxx.lower()).replace("XXX", xxx.upper()))

    # set tool tips for all attribute frames
    for xx in list_number_attr_file_max:
        eval('self.dlg2.frame_attr_xx.setToolTip("Attribute xx")'
             .replace("xx", str(xx)))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # DETECT USER INPUT IN GUI

    # execute for all filetypes
    for j in list_inputfile_types:

        # remove unsuitable layers from layer selection cb
        #  variable marked as unused by IDE, but it is used in eval
        suitable_layers = (QgsMapLayerProxyModel.VectorLayer
                           or QgsMapLayerProxyModel.NoGeometry)
        eval("self.dlg.cb_xxx_layerselection.setFilters(suitable_layers)"
             .replace("xxx", j.lower()))

        # triggers functions if the layer in the selection combo box
        #  is changed
        eval("self.dlg.cb_xxx_layerselection"
             ".layerChanged.connect(xxx_layerselection_used)"
             .replace("xxx", j.lower()))

        # triggers functions if the "by name"-buttons are clicked
        eval("self.dlg.pb_xxx_byname.clicked.connect(xxx_byname_clicked)"
             .replace("xxx", j.lower()))

        # triggers functions if the "manually"-buttons are clicked
        eval("self.dlg.pb_xxx_manually.clicked.connect(xxx_manually_clicked)"
             .replace("xxx", j.lower()))

    # detect change of file path input
    self.dlg.fw_export_path.fileChanged.connect(filewidget_changed)

    # "generate"-button for SYS clicked
    self.dlg.pb_sys_generate.clicked.connect(generate_sys_layer)

    # "export"-button clicked
    self.dlg.pb_export.clicked.connect(export_clicked)

    # "Export user manual"-button clicked
    self.dlg.pb_export_user_manual.clicked.connect(export_user_manual)

    # "Export standards"-button clicked
    self.dlg.pb_export_attr_names.clicked.connect(export_standards)

    # "Clear"-button clicked
    self.dlg.pb_clear.clicked.connect(clear_dlg)

    # Connect value replacement line edit to its check-function
    self.dlg.le_value_replacement.textChanged.connect(check_val_rep_char)

    # layer adaption layer combobox changed
    self.dlg.cb_layer_adaption_selection.layerChanged.connect(append_layer_changed)

    # layer adaption filetype combobox changed
    self.dlg.cb_filetype_combobox.currentIndexChanged \
        .connect(append_layer_changed)

    # "APPEND"-button clicked
    self.dlg.pb_append_layer.clicked.connect(append_layer)

    # "Create GeoPackage"-button clicked
    self.dlg.pb_create_geopackage.clicked.connect(create_geopackage)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Buttons of second window:

    # "match attributes by name if possible" button in second window clicked
    self.dlg2.pb_match_attr_by_name_if_possible.clicked \
        .connect(match_attributes_by_name_if_possible)

    # "match attributes by order" button in second window clicked
    self.dlg2.pb_match_attr_by_order.clicked \
        .connect(match_attributes_by_order)

    # "clear all matches" button in second window clicked
    self.dlg2.pb_clear_all_matches.clicked \
        .connect(clear_all_matches)

    # "set field names from first row" button in second window clicked
    self.dlg2.pb_correct_field_names.clicked \
        .connect(correct_field_names)

    # ok button in second window clicked
    self.dlg2.pb_ok.clicked.connect(execute_second_window)

    # chancel button in second window clicked
    self.dlg2.pb_cancel.clicked.connect(reject_second_window)


#############################################################################


# Set the tab order
def set_tab_order():

    # tab order for first window

    self.dlg.setTabOrder(
        self.dlg.cb_all_layerselection, self.dlg.pb_all_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_all_byname, self.dlg.pb_all_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_all_manually, self.dlg.pb_sys_generate)

    self.dlg.setTabOrder(
        self.dlg.pb_sys_generate, self.dlg.cb_sys_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_sys_layerselection, self.dlg.pb_sys_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_sys_byname, self.dlg.pb_sys_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_sys_manually, self.dlg.cb_fkt_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_fkt_layerselection, self.dlg.pb_fkt_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_fkt_byname, self.dlg.pb_fkt_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_fkt_manually, self.dlg.cb_ktr_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_ktr_layerselection, self.dlg.pb_ktr_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_ktr_byname, self.dlg.pb_ktr_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_ktr_manually, self.dlg.cb_ext_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_ext_layerselection, self.dlg.pb_ext_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_ext_byname, self.dlg.pb_ext_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_ext_manually, self.dlg.cb_jgg_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_jgg_layerselection, self.dlg.pb_jgg_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_jgg_byname, self.dlg.pb_jgg_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_jgg_manually, self.dlg.cb_tgg_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_tgg_layerselection, self.dlg.pb_tgg_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_tgg_byname, self.dlg.pb_tgg_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_tgg_manually, self.dlg.cb_wgg_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_wgg_layerselection, self.dlg.pb_wgg_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_wgg_byname, self.dlg.pb_wgg_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_wgg_manually, self.dlg.cb_bek_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_bek_layerselection, self.dlg.pb_bek_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_bek_byname, self.dlg.pb_bek_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_bek_manually, self.dlg.cb_ein_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_ein_layerselection, self.dlg.pb_ein_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_ein_byname, self.dlg.pb_ein_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_ein_manually, self.dlg.cb_ezg_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_ezg_layerselection, self.dlg.pb_ezg_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_ezg_byname, self.dlg.pb_ezg_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_ezg_manually, self.dlg.cb_fka_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_fka_layerselection, self.dlg.pb_fka_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_fka_byname, self.dlg.pb_fka_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_fka_manually, self.dlg.cb_hya_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_hya_layerselection, self.dlg.pb_hya_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_hya_byname, self.dlg.pb_hya_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_hya_manually, self.dlg.cb_rue_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_rue_layerselection, self.dlg.pb_rue_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_rue_byname, self.dlg.pb_rue_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_rue_manually, self.dlg.cb_tal_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_tal_layerselection, self.dlg.pb_tal_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_tal_byname, self.dlg.pb_tal_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_tal_manually, self.dlg.cb_trs_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_trs_layerselection, self.dlg.pb_trs_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_trs_byname, self.dlg.pb_trs_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_trs_manually, self.dlg.cb_urb_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_urb_layerselection, self.dlg.pb_urb_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_urb_byname, self.dlg.pb_urb_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_urb_manually, self.dlg.cb_ver_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_ver_layerselection, self.dlg.pb_ver_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_ver_byname, self.dlg.pb_ver_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_ver_manually, self.dlg.cb_boa_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_boa_layerselection, self.dlg.pb_boa_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_boa_byname, self.dlg.pb_boa_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_boa_manually, self.dlg.cb_bod_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_bod_layerselection, self.dlg.pb_bod_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_bod_byname, self.dlg.pb_bod_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_bod_manually, self.dlg.cb_efl_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_efl_layerselection, self.dlg.pb_efl_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_efl_byname, self.dlg.pb_efl_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_efl_manually, self.dlg.cb_lnz_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_lnz_layerselection, self.dlg.pb_lnz_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_lnz_byname, self.dlg.pb_lnz_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_lnz_manually, self.dlg.cb_dif_layerselection)

    self.dlg.setTabOrder(
        self.dlg.cb_dif_layerselection, self.dlg.pb_dif_byname)
    self.dlg.setTabOrder(
        self.dlg.pb_dif_byname, self.dlg.pb_dif_manually)
    self.dlg.setTabOrder(
        self.dlg.pb_dif_manually, self.dlg.fw_export_path)

    self.dlg.setTabOrder(self.dlg.fw_export_path, self.dlg.pb_export)
    self.dlg.setTabOrder(self.dlg.pb_export, self.dlg.pb_cancel)

    # second tab of first window

    self.dlg.setTabOrder(
        self.dlg.pb_cancel, self.dlg.pb_export_attr_names)
    self.dlg.setTabOrder(
        self.dlg.pb_export_attr_names, self.dlg.lb_export_user_manual)
    self.dlg.setTabOrder(
        self.dlg.lb_export_user_manual, self.dlg.cb_open_explorer)
    self.dlg.setTabOrder(
        self.dlg.cb_open_explorer, self.dlg.cb_close_after_export)

    self.dlg.setTabOrder(
        self.dlg.cb_close_after_export, self.dlg.le_value_replacement)
    self.dlg.setTabOrder(
        self.dlg.le_value_replacement, self.dlg.cb_bottom_every_file)
    self.dlg.setTabOrder(
        self.dlg.cb_bottom_every_file, self.dlg.cb_separate_file)

    self.dlg.setTabOrder(
        self.dlg.cb_separate_file, self.dlg.le_project_name)
    self.dlg.setTabOrder(
        self.dlg.le_project_name, self.dlg.pb_type_in_name)
    self.dlg.setTabOrder(
        self.dlg.pb_type_in_name, self.dlg.pb_layer_in_name)
    self.dlg.setTabOrder(
        self.dlg.pb_layer_in_name, self.dlg.pb_time_in_name)

    self.dlg.setTabOrder(
        self.dlg.pb_time_in_name, self.dlg.cb_layer_adaption_selection)
    self.dlg.setTabOrder(
        self.dlg.cb_layer_adaption_selection, self.dlg.cb_filetype_combobox)
    self.dlg.setTabOrder(
        self.dlg.cb_filetype_combobox, self.dlg.pb_append_layer)
    self.dlg.setTabOrder(
        self.dlg.pb_append_layer, self.dlg.pb_create_geopackage)

    self.dlg.setTabOrder(
        self.dlg.pb_create_geopackage, self.dlg.pb_clear)
    self.dlg.setTabOrder(
        self.dlg.pb_clear, self.dlg.fw_export_path)
    self.dlg.setTabOrder(
        self.dlg.fw_export_path, self.dlg.pb_export)
    self.dlg.setTabOrder(
        self.dlg.pb_export, self.dlg.pb_cancel)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # tab order for second window

    self.dlg2.setTabOrder(
        self.dlg2.pb_ok,
        self.dlg2.pb_cancel)
    self.dlg2.setTabOrder(
        self.dlg2.pb_cancel,
        self.dlg2.scrollArea_example)

    self.dlg2.setTabOrder(
        self.dlg2.scrollArea_example,
        self.dlg2.scrollArea_attr_match)
    self.dlg2.setTabOrder(
        self.dlg2.scrollArea_attr_match,
        self.dlg2.pb_match_attr_by_name_if_possible)

    self.dlg2.setTabOrder(
        self.dlg2.pb_match_attr_by_name_if_possible,
        self.dlg2.pb_match_attr_by_order)
    self.dlg2.setTabOrder(
        self.dlg2.pb_match_attr_by_order,
        self.dlg2.pb_clear_all_matches)

    self.dlg2.setTabOrder(
        self.dlg2.pb_clear_all_matches,
        self.dlg2.pb_correct_field_names)
    self.dlg2.setTabOrder(
        self.dlg2.pb_correct_field_names,
        self.dlg2.pb_ok)


#############################################################################
#   ADAPTING EXISTING LAYERS                                                #
#       Änderungen an bestehenden Layern (Kapitel 5.6)                      #
#############################################################################


# Correct i.e. set field names in attribute table of faulty layer
def correct_field_names():

    # get current filetype of second window from global variable
    filetype = current_filetype_second_window

    # get selected layer for current filetype
    faulty_layer = \
        eval("self.dlg.cb_xxx_layerselection.currentLayer()"
             .replace("xxx", str(filetype.lower())))

    # start editing layer
    faulty_layer.startEditing()

    # change field names
    for field in faulty_layer.fields():
        # checks if names are really faulty
        if field.name()[:5] == "Field":
            # get index of current field
            index_faulty_name = \
                faulty_layer.fields().indexFromName(field.name())

            # get the features of the layer
            feature_count = 0
            value_first_row = ""
            for feature in faulty_layer.getFeatures():
                # get the first entry in that column
                while feature_count < 1:
                    feature_count += 1
                    value_first_row = feature[field.name()]

            # give column new field name
            faulty_layer.renameAttribute(
                index_faulty_name, str(value_first_row))

    # stop editing layer
    faulty_layer.commitChanges()

    # The first row (containing the field names) could have been deleted,
    #  but this would change the original data in the excel / csv file.
    # Therefore the row with the field names gets filtered out in the
    #  export file function.

    # If the QGIS layer is deleted later, it may create a copy of the
    #  first row in the original excel / csv file.

    # reopen second window so that changes take effect in the comboboxes
    open_second_window(filetype)


#############################################################################


# Get information from GUI and give it to general function
def append_layer():

    # get layer which to append to
    layer_to_append = self.dlg.cb_layer_adaption_selection.currentLayer()

    # get filetype from combobox
    filetype = self.dlg.cb_filetype_combobox.currentText()

    # give to generic function
    append_layer_generic(layer_to_append, filetype)

    # display message in QGIS
    self.iface.messageBar().pushMessage(str(filetype.upper() +
                                            "-fields appended to layer: "),
                                        str(layer_to_append.name()))

    # do something special if filetype is SYS
    if filetype.upper() == "SYS":
        change_widget_type_sys(layer_to_append)


#############################################################################


# Append fields of a specific filetype to a specific layer
def append_layer_generic(layer_to_append, filetype):

    # get a list of the field names for this filetype
    current_filetype_fields_list = eval(filetype.lower() + "_file_attr_list")

    # get a dictionary for the current field type definitions
    current_dict_type = eval(filetype.lower() + "_file_attr_type_dict")

    # create a new dictionary with field name as key
    #  and QVariant.XXX as value
    field_name_to_qvariant_dict = {}
    for field_name, field_type \
            in zip(current_filetype_fields_list, current_dict_type.values()):

        # set field type to int for integer
        if field_type.startswith("i"):
            field_name_to_qvariant_dict[str(field_name)] = QVariant.Int
        # set field type to double (other word for float)
        elif field_type.startswith("f"):
            field_name_to_qvariant_dict[str(field_name)] = QVariant.Double
        # set field type for dates or time to datetime
        elif field_type.startswith(("T", "M", "J", "h", "m")):
            field_name_to_qvariant_dict[str(field_name)] = QVariant.DateTime
        # set field type of a decision value or string to string
        else:
            field_name_to_qvariant_dict[str(field_name)] = QVariant.String

    # get a list of existing field names in layer
    existing_fields_list = []
    for field in layer_to_append.fields():
        existing_fields_list.append(field.name())

    # get a list of fields that are to append to the layer
    fields_to_append_list = []
    for field_name in current_filetype_fields_list:
        if field_name not in existing_fields_list:
            fields_to_append_list.append(field_name)

    # add all necessary fields to the layer with its correct type
    for field_name in fields_to_append_list:
        layer_to_append.dataProvider().addAttributes(
            [QgsField(str(field_name),
                      field_name_to_qvariant_dict[field_name])])

    # update the attribute table
    layer_to_append.updateFields()


#############################################################################


# change field widget type for SYS
def change_widget_type_sys(layer):

    # list of fields in SYS file that need a drop down menu
    list_sys_fields_drop_down = ["Zulauf_1", "Zulauf_2", "Zulauf_3",
                                 "Ablauf_1", "Ablauf_2", "Ablauf_3"]

    # the source for the drop down menu should be this field
    field_source = "Nr"

    # loop through all fields that need a drop down menu & send to function
    for field in list_sys_fields_drop_down:
        change_widget_type(layer, field, field_source)


#############################################################################


# change widget type of field in attribute table to a drop down menu
def change_widget_type(layer, field_to_change, field_source):

    # get index of field_to_change in layer
    i = layer.fields().indexFromName(field_to_change)

    # define the change (ValueRelation with values from field_source)
    new_setup = QgsEditorWidgetSetup('ValueRelation',
                                     {'AllowMulti': False,
                                      'AllowNull': True,
                                      'FilterExpression': '',
                                      'Key': field_source,
                                      'Layer': layer.id(),
                                      'NofColumns': 1,
                                      'OrderByValue': False,
                                      'UseCompleter': False,
                                      'Value': field_source})

    # execute change for field with index i
    layer.setEditorWidgetSetup(i, new_setup)


#############################################################################
#   SUPPORT FUNCTIONS  -  Support-Funktionen (Kapitel 5.7)                  #
#############################################################################


# create and layer and fill it with SYS-information from other Layers
def generate_sys_layer():

    # define field name of ID in element layers
    field_name_id = "BlueM_ID"

    # define field name of where they output to in element layers
    field_name_output_to = "Output_to"

    # list of filetypes that contain information about elements
    element_filetypes_list = ["BEK", "EIN", "EZG", "FKA", "HYA",
                              "RUE", "TAL", "TRS", "URB", "VER"]

    # get a list of layers with element-data
    element_data_layer_list = []

    for XXX in element_filetypes_list:

        # check for the current element-filetype if a layer is selected
        if eval("self.dlg.cb_xxx_layerselection.currentIndex()"
                .replace("xxx", XXX.lower())) != -1:

            # if a layer is selected, append it to the list
            element_data_layer_list.append(
                eval("self.dlg.cb_xxx_layerselection.currentLayer()"
                     .replace("xxx", XXX.lower())))

    # if there is at least one layer with element-data selected
    if len(element_data_layer_list) != 0:

        # create empty dictionary for sys elements
        sys_elements_dict = {}

        # create a list of invalid values for ID
        nono_list = [None, "", "NULL", " ", "None"]

        # go through every element data layer
        for layer in element_data_layer_list:

            # check if "layer" really is something
            if layer is not None:

                # check if both fields exist
                if layer.fields().indexOf(field_name_id) != -1 \
                 and layer.fields().indexOf(field_name_output_to) != -1:

                    # go through every feature of current layer
                    for feature in layer.getFeatures():

                        # get output_to with ID into dictionary
                        sys_id = feature[field_name_id]
                        output_to = feature[field_name_output_to]
                        if sys_id not in nono_list:
                            sys_elements_dict[sys_id] = str(output_to)

        # Add ZPG ("Zielpegel") with no output to elements-dictionary
        sys_elements_dict["ZPG"] = ""

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # CREATE A NEW LAYER

        # define name for new sys-layer
        name_new_sys_layer = "Generated_SYS_layer_temporary"

        # check if there is already a layer with that name
        if len(QgsProject.instance().mapLayersByName(
                name_new_sys_layer)) != 0:

            # remove other layers
            for evil_layer in QgsProject.instance()\
                    .mapLayersByName(name_new_sys_layer):
                QgsProject.instance().removeMapLayer(evil_layer)

        # create a new layer with that name and add it to the project
        new_sys_layer = QgsVectorLayer(
            "NoGeometry", name_new_sys_layer, "memory")
        QgsProject.instance().addMapLayer(new_sys_layer)

        # get the field names for the new sys layer via other functions
        append_layer_generic(new_sys_layer, "SYS")
        change_widget_type_sys(new_sys_layer)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # FILL THAT LAYER WITH FEATURES

        # for all sys elements, reformat output_to
        for element in sys_elements_dict.keys():

            # divide up dict value, if there are multiple parts to it
            value = sys_elements_dict[element]
            value = value.replace(";", " ")
            value = value.replace(",", " ")
            value_list = value.split(" ")

            # remove empty values (from to many spaces)
            while "" in value_list:
                value_list.remove("")

            # make sure only a max of 3 items are in value list
            while len(value_list) > 3:
                value_list.pop()

            # put it back into the dictionary (overwrite old value)
            sys_elements_dict[element] = value_list

        # create a new dictionary for input_from
        sys_input_from = {}

        # for all sys elements, build a reverse dictionary
        for element1 in sys_elements_dict.keys():

            # list for element1 input_from
            element1_list = []

            # for every element check every dict entry
            for element2 in sys_elements_dict.keys():

                # check where the element is in the output_to_list
                if element1 in sys_elements_dict[element2]:

                    # add element2 to the list of input_from for element1
                    element1_list.append(element2)

            # cut element1 list, if it wrongly contains more than 3
            while len(element1_list) > 3:
                element1_list.pop()

            # add element1 and its list to the new dict
            sys_input_from[element1] = element1_list

        # create empty list of features
        feat_list = []

        # for all sys elements, reformat output_to
        for element in sys_elements_dict.keys():

            # add the feature with its info to the layer
            feat = QgsFeature()
            feat.setFields(new_sys_layer.fields())
            feat.setAttribute(1, element)

            # add input_from to attributes
            for x in range(0, len(sys_input_from[element])):
                feat.setAttribute(2 + x, sys_input_from[element][x])

            # add output_to to attributes
            for x in range(0, len(sys_elements_dict[element])):
                feat.setAttribute(5 + x, sys_elements_dict[element][x])

            # add feature to list of features
            feat_list.append(feat)

        # start editing layer and add features from list to it
        with edit(new_sys_layer):
            new_sys_layer.addFeatures(feat_list)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # HOUSEKEEPING

        # select new layer in combobox
        self.dlg.cb_sys_layerselection.setLayer(new_sys_layer)

        # check "by name"-button and additional stuff (not the normal way)
        if self.dlg.pb_sys_byname.isChecked():
            create_dict_by_name('SYS')
        else:
            self.dlg.pb_sys_byname.setChecked(True)
            self.dlg.pb_sys_manually.setChecked(False)
            self.dlg.cb_sys_layerselection.setEnabled(False)
            create_dict_by_name('SYS')
            list_filetypes_for_export.append('SYS')

        # display message with information about SYS-layer creation
        self.iface.messageBar().pushMessage(
            "SYS-layer created",
            "A new layer was created from element-data of the other layers "
            "and added to the SYS-file layerselection")

    else:
        # display a warning if there are no layers with element data
        self.iface.messageBar().pushMessage(
            "No elements for new SYS-layer found",
            "Please select layers for the element-files with suitable data")


#############################################################################


# Opens a windows explorer window of the export directory
def open_explorer_window():

    # only if option is checked in settings (GUI, dlg, tab2)
    if self.dlg.cb_open_explorer.isChecked():
        export_path = str(self.dlg.fw_export_path.filePath())
        os.system(str('start ' + export_path))


#############################################################################


# Get the filetype index for this filetype
def get_filetype_index(filetype):

    # get the index of the current filetype in the array
    #  (only search in the "name_short" column, otherwise there might be
    #  more than one match)

    # start at -1 one because first row is then 0
    row_index = -1
    # filetype_index has to be set here to avoid a warning, but will be set
    #  correctly in the if-statement
    filetype_index = 1
    # go through every row of array and check the "name_short" column
    for row in inputfiles_overview:
        row_index += 1
        if row[int(index_name_short)] == filetype:
            filetype_index = row_index

    # give filetype index back
    return filetype_index


#############################################################################


# Get data about "this" type of file from csv i.e. array
def get_type_info(filetype):

    # get current layer from specific combobox
    current_layer = \
        eval("self.dlg.cb_xxx_layerselection.currentLayer()"
             .replace("xxx", filetype.lower()))

    # get filetype index from function
    filetype_index = get_filetype_index(filetype)

    # get the number of attributes for the filetype
    number_attr_filetype = \
        int(inputfiles_overview[int(filetype_index)]
                               [int(index_attr_count)])

    # create list of numbers of attributes for this filetype
    list_number_attr_file = []
    for i in range(1, number_attr_filetype + 1):
        if len(str(i)) == 1:  # give i a leading zero if necessary
            i = "0" + str(i)
        list_number_attr_file.append(str(i))

    # get attribute insertion pattern for this filetype from csv
    pattern = str(inputfiles_overview[filetype_index][index_pattern])
    # remove both ends of element
    pattern = pattern.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi line pattern
    pattern = pattern.replace(r"\n", "\n")
    # add line escape to end of pattern
    pattern = pattern + "\n"
    # replace possible \xa0 with real spaces
    pattern = pattern.replace(r'\xa0', " ")

    # get matching headlines from csv
    headlines = str(inputfiles_overview
                    [filetype_index]
                    [index_headlines])
    # crop both ends of string
    headlines = headlines.lstrip("['").rstrip("']")
    # "\n" is a valid character in the original csv element,
    #  so it has to be replaced with a line escape
    headlines = headlines.replace(r"\n", "\n")
    # crop possible line escape from the end
    headlines = headlines.rstrip("\n")
    # add line escape at the end
    headlines = headlines + "\n"
    # replace possible \xa0 with real spaces
    headlines = headlines.replace(r'\xa0', " ")

    # get matching additional lines 1 ("add_lines_1") from csv
    add_lines_1 = \
        str(inputfiles_overview[filetype_index][index_add_lines_1])
    # crop both ends of string
    add_lines_1 = add_lines_1.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_1 = add_lines_1.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_1 = add_lines_1.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_1 = add_lines_1.replace(r'\xa0', " ")

    # get matching additional lines 2 ("add_lines_2") from csv
    add_lines_2 = \
        str(inputfiles_overview[filetype_index][index_add_lines_2])
    # crop both ends of string
    add_lines_2 = add_lines_2.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_2 = add_lines_2.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_2 = add_lines_2.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_2 = add_lines_2.replace(r'\xa0', " ")

    # get matching additional lines 3 ("add_lines_3") from csv
    add_lines_3 = \
        str(inputfiles_overview[filetype_index][index_add_lines_3])
    # crop both ends of string
    add_lines_3 = add_lines_3.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_3 = add_lines_3.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_3 = add_lines_3.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_3 = add_lines_3.replace(r'\xa0', " ")

    # get matching additional lines 4 ("add_lines_4") from csv
    add_lines_4 = \
        str(inputfiles_overview[filetype_index][index_add_lines_4])
    # crop both ends of string
    add_lines_4 = add_lines_4.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_4 = add_lines_4.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_4 = add_lines_4.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_4 = add_lines_4.replace(r'\xa0', " ")

    # get matching additional lines 5 ("add_lines_5") from csv
    add_lines_5 = \
        str(inputfiles_overview[filetype_index][index_add_lines_5])
    # crop both ends of string
    add_lines_5 = add_lines_5.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_5 = add_lines_5.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_5 = add_lines_5.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_5 = add_lines_5.replace(r'\xa0', " ")

    # get matching additional lines 6 ("add_lines_6") from csv
    add_lines_6 = \
        str(inputfiles_overview[filetype_index][index_add_lines_6])
    # crop both ends of string
    add_lines_6 = add_lines_6.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_6 = add_lines_6.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_6 = add_lines_6.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_6 = add_lines_6.replace(r'\xa0', " ")

    # get matching additional lines 7 ("add_lines_7") from csv
    add_lines_7 = \
        str(inputfiles_overview[filetype_index][index_add_lines_7])
    # crop both ends of string
    add_lines_7 = add_lines_7.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    add_lines_7 = add_lines_7.replace(r"\n", "\n")
    # crop possible line escape from the end
    add_lines_7 = add_lines_7.rstrip("\n")
    # replace possible \xa0 with real spaces
    add_lines_7 = add_lines_7.replace(r'\xa0', " ")

    # get matching last line from csv
    last_line = \
        str(inputfiles_overview[filetype_index][index_last_line])
    # crop both ends of string
    last_line = last_line.lstrip("['").rstrip("']")
    # exchange "\n" if necessary for multi input
    last_line = last_line.replace(r"\n", "\n")
    # crop possible line escape from the end
    last_line = last_line.rstrip("\n")
    # replace possible \xa0 with real spaces
    last_line = last_line.replace(r'\xa0', " ")

    # give the data back
    return (current_layer, list_number_attr_file,
            pattern, headlines, last_line,
            add_lines_1, add_lines_2, add_lines_3,
            add_lines_4, add_lines_5, add_lines_6,
            add_lines_7)


#############################################################################


# Check the value replacement character
def check_val_rep_char():

    char = self.dlg.le_value_replacement.text()

    if char not in list_valid_chars_not_space:
        char = " "

    global val_rep_char
    val_rep_char = char

    # set text in line edit with something valid
    self.dlg.le_value_replacement.setText(val_rep_char)


#############################################################################


# Construct a name for the file that is currently written
def construct_filename(filetype):

    # get export path
    export_path = self.dlg.fw_export_path.filePath()

    # get project name from line edit
    project_name = self.dlg.le_project_name.text()

    # get filetype name in suitable format
    filetype_name = str(filetype.upper() + "_file")

    # get name of source layer
    name_source_layer = \
        eval("self.dlg.cb_xxx_layerselection.currentText()"
             .replace("xxx", filetype.lower()))
    # remove possible spaces from layer name
    name_source_layer = name_source_layer.replace(" ", "_")
    # add "from"
    name_source_layer = str("from_" + name_source_layer)

    # get time of export
    now = datetime.now()
    # reformat suitably
    time_of_export = now.strftime("%Y%m%d_%H%M")
    time_of_export_2 = now.strftime("%Y/%m/%d at %H:%M")

    # construct the name of the file
    filename = ""

    # add project name
    if project_name is not "":
        filename = self.dlg.le_project_name.text()

    # add filetype
    if self.dlg.pb_type_in_name.isChecked():
        filename = str(filename + "_" + filetype_name)

    # add source layer
    if self.dlg.pb_layer_in_name.isChecked():
        filename = str(filename + "_" + name_source_layer)

    # add time of export
    if self.dlg.pb_time_in_name.isChecked():
        filename = str(filename + "_" + time_of_export)

    # remove "_" from front if project name is empty
    if project_name == "":
        filename = filename.lstrip("_")

    # remove 1 char from front if project name is "_" and
    #  other things are in filename
    if project_name == "_" and len(filename) > 1:
        filename = filename[1:]

    # make name something, if it is not already
    if filename == "":
        filename = "unnamed"

    # add export path to filename
    filename = os.path.join(export_path, filename)

    # shorten filename if necessary
    max_filename_len = 250  # not 255 because of extension
    #  32000+ characters possible since Windows 10

    if len(filename) > max_filename_len:
        # shorten filename to maximum possible
        filename = filename[0:max_filename_len]

    # add matching file extension to file name
    filename = str(filename + "." + filetype.lower())

    # give filename back
    return filename, time_of_export_2


#############################################################################


# Clear layerselection comboboxes and uncheck all buttons in first dialog
def clear_dlg():

    # clear list of files for export
    global list_filetypes_for_export
    list_filetypes_for_export = []

    # for all filetypes
    for xxx in list_inputfile_types:

        # enable and set layerselection combobox to index 0 (empty)
        eval("self.dlg.cb_xxx_layerselection.setEnabled(True)"
             .replace("xxx", xxx.lower()))
        eval("self.dlg.cb_xxx_layerselection.setCurrentIndex(0)"
             .replace("xxx", xxx.lower()))

        # uncheck and disable "by name" button
        eval("self.dlg.pb_xxx_byname.setChecked(False)"
             .replace("xxx", xxx.lower()))
        eval("self.dlg.pb_xxx_byname.setEnabled(False)"
             .replace("xxx", xxx.lower()))

        # uncheck and disable "manually" button
        eval("self.dlg.pb_xxx_manually.setChecked(False)"
             .replace("xxx", xxx.lower()))
        eval("self.dlg.pb_xxx_manually.setEnabled(False)"
             .replace("xxx", xxx.lower()))


#############################################################################


"""

                        ,&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                      &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                   .&&&&&&&&&&&,                                   &&&&&&&&&&
                 &&&&&&&  &&&&&,                                &&&&&&&.&&&&&
               &&&&&&&    &&&&&,                              &&&&&&&   &&&&&
            &&&&&&&.      &&&&&,                           &&&&&&&//    &&&&&
          &&&&&&&         &&&&&, &&,,,,(&  (&*,,,,&& *&*,&&&&&&&,,,,,,&&&&&&&
       &&&&&&&,           &&&##/,,,,,,,,,*,,,,,,,,,,,,&&&&&&&/,,,,,,,&..&&&&&
     &&&&&&&             &#####*,,,,,,/,,,,,,,,,,/,,&&&&&&&,,,,,,,*&....&&&&&
  &&&&&&&*            #%,,(####*,,,,,,,,,,,,,,/,,&&&&&&&(,,,,,,,&,......&&&&&
%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&,,,,,,,,&.........&&&&&
%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&#,,,,,,,&(...........&&&&&
%&&&&/         &,,,,,,,,,,##(##*,,,,,,/,,,,,,,&&&&&,,,,,,&..............&&&&&
%&&&&/      #%,,/,,,,,,,,*#####*,,,*,,,,,,,,,*&&&&&,,,#%................&&&&&
%&&&&/    &,,*,,,,,,,,,*,,#####*,,,,,,,,,,,,,,&&&&&,&...................&&&&&
%&&&&/ #%,,(,,,,,,,,&&,,,,###%&&&,,,,,,,#&&,,,&&&&&.....................&&&&&
%&&&&&&&......&&&&......(&&&(((,...&&&........&&&&&.....................&&&&&
%&&&&(....................(((((,..............&&&&&.....................&&&&&
%&&&&(....................((((((((((((((((((((&&&&&(((((((((((((((((((((&&&&&
%&&&&(..................((((((((((((((((((((((&&&&&(((((((((((((((((((%&&&&&&
%&&&&(...............,(((((((.................&&&&&.................&&&&&&&, 
%&&&&(.............(((((((....................&&&&&...............&&&&&&&    
%&&&&/..........,(((((((......................&&&&&............%&&&&&&*      
%&&&&/........(((((((.........................&&&&&..........&&&&&&&         
%&&&&/.....,(((((((...........................&&&&&.......%&&&&&&(           
%&&&&/...(((((((..............................&&&&&.....&&&&&&&              
%&&&&/.(((((((................................&&&&&..(&&&&&&#                
%&&&&&(((((,..................................&&&&&&&&&&&&                   
%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%                     
%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&                        

"""
