# -*- coding: utf-8 -*-
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from typing import Dict, List

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'snapshot_reporter.ui'))


class SnapshotReporter(QtWidgets.QDialog, FORM_CLASS):
    TREEVIEW_ITEMS = {
        'Name': 0,
        'Provider': 1,
        'Datasource': 2
    }

    def __init__(self, report: List[Dict], parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Snapshot load report - failed layers')
        self.setModal(True)

        self.report = report

        self.treeview_model = self._get_treeview_model(self)
        self.treeViewFailedToLoad.setModel(self.treeview_model)

        self._populate_treeview()

    def _populate_treeview(self):
        for row in self.report:
            self.treeview_model.insertRow(0)
            self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Name']), row['Name'])
            self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Provider']), row['Provider'])
            self.treeview_model.setData(self.treeview_model.index(0, self.TREEVIEW_ITEMS['Datasource']), row['Datasource'])

    def _get_treeview_model(self, parent) -> QStandardItemModel:
        model = QStandardItemModel(0, len(self.TREEVIEW_ITEMS), parent)
        model.setHeaderData(self.TREEVIEW_ITEMS['Name'], Qt.Horizontal, "Name")
        model.setHeaderData(self.TREEVIEW_ITEMS['Provider'], Qt.Horizontal, "Provider")
        model.setHeaderData(self.TREEVIEW_ITEMS['Datasource'], Qt.Horizontal, "Datasource")

        return model
