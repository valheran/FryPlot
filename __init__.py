# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FryPlot
                                 A QGIS plugin
 a utility for performing autocorrelation analysis (fry plots) of point data
                             -------------------
        begin                : 2015-02-15
        copyright            : (C) 2015 by A Brown
        email                : email
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FryPlot class from file FryPlot.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fryplot import FryPlot
    return FryPlot(iface)
