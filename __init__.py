# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EcosolLog
                                 A QGIS plugin
 EcosolLog
                             -------------------
        begin                : 2015-09-08
        copyright            : (C) 2015 by Everton Bortolini
        email                : evertonbortolini@hotmail.com
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
    """Load EcosolLog class from file EcosolLog.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .EcosolLog import EcosolLog
    return EcosolLog(iface)
