"""
/*******BLNexp
                                 A QGIS plugin
 Exports to Vector data to SurferBLN
                             -------------------
        begin                : 2014-16-09
        copyright            : (C) 2014 by Mario Noriega
        email                : Mario@norcex.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "BLN Exporter"
def description():
    return "Converts Vector layers to BLN"
def version():
    return "Version 0.2"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "2.0"
def classFactory(iface):
    # load BLNExp class from file BLNExp
    from BLNExp import blnexp
    return blnexp(iface)
