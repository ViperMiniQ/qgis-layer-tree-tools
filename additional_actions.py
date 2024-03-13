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
from typing import List, Dict


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


def run_file_exporter(filepaths: Dict, destination_directory: str, all_in_single_directory: bool = True):
    task = FileExporter(filepaths, destination_directory, all_in_single_directory)
    tools.run_background_processing_task(task)


def export_layers_in_group_to_dir(group: QgsLayerTreeGroup, destination_directory: str):
    if not tools.is_node_a_group(group):
        return

    filepaths = {}
    for i, node in enumerate(group.children()):
        if tools.is_node_a_group(node):
            continue

        layer = node.layer()

        filepaths[i] = layer.dataProvider().dataSourceUri()

    if filepaths:
        run_file_exporter(filepaths, destination_directory)


def export_selected_layers_to_dir(destination_directory: str):
    filepaths = {}
    for i, layer in enumerate(tools.get_selected_layers()):
        filepaths[i] = layer.dataProvider().dataSourceUri()

    if filepaths:
        run_file_exporter(filepaths, destination_directory)


def build_tree_dict(current, root=None):
    if root is None:
        return

    for node in root.children():
        if tools.is_node_a_group(node):
            key = tools.sanitize_filename(node.name())

            i = 0
            while key in current.keys():
                key = f"{key}{i}"

            current[key] = {}
            build_tree_dict(current[key], node)
            continue

        if tools.is_node_a_layer(node):
            current[len(current)] = node.layer().dataProvider().dataSourceUri()


def export_layers_in_order_making_a_dir_tree(group: QgsLayerTreeGroup, destination_directory: str):
    if not tools.is_node_a_group(group):
        return

    tree = {}
    build_tree_dict(tree, group)

    run_file_exporter(tree, destination_directory, False)


class FileExporter(QgsTask):
    def __init__(self, filepaths: Dict, destination_directory: str, all_in_single_directory: bool = False):
        super().__init__("Exporting layers to new directory")
        self.filepaths = filepaths
        self.destination_directory = destination_directory
        self.processing_done = False
        self.total = tools.get_nested_dictionary_total_value_count(self.filepaths)
        self.exported = 0
        self.check = True
        self.all_in_single_directory = all_in_single_directory

    def run(self):
        self.setProgress(0)

        def export_files(current: Dict, current_dir: str):
            for key, value in current.items():
                if self.isCanceled():
                    return False

                if isinstance(value, dict):
                    new_dir = current_dir
                    if not self.all_in_single_directory:
                        new_dir = os.path.join(current_dir, key)
                        os.makedirs(new_dir, exist_ok=True)
                    export_files(value, new_dir)
                    continue

                if not os.path.isfile(value):
                    continue

                if not tools.copy_file_with_sidecar_files_to_destination(value, current_dir + '/'):
                    self.check = False

                self.setProgress(self.exported / self.total * 100)

        export_files(self.filepaths, self.destination_directory)

        self.finished(self.check)

        return self.check

    def finished(self, result):
        if self.processing_done:
            return

        self.processing_done = True
