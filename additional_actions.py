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
    QgsTask
)
from . import tools


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
