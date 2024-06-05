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
import os

from PyQt5.QtWidgets import QMenu, QAction
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

from . import additional_actions
from . import tools

from . import help_render


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

    def _create_truncate_action(self, parent):
        truncate_menu = QMenu()

        truncate_all_layers = QAction(
            self.tr("Delete features in all layers"),
            parent=truncate_menu
        )
        truncate_all_layers.triggered.connect(self.truncate_all_layers)
        truncate_menu.addAction(truncate_all_layers)

        truncate_menu.addSeparator()

        truncate_layers_in_selected_groups = QAction(
            self.tr("Delete all layers features in selected group(s)"),
            parent=truncate_menu
        )
        truncate_layers_in_selected_groups.triggered.connect(self.truncate_all_layers_in_selected_groups)
        truncate_menu.addAction(truncate_layers_in_selected_groups)

        truncate_menu.addSeparator()

        truncate_selected_layers = QAction(
            self.tr("Delete all features in selected layer(s)"),
            parent=truncate_menu
        )
        truncate_selected_layers.triggered.connect(self.truncate_selected_layers)
        truncate_menu.addAction(truncate_selected_layers)

        truncate_action = QAction(
            self.tr("Truncate (delete features in vector layers)"),
            parent=parent
        )
        truncate_action.setMenu(truncate_menu)

        return truncate_action

    def _export_layers_to_dir_action(self, parent):
        export_layers_to_dir_menu = QMenu()

        export_layers_to_dir_all_layers = QAction(
            self.tr("Copy all layers files to directory"),
            parent=export_layers_to_dir_menu
        )
        export_layers_to_dir_all_layers.triggered.connect(self.export_all_layers_to_dir)
        export_layers_to_dir_menu.addAction(export_layers_to_dir_all_layers)

        export_layers_to_dir_menu.addSeparator()

        export_layers_to_dir_selected_groups = QAction(
            self.tr("Copy layers files in selected group(s) to directory"),
            parent=export_layers_to_dir_menu
        )
        export_layers_to_dir_selected_groups.triggered.connect(self.export_layers_in_selected_groups_to_dir)
        export_layers_to_dir_menu.addAction(export_layers_to_dir_selected_groups)

        export_layers_to_dir_menu.addSeparator()

        export_layers_to_dir_selected_layers = QAction(
            self.tr("Copy selected layers files to directory"),
            parent=export_layers_to_dir_menu
        )
        export_layers_to_dir_selected_layers.triggered.connect(self.export_selected_layers_to_dir)
        export_layers_to_dir_menu.addAction(export_layers_to_dir_selected_layers)

        export_layers_to_dir_menu.addSeparator()

        copy_layers_in_order_making_a_tree_dict = QAction(
            self.tr("Copy layers files (including sub-groups) making a directory tree"),
            parent=export_layers_to_dir_menu
        )

        copy_layers_in_order_making_a_tree_dict_menu = QMenu()
        copy_layers_in_order_making_a_tree_dict_starting_from_root = QAction(
            self.tr("Start from root"),
            parent=copy_layers_in_order_making_a_tree_dict_menu
        )
        copy_layers_in_order_making_a_tree_dict_starting_from_root.triggered.connect(lambda: self.copy_layers_files_making_a_tree_dict_starting_from_selected_group(True))
        copy_layers_in_order_making_a_tree_dict_menu.addAction(copy_layers_in_order_making_a_tree_dict_starting_from_root)
        copy_layers_in_order_making_a_tree_dict_menu.addSeparator()

        copy_layers_in_order_making_a_tree_dict_starting_from_selected_group = QAction(
            self.tr("Start from selected group"),
            parent=copy_layers_in_order_making_a_tree_dict_menu
        )
        copy_layers_in_order_making_a_tree_dict_starting_from_selected_group.triggered.connect(lambda: self.copy_layers_files_making_a_tree_dict_starting_from_selected_group(False))
        copy_layers_in_order_making_a_tree_dict_menu.addAction(copy_layers_in_order_making_a_tree_dict_starting_from_selected_group)
        copy_layers_in_order_making_a_tree_dict.setMenu(copy_layers_in_order_making_a_tree_dict_menu)

        export_layers_to_dir_menu.addAction(copy_layers_in_order_making_a_tree_dict)

        export_layers_to_dir_action = QAction(
            self.tr("Copy layers files to directory"),
            parent=parent
        )
        export_layers_to_dir_action.setMenu(export_layers_to_dir_menu)

        return export_layers_to_dir_action

    def copy_layers_files_making_a_tree_dict_starting_from_selected_group(self, start_from_root: bool = False):
        selected_groups = []

        if start_from_root:
            selected_groups = [tools.get_layer_tree()]
        else:
            selected_groups = tools.get_selected_groups()

        if not selected_groups:
            return

        if len(selected_groups) > 1:
            tools.show_dialog_error_message('Please select only one group')
            return

        destination_directory = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            self.tr("Select starting directory to export layers to"),
            options=QFileDialog.ShowDirsOnly
        )

        if not destination_directory or destination_directory == '/':
            return

        res = tools.ask_question(
            'Use layer name as file name?',
            'Do you want to use layer name or original file name for copied files?',
            'Use layer name',
            'Use original file name'
        )

        if res is None:
            return

        additional_actions.copy_layer_files_making_a_dir_tree(selected_groups[0], destination_directory, res)

    def _create_feature_count_action(self, parent):
        toggle_feature_count_menu = QMenu()

        toggle_feature_count_all_layers_on = QAction(
            self.tr("Toggle feature count ON (all layers)"),
            parent=toggle_feature_count_menu
        )
        toggle_feature_count_all_layers_on.triggered.connect(lambda: self.toggle_all_nodes_feature_count(True))
        toggle_feature_count_menu.addAction(toggle_feature_count_all_layers_on)

        toggle_feature_count_all_layers_off = QAction(
            self.tr("Toggle feature count OFF (all layers)"),
            parent=toggle_feature_count_menu
        )
        toggle_feature_count_all_layers_off.triggered.connect(lambda: self.toggle_all_nodes_feature_count(False))
        toggle_feature_count_menu.addAction(toggle_feature_count_all_layers_off)
        toggle_feature_count_menu.addSeparator()

        toggle_feature_count_selected_groups_on = QAction(
            self.tr("Toggle feature count ON (in selected group(s))"),
            parent=toggle_feature_count_menu
        )
        toggle_feature_count_selected_groups_on.triggered.connect(
            lambda: self.toggle_nodes_feature_count_in_selected_groups(True)
        )
        toggle_feature_count_menu.addAction(toggle_feature_count_selected_groups_on)

        toggle_feature_count_selected_groups_off = QAction(
            self.tr("Toggle feature count OFF (in selected group(s))"),
            parent=toggle_feature_count_menu
        )
        toggle_feature_count_selected_groups_off.triggered.connect(
            lambda: self.toggle_nodes_feature_count_in_selected_groups(False)
        )
        toggle_feature_count_menu.addAction(toggle_feature_count_selected_groups_off)
        toggle_feature_count_menu.addSeparator()

        toggle_feature_count_selected_nodes_on = QAction(
            self.tr("Toggle feature count ON (selected layers)"),
            parent=toggle_feature_count_menu
        )
        toggle_feature_count_selected_nodes_on.triggered.connect(
            lambda: self.toggle_nodes_feature_count_on_selected_nodes(True)
        )
        toggle_feature_count_menu.addAction(toggle_feature_count_selected_nodes_on)

        toggle_feature_count_selected_nodes_off = QAction(
            self.tr("Toggle feature count OFF (selected layers)"),
            parent=toggle_feature_count_menu
        )
        toggle_feature_count_selected_nodes_off.triggered.connect(
            lambda: self.toggle_nodes_feature_count_on_selected_nodes(False)
        )
        toggle_feature_count_menu.addAction(toggle_feature_count_selected_nodes_off)

        toggle_feature_count_action = QAction(
            self.tr("Toggle feature count"),
            parent=parent
        )
        toggle_feature_count_action.setMenu(toggle_feature_count_menu)

        return toggle_feature_count_action

    def _create_commit_changes_action(self, parent):
        commit_changes_menu = QMenu()

        commit_changes_all_layers = QAction(
            self.tr("Commit changes (all layers)"),
            parent=commit_changes_menu
        )
        commit_changes_all_layers.triggered.connect(self.commit_changes_to_all_layers)
        commit_changes_menu.addAction(commit_changes_all_layers)

        commit_changes_menu.addSeparator()

        commit_changes_selected_layers_in_selected_groups = QAction(
            self.tr("Commit changes (layers in selected group(s))"),
            parent=commit_changes_menu
        )
        commit_changes_selected_layers_in_selected_groups.triggered.connect(
            self.commit_changes_to_layers_in_selected_groups)
        commit_changes_menu.addAction(commit_changes_selected_layers_in_selected_groups)

        commit_changes_menu.addSeparator()

        commit_changes_selected_layers = QAction(
            self.tr("Commit changes (selected layers)"),
            parent=commit_changes_menu
        )
        commit_changes_selected_layers.triggered.connect(self.commit_changes_to_selected_layers)
        commit_changes_menu.addAction(commit_changes_selected_layers)

        commit_changes_action = QAction(
            self.tr("Commit changes"),
            parent=parent
        )
        commit_changes_action.setMenu(commit_changes_menu)

        return commit_changes_action

    def _create_reload_action(self, parent):
        reload_layers_menu = QMenu()

        reload_selected_layers = QAction(
            self.tr("Reload selected layers"),
            parent=reload_layers_menu
        )
        reload_selected_layers.triggered.connect(self.reload_selected_layers)
        reload_layers_menu.addAction(reload_selected_layers)
        reload_layers_menu.addSeparator()

        reload_layers_in_selected_groups = QAction(
            self.tr("Reload layers in selected group(s)"),
            parent=reload_layers_menu
        )
        reload_layers_in_selected_groups.triggered.connect(self.reload_layers_in_selected_groups)
        reload_layers_menu.addAction(reload_layers_in_selected_groups)
        reload_layers_menu.addSeparator()

        reload_all_layers = QAction(
            self.tr("Reload all layers"),
            parent=reload_layers_menu
        )
        reload_all_layers.triggered.connect(self.reload_all_layers)
        reload_layers_menu.addAction(reload_all_layers)

        reload_layers = QAction(
            self.tr("Reload layers"),
            parent=parent
        )
        reload_layers.setMenu(reload_layers_menu)

        return reload_layers

    def expand_doubleclicked_group(self):
        selected_groups = tools.get_selected_groups()

        if not selected_groups:
            return

        group = selected_groups[0]

        if group.isExpanded():
            group.setExpanded(False)
            return

        group.setExpanded(True)

    def _expand_selected_group(self, state: bool):
        self.iface.layerTreeView().doubleClicked.connect(self.expand_doubleclicked_group)

    def _create_expanding_groups_with_doubleclick_action(self, parent):
        expand_groups_with_doubleclick_action = QAction(
            self.tr("Expand groups with double click"),
            parent=parent,
            checkable=True
        )
        expand_groups_with_doubleclick_action.triggered.connect(self._expand_selected_group)

        return expand_groups_with_doubleclick_action

    def _get_additional_actions_menu(self):
        additional_actions_menu = QMenu()

        additional_actions_menu.addAction(self._create_feature_count_action(additional_actions_menu))
        additional_actions_menu.addSeparator()

        additional_actions_menu.addAction(self._create_reload_action(additional_actions_menu))
        additional_actions_menu.addSeparator()

        additional_actions_menu.addAction(self._create_truncate_action(additional_actions_menu))
        additional_actions_menu.addSeparator()

        additional_actions_menu.addAction(self._create_commit_changes_action(additional_actions_menu))
        additional_actions_menu.addSeparator()

        additional_actions_menu.addAction(self._export_layers_to_dir_action(additional_actions_menu))

        additional_actions_menu.addSeparator()

        additional_actions_menu.addAction(self._create_expanding_groups_with_doubleclick_action(additional_actions_menu))

        return additional_actions_menu

    def export_layers_in_selected_groups_to_dir(self):
        groups = tools.get_selected_groups()

        if not groups:
            return

        destination_directory = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            self.tr("Select directory to export layers to"),
            options=QFileDialog.ShowDirsOnly
        )

        res = tools.ask_question(
            'Use layer name as file name?',
            'Do you want to use layer name or original file name for copied files?',
            'Use layer name',
            'Use original file name'
        )

        if res is None:
            return

        for group in groups:
            additional_actions.copy_layer_files_in_group_to_dir(group, destination_directory + '/', res)

    def export_selected_layers_to_dir(self):
        destination_directory = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            self.tr("Select directory to export layers to"),
            options=QFileDialog.ShowDirsOnly
        )

        if not destination_directory or destination_directory == '/':
            return

        res = tools.ask_question(
            'Use layer name as file name?',
            'Do you want to use layer name or original file name for copied files?',
            'Use layer name',
            'Use original file name'
        )

        if res is None:
            return

        additional_actions.export_selected_layers_to_dir(destination_directory + '/', res)

    def export_all_layers_to_dir(self):
        destination_directory = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            self.tr("Select directory to export layers to"),
            options=QFileDialog.ShowDirsOnly
        )

        if not destination_directory or destination_directory == '/':
            return

        res = tools.ask_question(
            'Use layer name as file name?',
            'Do you want to use layer name or original file name for copied files?',
            'Use layer name',
            'Use original file name'
        )

        if res is None:
            return

        for group in tools.get_all_groups():
            additional_actions.copy_layer_files_in_group_to_dir(group, destination_directory + '/', res)

    def commit_changes_to_selected_layers(self):
        for layer in tools.get_selected_layers():
            tools.commit_changes_to_layer(layer)

    def commit_changes_to_layers_in_selected_groups(self):
        for group in tools.get_selected_groups():
            additional_actions.commit_changes_to_layers_in_group(group)

    def commit_changes_to_all_layers(self):
        for group in tools.get_all_groups():
            additional_actions.commit_changes_to_layers_in_group(group)

    def truncate_all_layers(self):
        if not tools.show_yes_no_message('Are you sure you want to truncate all layers?\n\nWARNING: This action cannot be reversed.'):
            return

        for group in reversed(tools.get_all_groups()):
            additional_actions.truncate_all_layers_in_group(group)

    def truncate_selected_layers(self):
        if not tools.show_yes_no_message('Are you sure you want to truncate selected layers?\n\nWARNING: This action cannot be reversed.'):
            return

        additional_actions.truncate_selected_layers()

    def truncate_all_layers_in_selected_groups(self):
        if not tools.show_yes_no_message('Are you sure you want to truncate all layers in selected group(s)?\n\nWARNING: This action cannot be reversed.'):
            return

        for group in tools.get_selected_groups():
            additional_actions.truncate_all_layers_in_group(group)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        sort_icon_path = self.plugin_dir + '/sort_icon.png'
        snapshot_icon_path = self.plugin_dir + '/snapshot_icon.png'
        additional_actions_icon_path = self.plugin_dir + '/additional_actions_icon.png'

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

        self.action_additional_actions = QAction(
            QIcon(additional_actions_icon_path),
            self.tr("Additionals actions"),
            parent=self.iface.mainWindow(),
        )
        self.layers_panel_actions.append(self.action_additional_actions)

        self.action_additional_actions.setMenu(self._get_additional_actions_menu())

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
        self.action_plugin_toolbar_additional_actions = QAction(
            QIcon(additional_actions_icon_path),
            self.tr('Additional actions'),
            self.iface.mainWindow()
        )
        self.action_plugin_toolbar_additional_actions.setMenu(self._get_additional_actions_menu())

        self.action_sorter.triggered.connect(self.run)
        self.action_snapshooter.triggered.connect(self.run_snapshooter)

        menu = self.toolbutton.menu()

        menu.addAction(self.action_sorter)
        menu.addAction(self.action_snapshooter)
        menu.addAction(self.action_plugin_toolbar_additional_actions)

        self.toolbutton.setDefaultAction(self.action_sorter)

        self.actions.append(self.action_sorter)
        self.actions.append(self.action_snapshooter)
        self.actions.append(self.action_plugin_toolbar_additional_actions)

        if help_render.is_runnable():

            self.action_help = QAction(
                self.tr('Help'),
                self.iface.mainWindow()
            )

            self.action_change_log = QAction(
                self.tr('Change log'),
                self.iface.mainWindow()
            )
            self.action_help.triggered.connect(self.show_help)
            self.action_change_log.triggered.connect(self.show_changelog)

            menu.addAction(self.action_help)
            menu.addAction(self.action_change_log)

            self.actions.append(self.action_help)
            self.actions.append(self.action_change_log)

        # /plugins toolbar

        self.first_start = True

    def show_changelog(self):
        self.w = help_render.ChangeLogDialog()
        self.w.show()

    def show_help(self):
        self.w = help_render.HelpDialog()
        self.w.show()

    def reload_all_layers(self):
        for group in tools.get_all_groups():
            additional_actions.reload_layers_in_group(group)

    def reload_layers_in_selected_groups(self):
        for group in tools.get_selected_groups():
            additional_actions.reload_layers_in_group(group)

    def reload_selected_layers(self):
        for layer in tools.get_selected_layers():
            tools.reload_layer(layer)

    def toggle_nodes_feature_count_on_selected_nodes(self, state: bool):
        for node in tools.get_selected_nodes():
            if tools.is_node_a_group(node):
                continue
            tools.toggle_feature_count(node, state)

    def toggle_nodes_feature_count_in_selected_groups(self, state: bool):
        for group in tools.get_selected_groups():
            additional_actions.toggle_all_layers_in_group_feature_count(group, state)

    def toggle_all_nodes_feature_count(self, state: bool):
        for group in tools.get_all_groups():
            additional_actions.toggle_all_layers_in_group_feature_count(group, state)

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
        if self.first_start:
            self.first_start = False
            self.dlg = SortAndGroupDialog()
            # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
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
