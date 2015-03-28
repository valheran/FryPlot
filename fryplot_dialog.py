# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FryPlotDialog
                                 A QGIS plugin
 a utility for performing autocorrelation analysis (fry plots) of point data
                             -------------------
        begin                : 2015-02-15
        git sha              : $Format:%H$
        copyright            : (C) 2015 by A Brown
        email                : email
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

import os

from PyQt4 import QtGui, uic, QtCore

import fryplot_utils as utils
import qgis.core
from qgis.utils import *
from qgis.gui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib import pyplot as plt

import numpy as np

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'fryplot_dialog_base.ui'))


class FryPlotDialog(QtGui.QDialog, FORM_CLASS):

    tarLayer = 0
    fryspaceFigure = None
    frylengthFigure = None
    roseFigure = None
    #calcButton = 0
    
    def __init__(self, iface, parent=None):
    
    
    
        """Constructor."""
        super(FryPlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-
        self.iface = iface
        self.setupUi(self)
        #self.buttonPress()
        FryPlotDialog.tarLayer = self.targetLayer
        
        self.manageGui()
        ##initialise matplot figures/canvas
        FryPlotDialog.fryspaceFigure = InitFigure(self.fryplotLayout, self.fryplotToolbar)
        FryPlotDialog.frylengthFigure = InitFigure(self.frylenLayout, self.frylenToolbar)
        FryPlotDialog.roseFigure = InitRose(self.roseLayout, self.roseToolbar)
        
        #actions of buttons
        self.calcButton.clicked.connect(self.calc)    ##the intended function of the button
        self.openFbtn.clicked.connect(self.showFileBrowser)
        #self.calcButton.clicked.connect(self.fryspacePlotter)
        
    def manageGui(self):
		
		FryPlotDialog.tarLayer.clear()
		FryPlotDialog.tarLayer.addItems(utils.getVectorLayerNames())
    
    
    def showFileBrowser(self):
        self.openFpseudo.setText(QtGui.QFileDialog.getSaveFileName(self, 'Save As', '/',"*.shp"))
        
       
    
    def calc(self):
        #run the calculations and plots selected in check boxes
                    #at the moment ignore checkbox and just run to see if backend machinery is working
         #set target layer
        #iface.messageBar().pushMessage("background calc", "Step 1", level=QgsMessageBar.INFO)
        #QgsMessageLog.logMessage("Message","the button was pressed", QgsMessageLog.INFO)
        #QMessageBox.information(None, "DEBUG:", "Button was pressed")
        target= self.tarLayer.currentText()
       
        
        #set output Layer for pseudo fry plot  ## need to set up to do this from dialog box
        outLayer = self.openFpseudo.text()
       
        
         #initialise class 
        analysis = utils.FryAnalysis(target, outLayer)
       
        
        #pull the data
        analysis.getData()
        #do the calculations to generate fry points and vector data
        analysis.makeFryplotlists()
        
        #Perform the pseudoplot
        if self.chkPseuPlot.isChecked():
            analysis.makePseudoFryplot()
       
        #plot in fryspace scatter plot
        if self.chkFSPlot.isChecked():
            self.fryspacePlotter(analysis.fryListX, analysis.fryListY)
        
        #plot fryvector lengths on histogram
        if self.chkFVPlot.isChecked():
            self.frylengthPlotter(analysis.lenList)
        
        #plot fryvector azimuths on rose diagram
        if self.chkRsDiag.isChecked():
            self.rosePlotter(analysis.vecList)
            
        #export results to text file ####not implemented yet
        if self.chkExTxt.isChecked():
            pass
       
        
            
    def fryspacePlotter(self, fryListX, fryListY):
    
        
        FryPlotDialog.fryspaceFigure.axes.clear()
        FryPlotDialog.fryspaceFigure.axes.set_title("Fryspace Plot")
        
        x = fryListX
        y = fryListY
        #print x
        FryPlotDialog.fryspaceFigure.axes.plot(x,y,'bo')
        FryPlotDialog.fryspaceFigure.axes.axis('equal')
        FryPlotDialog.fryspaceFigure.axes.grid(b=True)
        FryPlotDialog.fryspaceFigure.canvas.draw()
        
    def frylengthPlotter(self, lenList):
    
     
        FryPlotDialog.frylengthFigure.axes.clear()
        FryPlotDialog.frylengthFigure.axes.set_title("Frylength Distribution")
        
        x = lenList
        
        FryPlotDialog.frylengthFigure.axes.hist(x)
        
        FryPlotDialog.frylengthFigure.canvas.draw()
        
    def rosePlotter(self, aziList):
    
        FryPlotDialog.roseFigure.axes.set_title("Fryvector distribution")
        angle = 15 #the width of the divisions of the rose diagram. later stage this could be set by value in dialog box
                 ##get data list
        data = aziList
         #set up bin parameters
        nsection = 360 / angle
        direction = np.linspace(0, 360, nsection, False) / 180 * np.pi
        #print direction
        ##set up list for counting frequency
        frequency = [0] * (nsection)
        ##count up how many in each bin
      
        for i in data:
            
            tmp = int((i - (i % angle)) / angle) ##figure out which bin data belongs
            frequency[tmp] = frequency[tmp] + 1
             
        awidth = angle / 180.0 * np.pi * np.ones(nsection) ## makes an array with nection entries all with the same number representing the angular width
        
        FryPlotDialog.roseFigure.axes.bar(direction, frequency, width=awidth, bottom=0.0)
        FryPlotDialog.roseFigure.canvas.draw()
        
    
    def buttonPress(self):
        message = 'Button Pressed'
        qgis.core.QgsMessageLog.logMessage(message)
        #iface.messageBar().pushMessage("background calc", message, level=QgsMessageBar.INFO)
        
 
    
class InitFigure:
    
    def __init__(self, plotTarget, barTarget):
         # add matplotlib figure to dialog
        self.plotTarget = plotTarget  
        self.barTarget = barTarget
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.mpltoolbar = NavigationToolbar(self.canvas, self.barTarget)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction(lstActions[7])
        self.plotTarget.addWidget(self.canvas)
        self.plotTarget.addWidget(self.mpltoolbar)

        # and configure matplotlib params
        rcParams["font.serif"] = "Verdana, Arial, Liberation Serif"
        rcParams["font.sans-serif"] = "Tahoma, Arial, Liberation Sans"
        rcParams["font.cursive"] = "Courier New, Arial, Liberation Sans"
        rcParams["font.fantasy"] = "Comic Sans MS, Arial, Liberation Sans"
        rcParams["font.monospace"] = "Courier New, Liberation Mono"
        
class InitRose:
    
    def __init__(self, plotTarget, barTarget):
         # add matplotlib figure to dialog
        self.plotTarget = plotTarget  
        self.barTarget = barTarget
        
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111, polar = True) #set up a plot with polar co-ordinates
        self.axes.set_theta_direction(-1)  #change the direction of increasing angle to match compass
        self.axes.set_theta_zero_location("N") #change the O theta position to North
        self.canvas = FigureCanvas(self.figure)
        self.mpltoolbar = NavigationToolbar(self.canvas, self.barTarget)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction(lstActions[7])
        self.plotTarget.addWidget(self.canvas)
        self.plotTarget.addWidget(self.mpltoolbar)

        # and configure matplotlib params
        rcParams["font.serif"] = "Verdana, Arial, Liberation Serif"
        rcParams["font.sans-serif"] = "Tahoma, Arial, Liberation Sans"
        rcParams["font.cursive"] = "Courier New, Arial, Liberation Sans"
        rcParams["font.fantasy"] = "Comic Sans MS, Arial, Liberation Sans"
        rcParams["font.monospace"] = "Courier New, Liberation Mono" 
  