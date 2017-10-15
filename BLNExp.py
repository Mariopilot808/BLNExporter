"""
/***************************************************************************
BLNExp
                                 A QGIS plugin
 Converts polygon or line shapes to BLN
                              -------------------
        begin                : 2014-16-09
        copyright            : (C) 2014 by Mario Noriega
        email                : mario@norcex.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4.QtGui import *
from qgis.core import QgsProject
from qgis.gui import *
from PyQt4 import QtCore, QtGui 



import resources


import os

# Import the code for the dialog

class blnexp:


    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface


    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/blnexp/icon.png"),
            "Export VEctor Data to Surfer BLN", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)


        # Add toolbar button and menu item
        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.EnablePlugin)
        self.iface.digitizeToolBar().addAction(self.action)
        if hasattr ( self . iface , "addPluginToVectorMenu" ):
            self.iface.addPluginToVectorMenu("&BLN Exporter", self.action)
        else:
            self.iface.addPluginToMenu("&BLN Exporter", self.action)
        self.action.setEnabled(False)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&BLN Exporter",self.action)
        #self.iface.advancedDigitizeToolBar().removeAction(self.action)
        self.iface.removeToolBarIcon(self.action)



    # run method that performs all the real work
    def run(self):
        layer = self.iface.activeLayer()
        provider = layer.dataProvider()
        nFeatures = layer.featureCount()
        


        path_absolute = QgsProject.instance().readPath("./")
        fnm = layer.name()
        fnext = fnm + '.BLN'
        p = os.path.join(path_absolute, fnext)
        feature = QgsFeature()
        pcent = 0

        #file save dialog
        fileName = QtGui.QFileDialog.getSaveFileName(self.iface.mainWindow(), 'Save (cancel for default name)', path_absolute, '*.BLN')
        if len(str (fileName)) == 0:
            fileName = p
        else:
            p = fileName

        # create the progress dialog
        progressDialog = QProgressDialog('Exporting...', "Cancel", 0, 100)
        progressDialog.setWindowTitle('BLN Exporter')
        # create a file stream that supports callback
        


#reset file
        f = open(p,'w')
        f.write('')
        f.close()
        canc = 0

#multipart to singlepart.
        for i, feature in enumerate(layer.dataProvider().getFeatures()):
            pcent = float(i+1) / nFeatures * 100
            
            canc = self.update_progress(progressDialog, pcent)
            if ( canc == 1 ):
                break
            #QMessageBox.information(None, "Percent:", unicode(str(percent)))
            geom = feature.geometry()
            # if feature geometry is multipart starts split processing
            if geom != None:
                f = open(p,'a')
                if geom.isMultipart():
                    new_features = []
                    #n_of_splitted_features += 1
                    temp_feature = QgsFeature()
                        
                    # Get parts geometries from original feature
                    parts = geom.asGeometryCollection ()
                            
                    # from 2nd to last part create a new features using their
                    # single geometry and the attributes of the original feature
                    
                    # Convert part to multiType to prevent errors in Spatialite
                    for part in parts:
                        part.convertToMultiType()
                   
                    for i in range(1,len(parts)):
                        temp_feature.setGeometry(parts[i])
                        temp_feature.geometry().convertToMultiType()
                        #save sub-parts
                        self.ExtractCoords(temp_feature.geometry(),f)
                    temp_feature.setGeometry(parts[0])
                    #save sub-part 0
                    self.ExtractCoords(temp_feature.geometry(),f)
                else:
                    #if it is singlepart
                    self.ExtractCoords(geom,f)
        if (canc == 0):
            QMessageBox.information(None, "BLN Exporter","Saved file: " + unicode(p))
        else:
            QMessageBox.information(None, "BLN Exporter", "Operation Cancelled")




    #function that extracts vertex coordinates to a BLN formatted string
    def ExtractCoords(self, poly, file):

#feature header writer
        j = 0
        killatnext = 0
        vert0 = poly.vertexAt(0) #save first vertex to stop if loop closed
        layer = self.iface.activeLayer()
        while True:
            vertXY = poly.vertexAt(j)
            X=vertXY.x()
            Y=vertXY.y()
            #kill loop if either at invalid pint or if the loop closed.
            if ((X == 0) and (Y == 0)) or (killatnext == 1):
                file.write(str(j) + ',Generated By BLNExtporter\n')
                break
            if (vertXY == vert0) and (j > 0 ) and (layer.geometryType() == QGis.Polygon): #if line, do not check loop closing
                killatnext = 1
            j += 1

# Point writer
        j = 0
        killatnext = 0
        while True:
            vertXY = poly.vertexAt(j)
            X=vertXY.x()
            Y=vertXY.y()
            if ((X == 0) and (Y == 0)) or (killatnext ==1):
                break
            if (X <> 0) and (Y <> 0):
                VertBLN=str(X) + ',' + str(Y) + '\n'
                file.write(VertBLN)
            if (vertXY == vert0) and (j > 0 ) and (layer.geometryType() == QGis.Polygon): #if line, do not check loop closing
                killatnext = 1
            j += 1



    def update_progress(self,progressbar, progress):
        progressbar.setLabelText('Exporting...' )
        progressbar.setValue(progress)
        QApplication.processEvents()
    
        if progressbar.wasCanceled():
            return 1
        else: 
            return 0


    def EnablePlugin(self):
        layer = self.iface.activeLayer()
        if layer <> QgsRasterLayer:
            if (layer.geometryType() == QGis.Polygon) or (layer.geometryType() == QGis.Line) or (layer.geometryType() == QGis.Point):
                self.action.setEnabled(True)
                
            else:
                self.action.setEnabled(False)
