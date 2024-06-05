from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer, QgsRasterLayer, QgsLayerTreeNode
from . import definitions
from . import tools
from typing import List
import re


def get_alphabetical_node_order_within_group(group: QgsLayerTreeGroup, reverse: bool = False) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")
    return sorted(group.children(), key=lambda x: x.name(), reverse=reverse)


def get_natural_order_within_group(group: QgsLayerTreeGroup, reverse: bool = False) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    re_order = re.compile(r'(\d+)')

    group_children = list(group.children())
    group_children.sort(key=lambda x: [int(y) if y.isdigit() else y for y in re.split(re_order, x.name())],
                        reverse=reverse)
    return group_children


def get_geometry_node_order_within_group(group: QgsLayerTreeGroup, geometry_order: List[str]) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    geometries = {}
    for key in definitions.GEOMETRY_TYPES:
        geometries[key] = []
    unknown = []

    for node in group.children():
        if isinstance(node, QgsLayerTreeLayer):
            layer = node.layer()

            if tools.is_layer_a_raster(layer):
                geometries[definitions.QGS_RASTER_LAYER_GEOMETRY_TYPE].append(node)
                continue

            layer_geometry = tools.get_layer_geometry(layer)

            if layer_geometry not in geometries:
                geometries[layer_geometry] = [node]
                continue

            geometries[layer_geometry].append(node)
            continue

        if isinstance(node, QgsLayerTreeGroup):
            if definitions.QGS_GROUP_GEOMETRY_TYPE not in geometries:
                geometries[definitions.QGS_GROUP_GEOMETRY_TYPE] = [node]
                continue

            geometries[definitions.QGS_GROUP_GEOMETRY_TYPE].append(node)
            continue

        unknown.append(node)

    ordered_nodes = []

    for geometry in geometry_order:
        for key, value in definitions.GEOMETRY_TYPES.items():
            if geometry == value:
                ordered_nodes += geometries.pop(key)

    for remaining_key in geometries:
        ordered_nodes += geometries.pop(remaining_key)

    ordered_nodes += unknown

    return ordered_nodes


def get_file_extension_order(group: QgsLayerTreeGroup, file_extension_order: List[str]) -> List[QgsLayerTreeNode]:
    """get sorted order by file extension. To include temporary layers, add 'memory' to the list of extensions."""
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    nodes_by_extension = {x: [] for x in file_extension_order}
    groups = []

    for node in group.children():
        if tools.is_node_a_group(node):
            groups.append(node)
            continue

        layer = node.layer()
        filename, file_extension = tools.get_layer_filename_and_filetype(layer)

        if filename.startswith('memory'):
            if 'memory' not in nodes_by_extension:
                nodes_by_extension['memory'] = [node]
                continue
            nodes_by_extension['memory'].append(node)

        if file_extension not in nodes_by_extension:
            nodes_by_extension[file_extension] = [node]
            continue

        nodes_by_extension[file_extension].append(node)

    ordered_nodes = []

    for extension in file_extension_order:
        ordered_nodes += nodes_by_extension[extension]

    return ordered_nodes


def get_node_order_by_position(group: QgsLayerTreeGroup, from_: str) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    horizontal = ["left", "right"]
    vertical = ["top", "bottom"]

    if from_ not in horizontal + vertical:
        raise ValueError(f"'from_' possible values are: {horizontal + vertical}")

    nodes = []
    no_extent_nodes = []

    for node in group.children():
        if not isinstance(node, QgsLayerTreeLayer):
            no_extent_nodes.append(node)
            continue

        try:
            node.layer().extent()
        except AttributeError:
            no_extent_nodes.append(node)
            continue

        nodes.append(node)

    if from_ == 'left':
        nodes = sorted(nodes, key=lambda x: x.layer().extent().xMinimum(), reverse=False)
    if from_ == 'right':
        nodes = sorted(nodes, key=lambda x: x.layer().extent().xMaximum(), reverse=True)
    if from_ == 'top':
        nodes = sorted(nodes, key=lambda x: x.layer().extent().yMaximum(), reverse=True)
    if from_ == 'bottom':
        nodes = sorted(nodes, key=lambda x: x.layer().extent().yMinimum(), reverse=False)

    nodes += no_extent_nodes

    return nodes


def get_node_order_by_feature_count(group: QgsLayerTreeGroup, reverse: bool = False) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    nodes = []
    no_feature_nodes = []
    for node in group.children():
        if not isinstance(node, QgsLayerTreeLayer):
            no_feature_nodes.append(node)
            continue

        layer = node.layer()
        try:
            layer.featureCount()
        except AttributeError:
            no_feature_nodes.append(node)
            continue

        nodes.append(node)

    sorted_nodes = sorted(nodes, key=lambda x: x.layer().featureCount(), reverse=reverse)
    sorted_nodes += no_feature_nodes

    return sorted_nodes


def get_node_order_by_storage_type(group: QgsLayerTreeGroup, storage_type_order: List[str]) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    nodes = {x: [] for x in storage_type_order}
    no_storage_type_nodes = []

    for node in group.children():
        if not isinstance(node, QgsLayerTreeLayer):
            no_storage_type_nodes.append(node)
            continue

        layer = node.layer()

        if tools.is_layer_a_vector_layer(layer):
            storage_type = layer.storageType()
            if storage_type not in nodes:
                nodes[storage_type] = [node]
                continue
            nodes[storage_type].append(node)

            continue

        no_storage_type_nodes.append(node)

    sorted_nodes = []
    for storage_type in storage_type_order:
        sorted_nodes += nodes[storage_type]

    sorted_nodes += no_storage_type_nodes

    return sorted_nodes


def get_node_order_by_last_modified(group: QgsLayerTreeGroup, reverse: bool = False) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    groups = []
    nodes = []
    no_timestamp_nodes = []

    for node in group.children():
        if tools.is_node_a_group(node):
            groups.append(group)
            continue

        node_filepath = tools.get_node_filepath(node)

        if not node_filepath:
            no_timestamp_nodes.append(node)
            continue

        nodes.append(node)

    sorted_nodes = sorted(nodes, key=lambda x: tools.get_file_last_modified(tools.get_node_filepath(x)), 
                          reverse=reverse)
    
    sorted_nodes += no_timestamp_nodes  # + groups

    return sorted_nodes


def get_node_order_by_size_on_disk(group: QgsLayerTreeGroup, reverse: bool = False) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    groups = []
    nodes = []
    no_size_nodes = []

    for node in group.children():
        if tools.is_node_a_group(node):
            groups.append(group)
            continue

        filesize = tools.get_file_size_on_disk(tools.get_node_filepath(node))

        if filesize == -1:
            no_size_nodes.append(node)
            continue

        nodes.append(node)

    sorted_nodes = sorted(nodes, key=lambda x: tools.get_file_size_on_disk(tools.get_node_filepath(x)),
                          reverse=reverse)

    sorted_nodes += no_size_nodes  # + groups

    return sorted_nodes


def get_node_order_by_encoding(group: QgsLayerTreeGroup, encoding_order: List[str]) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    groups = []
    file_encodings = {}
    unknown = []

    for encoding in encoding_order:
        file_encodings[encoding] = []

    for node in group.children():
        if isinstance(node, QgsLayerTreeGroup):
            groups.append(node)

        if isinstance(node, QgsLayerTreeLayer):
            layer = node.layer()

            if tools.is_layer_a_raster(layer):
                continue

            encoding = tools.get_layer_encoding(layer)

            if encoding not in file_encodings.keys():
                file_encodings[encoding] = [node]
                continue

            file_encodings[encoding].append(node)
            continue

        unknown.append(node)

    sorted_nodes = []
    for encoding in encoding_order:
        sorted_nodes += file_encodings[encoding]

    sorted_nodes += unknown

    return sorted_nodes


def get_node_order_by_crs(group: QgsLayerTreeGroup, method: str, crs_order: List[str]) -> List[QgsLayerTreeNode]:
    if not isinstance(group, QgsLayerTreeGroup):
        raise ValueError(f"group: {group} not QgsLayerTreeGroup instance.")

    groups = []
    crs = {}
    unknown = []

    for crs_ in crs_order:
        crs[crs_] = []

    for node in group.children():
        if isinstance(node, QgsLayerTreeGroup):
            groups.append(node)
            continue

        if isinstance(node, QgsLayerTreeLayer):
            layer = node.layer()

            layer_crs = tools.get_layer_crs(layer, method)

            if layer_crs not in crs.keys():
                crs[layer_crs] = [node]
                continue

            crs[layer_crs].append(node)
            continue

        unknown.append(node)

    sorted_nodes = []
    for crs_ in crs_order:
        sorted_nodes += crs[crs_]

    sorted_nodes += unknown + groups

    return sorted_nodes
