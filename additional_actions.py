import os
from qgis.utils import iface

from qgis.core import (
    QgsProject,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsRasterLayer,
    QgsLayerTreeNode,
    QgsMapLayer,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsFeature,
    QgsWkbTypes,
    QgsField,
    NULL,
    QgsApplication,
    QgsTask,
    Qgis
)
from . import tools
from typing import List


def toggle_all_layers_in_group_feature_count(group: QgsLayerTreeGroup, state: bool = True):
    for node in group.children():
        if tools.is_node_a_layer(node):
            tools.toggle_feature_count(node, state)


def reload_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if tools.is_node_a_layer(node):
            tools.reload_layer(node)


def commit_changes_to_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if not tools.is_node_a_layer(node):
            continue
        layer = node.layer()
        tools.commit_changes_to_layer(layer)


def truncate_selected_layers():
    for layer in tools.get_selected_layers():
        if tools.is_layer_a_vector_layer(layer):
            tools.truncate_layer(layer)


def truncate_all_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if tools.is_node_a_layer(node):
            layer = node.layer()
            if tools.is_layer_a_vector_layer(layer):
                tools.truncate_layer(layer)


def run_file_exporter(filepaths: List[str], destination_directory: str):
    task = FileExporter(filepaths, destination_directory)
    tools.run_background_processing_task(task)


def export_layers_in_group_to_dir(group: QgsLayerTreeGroup, destination_directory: str):
    if not tools.is_node_a_group(group):
        return

    filepaths = []
    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        layer = node.layer()

        filepaths.append(layer.dataProvider().dataSourceUri())

    if filepaths:
        run_file_exporter(filepaths, destination_directory)


def export_selected_layers_to_dir(destination_directory: str):
    filepaths = []
    for layer in tools.get_selected_layers():
        filepaths.append(layer.dataProvider().dataSourceUri())

    if filepaths:
        run_file_exporter(filepaths, destination_directory)


class FileExporter(QgsTask):
    def __init__(self, filepaths: List[str], destination_directory: str):
        super().__init__("Exporting layers to new directory")
        self.filepaths = filepaths
        self.destination_directory = destination_directory
        self.processing_done = False

    def run(self):
        check = True

        self.setProgress(0.01)
        total = len(self.filepaths)

        for i, filepath in enumerate(self.filepaths):
            if self.isCanceled():
                return False

            if not os.path.isfile(filepath):
                return

            if not tools.copy_file_with_sidecar_files_to_destination(filepath, self.destination_directory):
                check = False

            self.setProgress(i / total * 100)

        self.finished(check)

        return check

    def finished(self, result):
        if self.processing_done:
            return

        self.processing_done = True
