from qgis.core import (
    QgsLayerTreeNode,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsRasterLayer
)

from . import tools

from . import definitions
from typing import Dict, List

import re


# TODO: make a group for unique values?


def group_same_name(group: QgsLayerTreeGroup, ignore_groups: bool = False, group_single: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    nodes: Dict[str, List[QgsLayerTreeNode]] = {}

    for node in group.children():
        if ignore_groups and tools.is_node_a_group(node):
            continue

        name = node.name()
        if name in nodes.keys():
            nodes[name].append(name)
            continue

        nodes[name] = [node]

    for name, values in nodes.items():
        if len(values) <= 1 and not group_single:
            continue
        tools.move_nodes_to_group(group=tools.create_group(group, name), nodes=values)

    return True


def group_containing_substring(group: QgsLayerTreeGroup, substring: str, ignore_groups: bool = False, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    nodes = []

    for node in group.children():
        if ignore_groups and tools.is_node_a_group(node):
            continue

        if substring in node.name():
            nodes.append(node)

    if not group_singles and len(nodes) <= 1:
        return False

    tools.move_nodes_to_group(group=tools.create_group(group, substring), nodes=nodes)
    return True


def group_same_geometry(group: QgsLayerTreeGroup, include_geometries: List = None, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values: Dict[int, List[QgsLayerTreeNode]] = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            if definitions.QGS_GROUP_GEOMETRY_TYPE not in same_values:
                same_values[definitions.QGS_GROUP_GEOMETRY_TYPE] = []
            same_values[definitions.QGS_GROUP_GEOMETRY_TYPE].append(node)
            continue

        if tools.is_node_a_layer(node):
            layer = node.layer()

            layer_geometry = tools.get_layer_geometry(layer)

            if layer_geometry not in same_values.keys():
                same_values[layer_geometry] = []
                
            same_values[layer_geometry].append(node)

    for name, nodes in same_values.items():
        if not nodes:
            continue
        if len(nodes) <= 1 and not group_singles:
            continue
        if name not in include_geometries:
            continue
        new_group = tools.create_group(group, definitions.GEOMETRY_TYPES[name])
        tools.move_nodes_to_group(new_group, nodes)

    return True


def group_same_filetype(group: QgsLayerTreeGroup, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        if not tools.is_node_a_layer(node):
            continue

        layer = node.layer()
        filename, file_extensions = tools.get_layer_filename_and_filetype(layer)

        if filename.startswith('memory'):
            if 'memory' not in same_values.keys():
                same_values['memory'] = []
            same_values['memory'].append(node)
            continue

        if file_extensions not in same_values.keys():
            same_values[file_extensions] = []

        same_values[file_extensions].append(node)

    for name, values in same_values.items():
        if len(values) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, name), values)

    return True


def group_same_position(group: QgsLayerTreeGroup, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        if tools.is_node_a_layer(node):
            layer = node.layer()

            value = f"{layer.extent().xMinimum()}, {layer.extent().yMinimum()}, {layer.extent().xMaximum()}, {layer.extent().yMaximum()}"

            if value not in same_values.keys():
                same_values[value] = [node]
                continue

            same_values[value].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)


def group_same_feature_count(group: QgsLayerTreeGroup, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        if tools.is_node_a_layer(node):
            layer = node.layer()
            if not tools.is_layer_a_vector_layer(layer):
                continue

            count = layer.featureCount()

            if count not in same_values.keys():
                same_values[count] = [node]
                continue

            same_values[count].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)

    return True


def group_same_storage_type(group: QgsLayerTreeGroup, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        if tools.is_node_a_layer(node):
            layer = node.layer()

            if not tools.is_layer_a_vector_layer(layer):
                continue

            storage_type = tools.get_layer_storage_type(layer)

            if storage_type not in same_values.keys():
                same_values[storage_type] = [node]
                continue

            same_values[storage_type].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)

    return True


def group_same_modification_time(group: QgsLayerTreeGroup,
                                 step, group_singles: bool = False) -> bool:
    """step: Literal['day', 'month', 'year']"""
    if not tools.is_node_a_group(group):
        return False

    supported_steps = {
        'day': {
            'step': '%d',
            'format': '%Y-%m-%d'
        },
        'month': {
            'step': '%m',
            'format': '%Y-%m'
        },
        'year': {
            'step': '%Y',
            'format': '%Y'
        }
    }

    if step not in supported_steps.keys():
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        filepath = tools.get_node_filepath(node)

        modification_time = tools.get_file_last_modified(filepath)

        if modification_time == -1:
            modification_time_format = 'None'
        else:
            modification_time_format = tools.get_seconds_since_epoch_in_format(
                modification_time, supported_steps[step]['format']
            )

        if modification_time_format not in same_values.keys():
            same_values[modification_time_format] = [node]
            continue

        same_values[modification_time_format].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)

    return True


def group_same_encoding(group: QgsLayerTreeGroup, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        if tools.is_node_a_layer(node):
            layer = node.layer()

            if not tools.is_layer_a_vector_layer(layer):
                continue

            encoding = tools.get_layer_encoding(layer)

            if not encoding:
                encoding = 'None'

            if encoding not in same_values.keys():
                same_values[encoding] = [node]
                continue

            same_values[encoding].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)

    return True


def group_same_size_on_disk(group: QgsLayerTreeGroup, step: float, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        filepath = tools.get_node_filepath(node)

        if not filepath or filepath.startswith('memory'):
            continue

        filesize_bytes = tools.get_file_size_on_disk(filepath)

        filesize_megabytes = tools.translate_byte_size_to_megabyte_size(filesize_bytes)

        nearest_step_index = filesize_megabytes // step if step else -1

        nearest_step = f"{nearest_step_index * step} - {(nearest_step_index + 1) * step}" if not nearest_step_index == -1 else filesize_megabytes
        if nearest_step not in same_values.keys():
            same_values[nearest_step] = [node]
            continue

        same_values[nearest_step].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)

    return True


def group_by_name_matching_regex_patter(group: QgsLayerTreeGroup, regex: str, ignore_groups: bool, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    nodes = []

    for node in group.children():
        if ignore_groups and tools.is_node_a_group(node):
            continue

        if re.match(regex, node.name()) is not None:
            nodes.append(node)

    if len(nodes) <= 1 and not group_singles:
        return True

    tools.move_nodes_to_group(tools.create_group(group, regex), nodes)

    return True


def group_same_crs(group: QgsLayerTreeGroup, method: str, group_singles: bool = False) -> bool:
    if not tools.is_node_a_group(group):
        return False

    same_values = {}

    for node in group.children():
        if tools.is_node_a_group(node):
            continue

        if tools.is_node_a_layer(node):
            layer = node.layer()

            crs = tools.get_layer_crs(layer, method)

            if crs is None:
                crs = 'None'

            if crs not in same_values.keys():
                same_values[crs] = [node]
                continue

            same_values[crs].append(node)

    for key, nodes in same_values.items():
        if len(nodes) <= 1 and not group_singles:
            continue
        tools.move_nodes_to_group(tools.create_group(group, key), nodes)

    return True
