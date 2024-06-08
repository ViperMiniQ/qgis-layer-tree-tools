# -*- coding: utf-8 -*-
import os
from pathlib import Path
import json

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from . import snapshooter

from . import tools

from qgis.core import (
    QgsProject,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsRasterLayer,
    QgsLayerTreeNode,
    QgsMapLayer,
    QgsVectorLayer,
    QgsFeatureRequest
)

from typing import Dict
import datetime

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from . import snapshot_name_dialog
from .snapshotreporter import SnapshotReporter


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'snapshooter_dialog_base.ui'))


SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), 'Snapshots/')
Path(SNAPSHOT_DIR).mkdir(parents=True, exist_ok=True)


SETTINGS_FILEPATH = os.path.join(os.path.dirname(__file__), 'settings.json')
DEFAULT_SETTINGS = {
    "snapshots_directory": Path(os.path.join(os.path.dirname(__file__), 'Snapshots')).as_posix() + '/',
    "expand_group_double_click": False
}
CURRENT_SETTINGS = None

if not os.path.exists(SETTINGS_FILEPATH):
    CURRENT_SETTINGS = DEFAULT_SETTINGS
    with open(SETTINGS_FILEPATH, 'w') as f:
        json.dump(CURRENT_SETTINGS, f)


def load_settings():
    global CURRENT_SETTINGS
    with open(SETTINGS_FILEPATH, 'r') as f:
        CURRENT_SETTINGS = json.load(f)
        if not CURRENT_SETTINGS['snapshots_directory'].endswith('/'):
            CURRENT_SETTINGS['snapshots_directory'] += '/'

        snapshooter.Snapshooter.SNAPSHOT_DIR = CURRENT_SETTINGS['snapshots_directory']

def write_settings():
    with open(SETTINGS_FILEPATH, 'w') as f:
        json.dump(CURRENT_SETTINGS, f)


load_settings()


snapshooter_task = None


class snapshooterDialog(QtWidgets.QDialog, FORM_CLASS):
    TREEVIEW_ITEMS = {
        'ID': 0,
        'Name': 1,
        'Time': 2,
        'Rasters': 3,
        'Vector layers': 4,
        'Vector layers in memory': 5
    }

    def __init__(self, parent=None):
        super().__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)

        self.setModal(True)

        self.treeview_model = self._get_treeview_model(self)
        self.treeViewSnapshots.setModel(self.treeview_model)
        self.treeViewSnapshots.hideColumn(self.TREEVIEW_ITEMS['ID'])

        self.pushButtonBrowseSnapshotDirectory.clicked.connect(self.browse_snapshot_directory)

        self.pushButtonCreateSnapshot.clicked.connect(self.create_snapshot)
        self.pushButtonLoadSelectedSnapshot.clicked.connect(self._load_selected_snapshot)
        self.pushButtonRefreshSnapshotsDetails.clicked.connect(self._reload_all_snapshots_details)

        self.checkBoxIncludeVectorLayers.stateChanged.connect(self.state_changed_include_vector_layers)

        self.pushButtonDeleteSelectedSnapshot.clicked.connect(self._delete_selected_snapshot)

        self.state_changed_include_vector_layers()

        self.refresh_snapshot_directory()

    def refresh_snapshot_directory(self):
        self.lineEditSnapshotDirectory.setText(CURRENT_SETTINGS['snapshots_directory'])
        self._reload_all_snapshots_details()

    def browse_snapshot_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory for snapshots', CURRENT_SETTINGS['snapshots_directory'])

        if not directory or not os.path.isdir(directory):
            return

        directory = Path(directory).as_posix() + '/'

        self.lineEditSnapshotDirectory.setText(directory)

        CURRENT_SETTINGS['snapshots_directory'] = directory

        write_settings()
        load_settings()

        self.refresh_snapshot_directory()

    def _get_selected_treeview_row_data(self) -> Dict:
        selected_indexes = self.treeViewSnapshots.selectedIndexes()

        if not selected_indexes:
            return {}

        row_index = selected_indexes[0].row()

        selected_row_data = []
        for column in range(self.treeview_model.columnCount()):
            selected_row_data.append(
                self.treeview_model.data(
                    self.treeview_model.index(row_index, column)))

        return dict(zip(list(self.TREEVIEW_ITEMS.keys()), selected_row_data))

    def _insert_treeview_row_data(self, id_: int, name: str, at_time: datetime.datetime, include_rasters: bool,
                                  include_vector_layers: bool, vector_layers_in_memory: bool):
        self.treeview_model.insertRow(0)
        self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['ID']), id_)
        self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Name']), name)
        self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Time']), at_time.strftime('%Y-%m-%d %H:%M:%S'))
        self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Rasters']), str(include_rasters))
        self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Vector layers']),
                                    str(include_vector_layers))
        self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Vector layers in memory']),
                                    str(vector_layers_in_memory))

        self._adjust_treeview_columns_text_size()

    def _adjust_treeview_columns_text_size(self):
        for i in range(len(self.TREEVIEW_ITEMS)):
            self.treeViewSnapshots.resizeColumnToContents(i)

    def _get_treeview_model(self, parent) -> QStandardItemModel:
        model = QStandardItemModel(0, len(self.TREEVIEW_ITEMS), parent)
        model.setHeaderData(self.TREEVIEW_ITEMS['ID'], Qt.Horizontal, "ID")
        model.setHeaderData(self.TREEVIEW_ITEMS['Name'], Qt.Horizontal, "Name")
        model.setHeaderData(self.TREEVIEW_ITEMS['Time'], Qt.Horizontal, "Time")
        model.setHeaderData(self.TREEVIEW_ITEMS['Rasters'], Qt.Horizontal, "Rasters")
        model.setHeaderData(self.TREEVIEW_ITEMS['Vector layers'], Qt.Horizontal, "Vector layers")
        model.setHeaderData(self.TREEVIEW_ITEMS['Vector layers in memory'], Qt.Horizontal, "Vector layers in memory")

        return model

    def _reload_all_snapshots_details(self):
        self.treeview_model.removeRows(0, self.treeview_model.rowCount())

        snapshots_details = snapshooter.Snapshooter.get_all_snapshots_details()

        for details in snapshots_details:
            self._insert_treeview_row_data(
                name=details['name'],
                at_time=details['at_time'],
                include_rasters=details['include_rasters'],
                include_vector_layers=details['include_vector_layers'],
                vector_layers_in_memory=details['vector_layers_in_memory'],
                id_=details['id']
            )

    def create_snapshot(self):

        dlg = snapshot_name_dialog.SnapshootNameDialog()
        res = dlg.exec()

        if not res == QtWidgets.QDialog.Accepted:
            return

        self.setDisabled(True)

        name = dlg.name

        include_rasters = self.checkBoxIncludeRasters.isChecked()
        include_vector_layers = self.checkBoxIncludeVectorLayers.isChecked()
        vector_layers_in_memory = self.checkBoxVectorLayersInMemory.isChecked()

        starting_point = None
        if self.radioButtonStartingPointRoot.isChecked():
            starting_point = tools.get_layer_tree()
        if self.radioButtonStartingPointSelectedGroup.isChecked():
            starting_point = tools.get_selected_groups()
            if not len(starting_point) == 1:
                tools.show_dialog_error_message('No group selected, please select a single group.')
                return
            starting_point = starting_point[0]

        global snapshooter_task
        snapshooter_task = snapshooter.Snapshooter(
            name,
            include_rasters,
            include_vector_layers,
            vector_layers_in_memory,
            starting_point,
            self._insert_new_snapshot
        )

        tools.run_background_processing_task(
            snapshooter_task
        )

    def _insert_new_snapshot(self, snapshot: Dict):
        self.setDisabled(False)
        if not snapshot:
            tools.show_dialog_error_message('Failed creating snapshot.')
            return

        self._insert_treeview_row_data(
            name=snapshot['name'],
            at_time=snapshot['at_time'],
            include_rasters=snapshot['include_rasters'],
            include_vector_layers=snapshot['include_vector_layers'],
            vector_layers_in_memory=snapshot['vector_layers_in_memory'],
            id_=snapshot['id']
        )

    def _load_snapshot_layers(self, group: QgsLayerTreeGroup, current, report, symbology=None):
        for key, value in current.items():  # in reverse order? should be OK
            if not isinstance(value, dict):
                continue

            state = key[0]
            if not state.isnumeric():
                state = True
            else:
                state = bool(int(state))

            if 'filepath' not in value.keys():
                if '(' not in key or ')' not in key:
                    continue
                group_name = key[key.find("(") + 1:key.find(")")]

                new_group = tools.create_group(group, group_name)
                tools.set_node_visibility(new_group, state)

                self._load_snapshot_layers(new_group, value, report, symbology)
                continue

            try:
                layer = None
                if value['type'] == 'QgsRasterLayer':
                    layer = tools.create_raster_layer(value['filepath'], value['name'], value['provider'])
                if value['type'] == 'QgsVectorLayer':
                    layer = tools.create_vector_layer(
                        value['filepath'],
                        value['name'],
                        value['provider'] if not value['attributes'] else 'memory')
                if layer is None:
                    report.append(
                        {'Name': value['name'], 'Provider': value['provider'], 'Datasource': value['filepath']})
                    continue

                if value['attributes']:
                    attrs = [tools.convert_dict_to_qgis_field(attr) for attr in value['attributes']]
                    tools.set_layer_attributes(layer, attrs)
                if value['features']:
                    if not tools.load_features_to_layer(layer, value['features']):
                        report.append({'Name': value['name'], 'Provider': value['provider'], 'Datasource': value['filepath']})
                        continue

                map_layer = QgsProject.instance().addMapLayer(layer, False)

                if 'crs' in value.keys():
                    tools.set_layer_crs_from_wkt(map_layer, value['crs'])

                group.addLayer(map_layer)

                if symbology is not None:
                    if key in symbology.keys():
                        result, qdom = tools.string_to_qdom(str(symbology[key]))

                        tools.set_layer_named_style_from_qdom(map_layer, qdom)

                tools.set_node_visibility(map_layer, state)

            except Exception:
                report.append({'Name': value['name'], 'Provider': value['provider'], 'Datasource': value['filepath']})

    def _load_selected_snapshot(self):
        selected_row_data = self._get_selected_treeview_row_data()

        if not selected_row_data:
            return

        details, snapshot, symbology = snapshooter.Snapshooter.get_snapshot(selected_row_data['ID'])

        if snapshot is None:
            return  # TODO: throw error

        starting_group = tools.get_layer_tree()

        if self.radioButtonSnapshotToNewGroup.isChecked():
            starting_group = tools.create_group(starting_group, f'snapshot {details["name"]}')
        else:
            tools.clear_layer_tree()

        report = []

        self._load_snapshot_layers(starting_group, snapshot, report, symbology)

        if report:
            dlg_report = SnapshotReporter(report)
            res = dlg_report.exec()

            if res:
                pass

    def state_changed_include_vector_layers(self, event=None):
        if self.checkBoxIncludeVectorLayers.isChecked():
            self.checkBoxVectorLayersInMemory.setDisabled(False)
            return
        self.checkBoxVectorLayersInMemory.setDisabled(True)

    def _delete_selected_snapshot(self):
        selected_row_data = self._get_selected_treeview_row_data()

        if not selected_row_data:
            return

        if not tools.show_yes_no_message(f'Are you sure you want to delete selected snapshot? \n'
                                                f'{selected_row_data["Name"]} {selected_row_data["Time"]}'):
            return

        if not snapshooter.Snapshooter.delete_snapshot(selected_row_data['ID']):
            tools.show_dialog_error_message(f'Could not delete selected snapshot. \n'
                                                   f'{selected_row_data["Name"]} {selected_row_data["Time"]}')
            return

        self._reload_all_snapshots_details()
