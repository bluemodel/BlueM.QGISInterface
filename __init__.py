# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CreateBlueMInputFiles
                                 A QGIS plugin
 Create BlueM input files
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-10-29
        copyright            : (C) 2021 by Martin Grosshaus
        email                : mgrosshaus@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

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
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CreateBlueMInputFiles class from file CreateBlueMInputFiles.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .create_bluem_input_files import CreateBlueMInputFiles
    return CreateBlueMInputFiles(iface)
