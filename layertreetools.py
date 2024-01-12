# -*- coding: utf-8 -*-
"""
/***************************************************************************
 layer_tree_tools
                                 A QGIS plugin
 Sorts layers from A-Z, Z-A, by feature count, geometry and many more
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-10-10
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Viper MiniQ
        email                : viperminiq@gmail.com
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
# import pydevd_pycharm
# pydevd_pycharm.settrace('127.0.0.1', port=53100, stdoutToServer=True, stderrToServer=True)

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
# from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .layer_tree_tools_dialog import SortAndGroupDialog
from .snapshooter_dialog import snapshooterDialog
import os.path


class LayerTreeTools:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LayerTreeTools_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.layers_panel_actions = []
        self.menu = self.tr(u'&layer_tree_tools')

        self.toolbutton = QToolButton()
        self.toolbutton.setMenu(QMenu())
        self.toolbutton.setPopupMode(QToolButton.MenuButtonPopup)
        self.toolbutton_action = self.iface.addToolBarWidget(self.toolbutton)

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('layer_tree_tools', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        sort_icon_path = self.plugin_dir + '/sort_icon.png'
        snapshot_icon_path = self.plugin_dir + '/snapshot_icon.png'

        # layers panel

        self.action_sorter_layers_panel = QAction(
            QIcon(sort_icon_path),
            self.tr("Sort and group"),
            parent=self.iface.mainWindow(),
        )
        self.action_sorter_layers_panel.triggered.connect(self.run)
        self.layers_panel_actions.append(self.action_sorter_layers_panel)

        self.action_snapshots_layers_panel = QAction(
            QIcon(snapshot_icon_path),
            self.tr("Snapshots"),
            parent=self.iface.mainWindow(),
        )
        self.action_snapshots_layers_panel.triggered.connect(self.run_snapshooter)
        self.layers_panel_actions.append(self.action_snapshots_layers_panel)

        layers_panel_toolbar = self._get_layers_panel_toolbar()

        if layers_panel_toolbar:
            for action in self.layers_panel_actions:
                layers_panel_toolbar.addAction(action)

        # /layers panel

        # plugins toolbar
        self.action_sorter = QAction(
            QIcon(sort_icon_path),
            self.tr('Sort and group layer tree'),
            self.iface.mainWindow()
        )
        self.action_snapshooter = QAction(
            QIcon(snapshot_icon_path),
            self.tr('Take tree snapshots'),
            self.iface.mainWindow()
        )

        self.action_sorter.triggered.connect(self.run)
        self.action_snapshooter.triggered.connect(self.run_snapshooter)

        menu = self.toolbutton.menu()

        menu.addAction(self.action_sorter)
        menu.addAction(self.action_snapshooter)

        self.toolbutton.setDefaultAction(self.action_sorter)

        self.actions.append(self.action_sorter)
        self.actions.append(self.action_snapshooter)

        # /plugins toolbar

        self.first_start = True

    def _get_layers_panel_toolbar(self):
        return self.iface.mainWindow().findChild(QDockWidget, "Layers").findChild(QToolBar)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&layer_tree_tools'),
                action
            )
        self.iface.removeToolBarIcon(self.toolbutton_action)

        layers_panel_toolbar = self._get_layers_panel_toolbar()
        if layers_panel_toolbar:
            for action in self.layers_panel_actions:
                layers_panel_toolbar.removeAction(action)

        self.iface.removeToolBarIcon(self.toolbutton_action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        dlg = SortAndGroupDialog()
        # show the dialog
        dlg.show()
        # Run the dialog event loop
        result = dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def run_snapshooter(self):
        dlg = snapshooterDialog()
        # show the dialog
        dlg.show()
        # Run the dialog event loop
        dlg.exec_()
        # See if OK was pressed
        if dlg.result():
            pass
             # Do something useful here - delete the line containing pass and
             # substitute with your code.
        #    pass
