import os

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
    Qgis,
    QgsGeometry,
    QgsMessageLog,
)
from qgis.utils import iface
from . import tools
from typing import Dict


file_copier_task = None


def toggle_all_layers_in_group_feature_count(group: QgsLayerTreeGroup, state: bool = True):
    for node in group.children():
        if tools.is_node_a_layer(node):
            tools.toggle_feature_count(node, state)


def reload_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if tools.is_node_a_layer(node):
            tools.reload_layer(node)

            QgsMessageLog.logMessage(
                f"Layer {node.layer().name()} reloaded",
                "Layer Tree Tools",
                Qgis.MessageLevel.Info
            )


def commit_changes_to_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if not tools.is_node_a_layer(node):
            continue
        layer = node.layer()

        tools.commit_changes_to_layer(layer)

        QgsMessageLog.logMessage(
            f"Changes committed to layer {layer.name()}",
            "Layer Tree Tools",
            Qgis.MessageLevel.Info
        )


def truncate_selected_layers():
    for layer in tools.get_selected_layers():
        if tools.is_layer_a_vector_layer(layer):
            tools.truncate_layer(layer)

            QgsMessageLog.logMessage(
                f"Layer {layer.name()} truncated",
                "Layer Tree Tools",
                Qgis.MessageLevel.Info
            )


def truncate_all_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if tools.is_node_a_layer(node):
            layer = node.layer()
            if tools.is_layer_a_vector_layer(layer):
                tools.truncate_layer(layer)


def run_file_copier(
        filepaths: Dict,
        destination_directory: str,
        all_in_single_directory: bool = True,
        use_layer_name: bool = False
):
    global file_copier_task
    file_copier_task = FileCopier(filepaths, destination_directory, all_in_single_directory, use_layer_name)
    tools.run_background_processing_task(file_copier_task)


def copy_layer_files_in_group_to_dir(group: QgsLayerTreeGroup, destination_directory: str, use_layer_name: bool = False):
    if not tools.is_node_a_group(group):
        return

    filepaths = {}
    for i, node in enumerate(group.children()):
        if tools.is_node_a_group(node):
            continue

        layer = node.layer()

        filepaths[i] = {
            'filepath': layer.dataProvider().dataSourceUri(),
            'name': node.name()
        }

    if filepaths:
        run_file_copier(filepaths, destination_directory, True, use_layer_name)


def export_selected_layers_to_dir(destination_directory: str, use_layer_name: bool = False):
    filepaths = {}
    for i, layer in enumerate(tools.get_selected_layers()):
        filepaths[i] = {
            'filepath': layer.dataProvider().dataSourceUri(),
            'name': layer.name()
        }

    if filepaths:
        run_file_copier(filepaths, destination_directory, True, use_layer_name)


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
            current[len(current)] = {
                'filepath': node.layer().dataProvider().dataSourceUri(),
                'name': node.name()
            }


def copy_layer_files_making_a_dir_tree(group: QgsLayerTreeGroup, destination_directory: str, use_layer_name: bool = False):
    if not tools.is_node_a_group(group):
        return

    tree = {}
    build_tree_dict(tree, group)

    run_file_copier(tree, destination_directory, False, use_layer_name)


class FileCopier(QgsTask):
    def __init__(
        self,
        filepaths: Dict,
        destination_directory: str,
        all_in_single_directory: bool = False,
        use_layer_name: bool = False
    ):
        super().__init__("Copying layer files to new directory")
        self.filepaths = filepaths
        self.destination_directory = destination_directory
        self.total = tools.get_nested_dictionary_total_value_count(self.filepaths)
        self.exported = 0
        self.check = True
        self.all_in_single_directory = all_in_single_directory
        self.use_layer_name = use_layer_name

    def run(self):
        self.setProgress(0)

        def export_files(current: Dict, current_dir: str):
            for key, value in current.items():
                if self.isCanceled():
                    return False

                if isinstance(value, dict):
                    if not (len(value) == 2 and 'filepath' in value.keys() and 'name' in value.keys()):
                        new_dir = current_dir

                        if not self.all_in_single_directory:
                            new_dir = os.path.join(current_dir, key)
                            os.makedirs(new_dir, exist_ok=True)

                        export_files(value, new_dir)
                        continue

                if not os.path.isfile(value['filepath']):
                    continue

                if not tools.copy_file_with_sidecar_files_to_destination(
                        value['filepath'],
                        current_dir + '/',
                        tools.sanitize_filename(value['name']) if self.use_layer_name else ""
                ):
                    self.check = False

                self.setProgress(self.exported / self.total * 100)

        export_files(self.filepaths, self.destination_directory)

        return self.check

    def finished(self, result):
        if result:
            iface.messageBar().pushMessage(
                "Layer Tree Tools",
                "Layer files successfully copied to new directory",
                Qgis.MessageLevel.Success
            )
            return
        iface.messageBar().pushMessage(
            "Layer Tree Tools",
            "Failed to copy layer files to new directory",
            Qgis.MessageLevel.Critical
        )


def vacuum_selected_layers():
    for layer in tools.get_selected_layers():
        result = tools.vacuum_layer_database(layer)

        if result == 1:
            QgsMessageLog.logMessage(
                f"Database vacuumed for layer {layer.name()}",
                "Layer Tree Tools",
                Qgis.MessageLevel.Info
            )
            return

        if result == 0:
            QgsMessageLog.logMessage(
                f"Database vacuum failed for layer {layer.name()}",
                "Layer Tree Tools",
                Qgis.MessageLevel.Critical
            )
            return
        

def vacuum_all_layers_in_group(group: QgsLayerTreeGroup):
    for node in group.children():
        if tools.is_node_a_layer(node):
            layer = node.layer()
            tools.vacuum_layer_database(layer)


def vacumm_all_layers():
    for layer in tools.get_layers():
        tools.vacuum_layer_database(layer)


def convert_selected_annotation_layer_to_memory_layers():
    selected_layers = tools.get_selected_layers()

    if not selected_layers:
        return

    selected_layer = selected_layers[0]

    if not tools.is_layer_an_annotation_layer(selected_layer):
        return

    polygons = []
    points = []
    lines = []

    for item in selected_layer.items():
        feature = selected_layer.items()[item]

        new_feature = QgsFeature()
        if feature.type() == 'polygon':
            geometry = feature.geometry().toPolygon()
            new_feature.setGeometry(geometry)
            polygons.append(new_feature)
            continue

        if feature.type() in ['point', 'marker']:
            geometry = QgsGeometry.fromPointXY(feature.geometry())
            new_feature.setGeometry(geometry)
            points.append(new_feature)
            continue

        if feature.type() == 'linestring':
            geometry = feature.geometry().curveToLine()
            new_feature.setGeometry(geometry)
            lines.append(new_feature)
            continue

    uri_polygons = f"multipolygon?crs={selected_layer.crs().authid()}"
    uri_points = f"point?crs={selected_layer.crs().authid()}"
    uri_lines = f"multilinestring?crs={selected_layer.crs().authid()}"

    memory_layer_polygons = QgsVectorLayer(uri_polygons, "Annotation polygons", "memory")
    memory_layer_points = QgsVectorLayer(uri_points, "Annotation points", "memory")
    memory_layer_lines = QgsVectorLayer(uri_lines, "Annotation lines", "memory")

    if polygons:
        memory_layer_polygons.dataProvider().addFeatures(polygons)
    if points:
        memory_layer_points.dataProvider().addFeatures(points)
    if lines:
        memory_layer_lines.dataProvider().addFeatures(lines)

    QgsProject.instance().addMapLayer(memory_layer_polygons)
    QgsProject.instance().addMapLayer(memory_layer_points)
    QgsProject.instance().addMapLayer(memory_layer_lines)

    iface.messageBar().pushMessage(
        "Layer Tree Tools",
        "Annotation layer successfully converted to memory layers",
        Qgis.MessageLevel.Success
    )
