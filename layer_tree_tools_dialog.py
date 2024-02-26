# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SortAndGroupDialog
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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from . import grouper
from . import tools
from . import sorter
from . import definitions

from typing import List

from qgis.core import QgsLayerTreeGroup


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sort_and_group_dialog_base.ui'))


# TODO: instead of applying order within sorting, have a function call get sorted values and it return them for the first func to apply them - first func iterates through tree
# TODO: fill geometry listbox from DEFINITIONS
# TODO: check featureCount if layer is a vector layer


class SortAndGroupDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.setModal(True)

        self.setWindowTitle("Sort and group layers")

        self.comboBoxSort.currentTextChanged.connect(self.change_page)
        self.pushButtonSort.clicked.connect(self.sort_a)
        self.pushButtonGroup.clicked.connect(self.group_nodes)
        self.pushButtonRefresh.clicked.connect(self.change_page)

        # TODO: change Run to Sort in self.commands
        self.commands = {
            "Name": {
                "Name": "Name",
                "Sort": lambda: self.sort_by_name(),
                "Refresh": None,
                "GroupSameValues": lambda: self.group_by_name()
            },
            "Geometry": {
                "Name": "Geometry",
                "Sort": lambda: self.sort_by_geometry(),
                "Refresh": None,
                "GroupSameValues": lambda: self.group_same_geometry()
            },
            "Filetype": {
                "Name": "Filetype",
                "Sort": lambda: self.sort_by_file_type(),
                "Refresh": lambda: self.refresh_loaded_layers_extensions(),
                "GroupSameValues": lambda: self.group_by_filetype()
            },
            "Position": {
                "Name": "Position",
                "Sort": lambda: self.sort_by_position(),
                "Refresh": None,
                "GroupSameValues": None
            },
            "Features": {
                "Name": "Feature count",
                "Sort": lambda: self.sort_by_feature_count(),
                "Refresh": None,
                "GroupSameValues": lambda: self.group_by_feature_count()
            },
            "StorageType": {
                "Name": "Storage type",
                "Sort": lambda: self.sort_by_storage_type(),
                "Refresh": lambda: self.refresh_loaded_layers_storage_types(),
                "GroupSameValues": lambda: self.group_by_storage_type()
            },
            "SizeOnDisk": {
                "Name": "Size on disk",
                "Sort": lambda: self.sort_by_size_on_disk(),
                "Refresh": None,
                "GroupSameValues": lambda: self.group_by_size_on_disk()
            },
            "LastModified": {
                "Name": "Last modified",
                "Sort": lambda: self.sort_by_last_modified(),
                "Refresh": None,
                "GroupSameValues": lambda: self.group_by_last_modified_time()
            },
            "Encoding": {
                "Name": "Encoding",
                "Sort": lambda: self.sort_by_encoding(),
                "Refresh": lambda: self._refresh_encodings(),
                "GroupSameValues": lambda: self.group_by_encoding()
            },
        }

        self.checkBoxGroupContainingSubstring.stateChanged.connect(self._manage_additional_actions_visibility)
        self.checkBoxGroupMatchingRegex.stateChanged.connect(self._manage_additional_actions_visibility)

        self._manage_additional_actions_visibility()

        self.set_combobox_items()
        self.set_default_listbox_geometries()

        self.tabWidget.setCurrentIndex(0)

    def _manage_additional_actions_visibility(self):
        if self.checkBoxGroupMatchingRegex.isChecked():
            self.checkBoxGroupContainingSubstring.setDisabled(True)
        else:
            self.checkBoxGroupContainingSubstring.setDisabled(False)
        self._state_changed_group_containing_substring()

        if self.checkBoxGroupContainingSubstring.isChecked():
            self.checkBoxGroupMatchingRegex.setDisabled(True)
        else:
            self.checkBoxGroupMatchingRegex.setDisabled(False)
        self._state_changed_group_matching_regex()

    def _refresh_encodings(self):
        encodings = tools.get_encodings()

        self.listWidgetEncoding.clear()

        if not encodings:
            return

        self.listWidgetEncoding.addItems(encodings)

    def group_by_size_on_disk(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        step = self.get_size_on_disk_step()
        group_singles = self.get_group_singles()

        for group in reversed(groups):
            grouper.group_same_size_on_disk(group, step, group_singles)

    def group_by_encoding(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        group_singles = self.get_group_singles()

        for group in reversed(groups):
            grouper.group_same_encoding(group, group_singles)

    def group_by_last_modified_time(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        step = self.get_last_modification_time_step()
        group_singles = self.get_group_singles()

        for group in reversed(groups):
            grouper.group_same_modification_time(group, step, group_singles)

    def group_by_storage_type(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        group_singles = self.get_group_singles()

        for group in groups:
            grouper.group_same_storage_type(group, group_singles)

    def group_by_feature_count(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        group_singles = self.get_group_singles()

        for group in reversed(groups):
            grouper.group_same_feature_count(group, group_singles)

    def group_by_name(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        ignore_groups = self.get_ignore_groups()
        group_singles = self.get_group_singles()

        if self.get_group_containing_substring():
            substring = self.get_group_substring()

            if not substring:
                return

            for group in reversed(groups):
                grouper.group_containing_substring(group, substring, ignore_groups, group_singles)

            return

        if self.get_group_matching_regex():
            regex = self.get_group_regex()

            if not regex:
                return

            for group in reversed(groups):
                grouper.group_by_name_matching_regex_patter(group, regex, ignore_groups, group_singles)

            return

        for group in reversed(groups):
            grouper.group_same_name(group, ignore_groups, group_singles)

    def group_same_geometry(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        group_singles = self.get_group_singles()
        include_geometries = self.get_geometries_to_group()

        for group in reversed(groups):
            grouper.group_same_geometry(group, include_geometries, group_singles)

    def group_by_filetype(self):
        groups = self.get_groups_to_group_values()

        if not groups:
            return

        for group in reversed(groups):
            grouper.group_same_filetype(group)

    def sort_by_geometry(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        geometry_order = self.get_geometry_order()

        for group in reversed(groups):
            tools.move_nodes_to_group(
                group,
                sorter.get_geometry_node_order_within_group(group, geometry_order)
            )

    def sort_by_name(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        reverse = self.get_alphabetical_reverse()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_alphabetical_node_order_within_group(group, reverse))

    def sort_by_file_type(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        file_extension_order = self.get_file_extension_order()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_file_extension_order(group, file_extension_order))

    def sort_by_position(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        from_ = self.get_position_from()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_node_order_by_position(group, from_))

    def sort_by_feature_count(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        reverse = self.get_feature_count_reverse()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_node_order_by_feature_count(group, reverse))

    def sort_by_storage_type(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        storage_type_order = self.get_storage_type_order()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_node_order_by_storage_type(group, storage_type_order))

    def sort_by_size_on_disk(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        reverse = self.get_size_on_disk_reverse()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_node_order_by_size_on_disk(group, reverse))

    def sort_by_last_modified(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        reverse = self.get_last_modified_reverse()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_node_order_by_last_modified(group, reverse))

    def sort_by_encoding(self):
        groups = self.get_groups_to_sort()

        if not groups:
            return

        encoding_order = self.get_encoding_order()

        for group in reversed(groups):
            tools.move_nodes_to_group(group, sorter.get_node_order_by_encoding(group, encoding_order))

    def get_feature_count_most_to_less(self) -> bool:
        return self.radioButtonMostToLess.isChecked()

    def get_position_to_sort_from(self):
        """-> Literal['left', 'right', 'bottom', 'top']"""
        if self.radioButtonPositionBottomToTop.isChecked():
            return "bottom"
        if self.radioButtonPositionTopToBottom.isChecked():
            return "top"
        if self.radioButtonPositionLeftToRight.isChecked():
            return "left"
        if self.radioButtonPositionRightToLeft.isChecked():
            return "right"

    def get_filetype_order(self):
        items = []
        model = self.listWidgetFiletypes.model()

        for i in range(model.rowCount()):
            items.append(self.listWidgetFiletypes.item(i).text())

        return items

    def set_combobox_items(self):
        for i in range(self.stackedWidgetSortPages.count()):
            self.comboBoxSort.addItem(self.commands[self.stackedWidgetSortPages.widget(i).objectName().replace('Sort', '')]["Name"])

    def change_page(self):
        for index, (key, values) in enumerate(self.commands.items()):
            if values['Name'] == self.comboBoxSort.currentText():
                if values['Refresh'] is not None:
                    values['Refresh']()
                    break
        self.stackedWidgetSortPages.setCurrentIndex(self.comboBoxSort.currentIndex())
        self.stackedWidgetGroupPages.setCurrentIndex(self.comboBoxSort.currentIndex())

    def _get_current_page(self) -> str:
        looked_for_key = None
        for index, (key, values) in enumerate(self.commands.items()):
            if values['Name'] == self.comboBoxSort.currentText():
                looked_for_key = key
                break
        return looked_for_key

    def sort_a(self):
        looked_for_key = self._get_current_page()

        if looked_for_key is None:
            return

        for index, (key, values) in enumerate(self.commands.items()):
            if values['Name'] == self.comboBoxSort.currentText():
                if values["Sort"] is not None:
                    self.labelStatus.setText("Sorting...")
                    values["Sort"]()
        self.labelStatus.setText("READY")

    def group_nodes(self):
        looked_for_key = self._get_current_page()

        if looked_for_key is None:
            return

        for index, (key, values) in enumerate(self.commands.items()):
            if values['Name'] == self.comboBoxSort.currentText():
                if values["GroupSameValues"] is not None:
                    self.labelStatus.setText("Grouping...")
                    values["GroupSameValues"]()
        self.labelStatus.setText("READY")

    def get_groups_to_sort(self) -> List[QgsLayerTreeGroup]:
        groups = []
        if self.radioButtonSortRootOnly.isChecked():
            groups = [tools.get_all_groups()[0]]
        if self.radioButtonOrderWithinGroups.isChecked():
            groups = tools.get_all_groups()
        if self.radioButtonSortOnlyWithinSelectedGroups.isChecked():
            groups = tools.get_selected_groups()
        if self.radioButtonExtractAndSortInRoot.isChecked():
            tools.delete_all_groups_and_move_nodes_to_root()
            groups = [tools.get_all_groups()[0]]

        return groups

    def get_groups_to_group_values(self) -> List[QgsLayerTreeGroup]:
        groups = []
        
        if self.radioButtonExtractAndGroupInRoot.isChecked():
            tools.delete_all_groups_and_move_nodes_to_root()
            groups = [tools.get_all_groups()[0]]
        if self.radioButtonGroupRootOnly.isChecked():
            groups = [tools.get_all_groups()[0]]
        if self.radioButtonGroupSelectedGroups.isChecked():
            groups = tools.get_selected_groups()
        if self.radioButtonGroupWithinAllGroups.isChecked():
            groups = tools.get_all_groups()

        return groups

    def set_default_listbox_geometries(self):
        self.listWidgetGeometry.clear()
        self.listWidgetGeometry.addItems(definitions.GEOMETRY_TYPES.values())

    def refresh_loaded_layers_storage_types(self):
        self.listWidgetStorageTypes.clear()
        self.listWidgetStorageTypes.addItems(tools.get_storage_types())

    def refresh_loaded_layers_extensions(self):
        self.listWidgetFiletypes.clear()
        self.listWidgetFiletypes.addItems(tools.get_loaded_layers_extensions())

    def get_alphabetical_reverse(self) -> bool:
        """True if reverse"""
        return self.radioButtonZA.isChecked()

    def get_geometry_order(self) -> List[str]:
        return [self.listWidgetGeometry.item(i).text().lower() for i in range(self.listWidgetGeometry.model().rowCount())]

    def get_storage_type_order(self) -> List[str]:
        return [self.listWidgetStorageTypes.item(i).text() for i in range(self.listWidgetStorageTypes.model().rowCount())]

    def get_file_extension_order(self) -> List[str]:
        return [self.listWidgetFiletypes.item(i).text() for i in range(self.listWidgetFiletypes.model().rowCount())]

    def get_position_from(self):
        """-> Literal['bottom', 'left', 'right', 'top']"""
        if self.radioButtonPositionBottomToTop.isChecked():
            return 'bottom'
        if self.radioButtonPositionLeftToRight.isChecked():
            return 'left'
        if self.radioButtonPositionRightToLeft.isChecked():
            return 'right'
        if self.radioButtonPositionTopToBottom.isChecked():
            return 'top'

    def get_feature_count_reverse(self) -> bool:
        return self.radioButtonLessToMost.isChecked()

    def get_size_on_disk_reverse(self) -> bool:
        return self.radioButtonSizeOnDiskDescending.isChecked()

    def get_last_modified_reverse(self) -> bool:
        return self.radioButtonNewerFirst.isChecked()

    def get_encoding_order(self) -> List[str]:
        return [self.listWidgetEncoding.item(i).text() for i in range(self.listWidgetEncoding.model().rowCount())]

    def get_ignore_groups(self) -> bool:
        return self.checkBoxIgnoreGroupNames.isChecked()

    def get_last_modification_time_step(self):
        """-> Literal['day', 'month', 'year']"""
        if self.radioButtonLastModifiedDay.isChecked():
            return 'day'
        if self.radioButtonLastModifiedMonth.isChecked():
            return 'month'
        if self.radioButtonLastModifiedYear.isChecked():
            return 'year'

    def get_size_on_disk_step(self) -> float:
        return self.doubleSpinBoxGroupSizeOnDiskStep.value()

    def get_group_singles(self) -> bool:
        return self.checkBoxGroupSingles.isChecked()

    def _state_changed_group_matching_regex(self, event=None):
        if self.checkBoxGroupMatchingRegex.isChecked():
            self.lineEditGroupMatchingRegex.setDisabled(False)
            return

        self.lineEditGroupMatchingRegex.setDisabled(True)

    def _state_changed_group_containing_substring(self, event=None):
        if self.checkBoxGroupContainingSubstring.isChecked():
            self.lineEditGroupContainingSubstring.setDisabled(False)
            return

        self.lineEditGroupContainingSubstring.setDisabled(True)

    def get_group_containing_substring(self) -> bool:
        return self.checkBoxGroupContainingSubstring.isChecked()

    def get_group_matching_regex(self) -> bool:
        return self.checkBoxGroupMatchingRegex.isChecked()

    def get_group_substring(self) -> str:
        return self.lineEditGroupContainingSubstring.text()

    def get_group_regex(self) -> str:
        return self.lineEditGroupMatchingRegex.text()

    def get_geometries_to_group(self) -> List[int]:
        included_geometries = []

        if self.checkBoxGroupIncludeRaster.isChecked():
            included_geometries.append(definitions.QGS_RASTER_LAYER_GEOMETRY_TYPE)
        if self.checkBoxGroupIncludePolygon.isChecked():
            included_geometries.append(definitions.QGS_POLYGON_GEOMETRY_TYPE)
        if self.checkBoxGroupIncludeLine.isChecked():
            included_geometries.append(definitions.QGS_LINE_GEOMETRY_TYPE)
        if self.checkBoxGroupIncludePoint.isChecked():
            included_geometries.append(definitions.QGS_POINT_GEOMETRY_TYPE)
        if self.checkBoxGroupIncludeGroups.isChecked():
            included_geometries.append(definitions.QGS_GROUP_GEOMETRY_TYPE)

        return included_geometries

# TODO: filetype shows as '' on sorter - should be memory
