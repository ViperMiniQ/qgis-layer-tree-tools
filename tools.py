import os.path
from typing import List, Dict, Tuple
from datetime import datetime
from pathlib import Path

from . import definitions

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
    QgsFileUtils,
    QgsProviderRegistry
)

try:
    from qgis.core import QgsAbstractDatabaseProviderConnection  # Added in version 3.10.
    qgs_abstract_database_provider_connection = True
except ImportError:
    qgs_abstract_database_provider_connection = False

try:
    from qgis.core import QgsAnnotationLayer  # Added in version 3.16.
    qgs_annotation_layer = True
except ImportError:
    qgs_annotation_layer = False

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtXml import QDomDocument

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import Qt, QItemSelectionModel

from qgis.utils import iface
from shutil import copyfile

import re
from osgeo import gdal

GDAL_DRIVERS = {"raster": {}, "vector": {}}
for i in range(gdal.GetDriverCount()):
    driver = gdal.GetDriver(i)
    driver_meta = driver.GetMetadata_Dict()

    if 'DCAP_RASTER' in driver_meta:
        GDAL_DRIVERS["raster"][driver.ShortName] = {
            "long_name": driver.LongName,
            "extensions": driver.GetMetadataItem(gdal.DMD_EXTENSIONS)
        }

    if 'DCAP_VECTOR' in driver_meta:
        GDAL_DRIVERS["vector"][driver.ShortName] = {
            "long_name": driver.LongName,
            "extensions": driver.GetMetadataItem(gdal.DMD_EXTENSIONS)
        }


def get_layers() -> Dict[str, QgsMapLayer]:
    return QgsProject.instance().mapLayers()


def get_layer_tree():
    return QgsProject.instance().layerTreeRoot()


def get_layer_filename_and_filetype(layer: QgsLayerTreeLayer):
    return os.path.splitext(layer.source())


def get_project_storage_types() -> List[str]:
    storage_types = []
    layers = get_layers()
    for layer in layers.values():
        if isinstance(layer, QgsRasterLayer):
            continue
        if layer.storageType() not in storage_types:
            storage_types.append(layer.storageType())

    return storage_types


def get_node_level(node: QgsLayerTreeNode):
    level = -1

    if not is_node_a_group(node):
        return level

    level += 1

    try:
        while node.parent() is not None:
            level += 1
            node = node.parent()
    except Exception:
        pass
    finally:
        return level


def delete_node(node: QgsLayerTreeNode):
    parent = node.parent()
    parent.removeChildNode(node)


def add_node_to_group(group: QgsLayerTreeGroup, node: QgsLayerTreeNode, remove_original: bool = False):
    group.insertChildNode(-1, node.clone())
    if remove_original:
        delete_node(node)


def get_layer_storage_type(layer: QgsVectorLayer) -> str:
    if not isinstance(layer, QgsVectorLayer):
        raise ValueError(f"Storage type not defined.")
    return layer.storageType()


def get_layer_geometry(layer: QgsVectorLayer) -> int:
    if is_layer_a_raster(layer):
        return definitions.QGS_RASTER_LAYER_GEOMETRY_TYPE
    return layer.geometryType()


def move_nodes_to_group(group: QgsLayerTreeGroup, nodes: List[QgsLayerTreeNode]):
    """clones nodes in order to group, removes original."""
    for node in nodes:
        add_node_to_group(group, node, True)


def is_node_a_group(node: QgsLayerTreeNode) -> bool:
    return isinstance(node, QgsLayerTreeGroup)


def is_node_a_layer(node: QgsLayerTreeNode) -> bool:
    return isinstance(node, QgsLayerTreeLayer)


def is_node_a_raster(node: QgsLayerTreeNode) -> bool:
    return isinstance(node, QgsRasterLayer)


def create_group(group: QgsLayerTreeGroup, name: str) -> QgsLayerTreeGroup:
    return group.addGroup(str(name))


def create_vector_layer(filepath: str, name: str, provider: str = 'ogr'):
    return QgsVectorLayer(filepath, name, provider)


def create_raster_layer(filepath: str, name: str, provider: str = 'gdal'):
    return QgsRasterLayer(filepath, name, provider)


def get_layer_type(layer) -> str:
    if isinstance(layer, QgsRasterLayer):
        return 'QgsRasterLayer'
    if isinstance(layer, QgsVectorLayer):
        return 'QgsVectorLayer'


def get_encodings() -> List[str]:
    layers = get_layers()

    encodings = []

    for layer in layers.values():
        if not isinstance(layer, QgsVectorLayer):
            continue

        encoding = get_layer_encoding(layer)  # layer.dataProvider().encoding()

        if encoding not in encodings:
            encodings.append(encoding)

    return encodings


def get_layer_encoding(layer: QgsVectorLayer) -> str:
    layer_encoding = layer.dataProvider().encoding()
    if not layer_encoding:
        return 'None'
    return layer_encoding


def get_all_groups() -> List[QgsLayerTreeGroup]:
    """returns groups in tree in order.
     note: LayerTree root is a group, it is a first element in the list."""  # TODO: explain better
    tree = get_layer_tree()

    groups = [tree]

    for node in groups:
        for child in node.children():
            if isinstance(child, QgsLayerTreeGroup):
                groups.append(child)

    return groups


def get_storage_types() -> List[str]:
    storage_types = []
    layers = get_layers()

    for layer in layers.values():
        if is_node_a_raster(layer):
            continue

        if layer.storageType() not in storage_types:
            storage_types.append(layer.storageType())

    return storage_types


def get_loaded_layers_extensions() -> List[str]:
    filetypes = []
    layers = get_layers()

    for layer in layers.values():
        if layer.source().startswith('memory?'):
            if "memory" in filetypes:
                continue

            filetypes.append('memory')
            continue

        filename, filetype = get_layer_filename_and_filetype(layer)

        if filetype in filetypes:
            continue

        filetypes.append(filetype)
    return filetypes


def get_selected_layers() -> List:
    return iface.layerTreeView().selectedLayers()


def get_selected_nodes() -> List[QgsLayerTreeNode]:
    return iface.layerTreeView().selectedNodes()


def get_selected_groups() -> List[QgsLayerTreeGroup]:
    selected_nodes = get_selected_nodes()
    groups = []

    for node in selected_nodes:
        if is_node_a_group(node):
            groups.append(node)

    return sorted(groups, key=lambda group: get_node_level(group))


def is_layer_a_vector_layer(layer: QgsLayerTreeLayer) -> bool:
    return isinstance(layer, QgsVectorLayer)


def is_layer_a_raster(layer: QgsLayerTreeLayer) -> bool:
    return isinstance(layer, QgsRasterLayer)


def get_node_filepath(node: QgsLayerTreeNode) -> str:
    if isinstance(node, QgsLayerTreeLayer):
        return get_layer_filepath(node.layer())
    return ""


def get_layer_filepath(layer: QgsLayerTreeLayer) -> str:
    filepath = ""
    try:
        filepath = layer.dataProvider().dataSourceUri()
    except AttributeError:
        filepath = ""
    finally:
        return filepath


def get_layer_provider(layer: QgsLayerTreeLayer) -> str:
    if isinstance(layer,(QgsVectorLayer, QgsRasterLayer)):
        return layer.dataProvider().name()


def make_in_memory_copy_of_vector_layer(layer: QgsVectorLayer) -> QgsVectorLayer:
    if not isinstance(layer, QgsVectorLayer):
        raise ValueError(f"arg not QgsVectorLayer instance")
    return layer.materialize(QgsFeatureRequest().setFilterFids(layer.allFeatureIds()))


def clear_layer_tree():
    layer_tree = get_layer_tree()
    for child in layer_tree.children():
        delete_node(child)


def get_file_sidecar_files(filepath: str) -> List[str]:
    """returns list of sidecar files"""
    return list(QgsFileUtils.sidecarFilesForPath(filepath))


def get_file_size_on_disk(filepath: str) -> float:
    """returns size in bytes"""
    if not os.path.isfile(filepath):
        return -1

    sidecar_files = get_file_sidecar_files(filepath)
    sidecar_files.append(filepath)

    size_on_disk = 0
    for file in sidecar_files:
        size_on_disk += os.path.getsize(file)

    return size_on_disk


def get_file_last_modified(filepath: str) -> float:
    if not os.path.isfile(filepath):
        return -1

    return os.path.getmtime(filepath)


def get_seconds_since_epoch_in_format(seconds: float, format_: str = "'%Y-%m-%d"):
    return datetime.fromtimestamp(seconds).strftime(format_)


def delete_all_groups_and_move_nodes_to_root():
    groups = get_all_groups()
    root = groups[0]

    for group in groups[1:]:

        nodes = []

        for node in group.children():
            if node in groups:
                continue
            nodes.append(node)

        if nodes:
            move_nodes_to_group(root, nodes)

    for group in reversed(groups[1:]):
        delete_node(group)


def translate_byte_size_to_megabyte_size(byte_size: float, decimals: int = 2) -> float:
    return round(byte_size / (1 << 20), decimals)


def get_layer_features(layer: QgsVectorLayer) -> List[Dict]:
    if not isinstance(layer, QgsVectorLayer):
        return []

    data = []
    for feature in layer.getFeatures():
        data.append(
            {
                'attributes': [None if attr == NULL else attr for attr in feature.attributes()],
                'geometry': feature.geometry().asWkb()
            }
        )

    return data


def load_features_to_layer(layer: QgsVectorLayer, features: List) -> bool:
    if not features:
        return True

    layer_features = []

    for feature in features:
        new_feature = QgsFeature()
        new_feature.setAttributes(feature['attributes'])
        geometry = new_feature.geometry()
        geometry.fromWkb(feature['geometry'])
        new_feature.setGeometry(geometry)
        layer_features.append(new_feature)

    if layer_features:
        return layer.dataProvider().addFeatures(layer_features)

    return False


def get_vector_layer_filepath_for_memory_layer(layer: QgsVectorLayer) -> str:
    geometry_type = QgsWkbTypes.displayString(layer.dataProvider().wkbType())

    crs = layer.dataProvider().sourceCrs().authid()

    return f'{geometry_type}?crs={crs}'


def get_layer_attributes(layer: QgsVectorLayer) -> List[QgsField]:
    if is_layer_a_vector_layer(layer):
        return layer.dataProvider().fields().toList()


def set_layer_attributes(layer: QgsVectorLayer, attributes: List[QgsField]):
    if is_layer_a_vector_layer(layer):
        layer.startEditing()
        layer.dataProvider().addAttributes(attributes)
        layer.commitChanges()


def convert_qgis_field_to_dict(qgsfield: QgsField) -> Dict:
    return {
        'name': str(qgsfield.name()),
        'type': int(qgsfield.type()),
        'typeName': str(qgsfield.typeName()),
        'length': int(qgsfield.length()),
        'precision': int(qgsfield.precision()),
        'comment': str(qgsfield.comment()),
        'subType': int(qgsfield.subType())
    }


def convert_dict_to_qgis_field(attributes: Dict) -> QgsField:
    field = None
    try:
        field = QgsField(attributes['name'], QVariant.Type(int(attributes['type'])), attributes['typeName'],
                      attributes['length'], attributes['precision'], attributes['comment'],
                      QVariant.Type(int(attributes['subType'])))
    except Exception:
        field = None

    return field


def run_background_processing_task(task: QgsTask):
    QgsApplication.taskManager().addTask(task)


def show_dialog_error_message(text: str):
    error_dialog = QMessageBox()
    error_dialog.setText(str(text))
    error_dialog.setWindowTitle('Error')
    error_dialog.setStandardButtons(QMessageBox.Ok)
    error_dialog.exec()


def show_yes_no_message(text: str) -> bool:
    """True if yes was pressed"""
    message = QMessageBox()
    message.setText(str(text))
    message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    message.exec()

    return message.standardButton(message.clickedButton()) == QMessageBox.Yes


def get_named_style_as_qdom(layer: QgsMapLayer) -> QDomDocument:
    doc = QDomDocument()
    try:
        layer.exportNamedStyle(doc)
    except Exception:
        pass

    return doc


def stringify_qdom(document: QDomDocument) -> str:
    text = ''
    try:
        text = document.toString()
    except Exception:
        text = ''
    finally:
        return text


def string_to_qdom(text: str):
    doc = QDomDocument()

    results = doc.setContent(text)
    return results[0], doc


def set_layer_named_style_from_qdom(layer: QgsMapLayer, document: QDomDocument):
    check = True
    try:
        layer.importNamedStyle(document)
    except Exception as e:
        check = False
    finally:
        return check


def is_node_visible(node: QgsLayerTreeNode):
    return node.isVisible()


def set_node_visibility(node: QgsLayerTreeNode, state: bool = True):
    try:
        if is_node_a_group(node):
            node.setItemVisibilityChecked(bool(state))
            return
        QgsProject.instance().layerTreeRoot().findLayer(node.id()).setItemVisibilityChecked(bool(state))
    except Exception as e:
        pass


def toggle_feature_count(tree_layer: QgsLayerTreeLayer, state: bool = True):
    if not isinstance(tree_layer, QgsLayerTreeLayer):
        return False
    tree_layer.setCustomProperty("showFeatureCount", state)
    return True


def reload_layer(layer: QgsLayerTreeLayer):
    if is_node_a_layer(layer):
        layer = layer.layer()
    layer.reload()
    layer.triggerRepaint()


def truncate_layer(layer: QgsVectorLayer):
    layer.dataProvider().truncate()


def commit_changes_to_layer(layer):
    """QgsVectorLayer"""
    if not isinstance(layer, QgsVectorLayer):
        return

    if not layer.isEditable():
        return

    layer.commitChanges()


def copy_file_to_destination(filepath: str, destination_filepath: str) -> bool:
    check = True
    try:
        copyfile(filepath, destination_filepath)
    except IOError:
        check = False

    return check


def copy_file_with_sidecar_files_to_destination(filepath: str, destination_directory: str, name: str = "") -> bool:
    if not os.path.isfile(filepath):
        return False

    check = True

    sidecar_files = get_file_sidecar_files(filepath)
    sidecar_files.append(filepath)

    for sidecar_file in sidecar_files:
        i = 0
        filename = Path(sidecar_file).resolve().stem
        suffix = Path(sidecar_file).resolve().suffixes[-1] if Path(sidecar_file).resolve().suffixes else ""

        if name:
            new_filepath = destination_directory + name + suffix
        else:
            new_filepath = destination_directory + filename + suffix

        while os.path.exists(new_filepath):
            i += 1

            if name:
                new_filepath = destination_directory + name + f"_{str(i)}" + suffix
            else:
                new_filepath = destination_directory + filename + f"_{str(i)}" + suffix

        if not copy_file_to_destination(sidecar_file, new_filepath):
            check = False

    return check


def sanitize_filename(name: str) -> str:
    # regex leaves only letters and numbers in the string
    return re.sub(r'[^a-zA-Z0-9 -_]', '', name)


def get_nested_dictionary_total_value_count(dictionary: Dict) -> int:
    return sum([get_nested_dictionary_total_value_count(v) if isinstance(v, dict) else 1 for v in dictionary.values()])


def ask_question(title: str, text: str, left_button_text: str, right_button_text: str) -> bool:
    """
    returns True if left button was pressed, False if right button was pressed, None if dialog was closed
    """
    box = QMessageBox()
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    buttonY = box.button(QMessageBox.Yes)
    buttonY.setText(left_button_text)
    buttonN = box.button(QMessageBox.No)
    buttonN.setText(right_button_text)
    box.exec_()

    if box.clickedButton() == buttonY:
        return True
    if box.clickedButton() == buttonN:
        return False

    return None


def get_layer_crs_authid(layer: QgsMapLayer) -> str:
    crs = layer.crs().authid()

    return crs if crs else 'None'


def get_layer_crs_user_friendly_identifier(layer: QgsMapLayer) -> str:
    crs = layer.crs().userFriendlyIdentifier()

    return crs if crs else 'None'


def get_layer_crs_description(layer: QgsMapLayer) -> str:
    crs = layer.crs().description()

    return crs if crs else 'None'


def get_layer_crs_ellipsoid_acronym(layer: QgsMapLayer) -> str:
    crs = layer.crs().ellipsoidAcronym()

    return crs if crs else 'None'


def get_layer_crs(layer: QgsMapLayer, method: str = 'authid') -> str:
    """method: 'auth_id' | 'descriptive_name' | 'user_friendly_id' | 'ellipsoid_acronym'
    defaults to 'authid' if wrong method is passed."""

    possible_methods = ['authid', 'descriptive_name', 'user_friendly_id', 'ellipsoid_acronym']

    if method not in possible_methods:
        method = 'authid'

    crs = ''

    if method == 'authid':
        crs = get_layer_crs_authid(layer)
    if method == 'descriptive_name':
        crs = get_layer_crs_description(layer)
    if method == 'user_friendly_id':
        crs = get_layer_crs_user_friendly_identifier(layer)
    if method == 'ellipsoid_acronym':
        crs = get_layer_crs_ellipsoid_acronym(layer)

    return crs if crs else 'None'


def get_all_layers_crs(method: str = 'authid') -> List[str]:
    """method: 'auth_id' | 'descriptive_name' | 'user_friendly_id' | 'ellipsoid_acronym'
    defaults to 'authid' if wrong method is passed."""

    possible_methods = ['authid', 'descriptive_name', 'user_friendly_id', 'ellipsoid_acronym']

    if method not in possible_methods:
        method = 'authid'

    layers = get_layers()
    crs = []

    for layer in layers.values():
        layer_crs = get_layer_crs(layer, method)

        if layer_crs is None:
            continue

        if layer_crs not in crs:
            crs.append(layer_crs)

    return crs


def get_layer_crs_as_wkt(layer: QgsMapLayer) -> str:
    return layer.crs().toWkt()


def set_layer_crs_from_wkt(layer: QgsMapLayer, wkt: str) -> str:
    return layer.crs().fromWkt(wkt)


def get_layer_database_connection(layer: QgsMapLayer):  # -> QgsAbstractDatabaseProviderConnection:
    return QgsProviderRegistry.instance().providerMetadata(
        layer.dataProvider().name()).createConnection(
        layer.dataProvider().dataSourceUri(), {}
    )


def check_layer_has_database_connection(layer: QgsMapLayer) -> bool:
    try:
        get_layer_database_connection(layer)
    except Exception:
        return False
    # if 'connection' not in layer.dataProvider().__dict__:
    #     return False
    #
    # if not callable(layer.dataProvider().connection):
    #     return False

    return True


def vacuum_database_connection(connection):  # QgsAbstractDatabaseProviderConnection):
    connection.vacuum(None, None)


def vacuum_layer_database(layer: QgsMapLayer) -> int:
    if not qgs_abstract_database_provider_connection:
        return -1

    if not (is_layer_a_vector_layer(layer) or is_layer_a_raster(layer)):
        return -1

    if not check_layer_has_database_connection(layer):
        return -1

    try:
        connection = get_layer_database_connection(layer)
        vacuum_database_connection(connection)
        return 1
    except Exception:
        return 0


def is_layer_an_annotation_layer(layer: QgsMapLayer) -> bool:
    if not qgs_annotation_layer:
        return False

    return isinstance(layer, QgsAnnotationLayer)


def select_node(node: QgsLayerTreeNode):
    if isinstance(node, QgsLayerTreeLayer):
        iface.layerTreeView().setCurrentLayer(node.layer())

    # https://gis.stackexchange.com/questions/293528/programmatically-select-a-group-node-using-pyqgis/383321#383321
    if isinstance(node, QgsLayerTreeGroup):
        view = iface.layerTreeView()
        m = view.model()

        listIndexes = m.match(m.index(0, 0), Qt.DisplayRole, node.name(), Qt.MatchFixedString)

        if listIndexes:
            view.selectionModel().setCurrentIndex(listIndexes[0], QItemSelectionModel.ClearAndSelect)


def insert_node_at_parent_index(node: QgsLayerTreeNode, index_: int,
                                delete_original: bool = False, set_selected: bool = True):
    parent = node.parent()
    cloned = node.clone()
    parent.insertChildNode(index_, cloned)

    if delete_original:
        delete_node(node)

    if set_selected:
        select_node(cloned)


def get_node_index_in_group(node: QgsLayerTreeNode):
    if not isinstance(node, QgsLayerTreeNode):
        return -1

    return node.parent().children().index(node)


def get_no_of_node_parent_children(node: QgsLayerTreeNode):
    if not isinstance(node, QgsLayerTreeNode):
        return -1

    return len(node.parent().children())


def move_node_up_down_in_group(up: bool = False) -> bool:
    selected_nodes = get_selected_nodes()

    if not selected_nodes:
        return False

    node = selected_nodes[0]

    node_index = get_node_index_in_group(node)

    if node_index == -1:
        return False

    if not up and get_no_of_node_parent_children(node) == node_index + 1:
        return False

    if up and node_index == 0:
        return False

    insert_node_at_parent_index(node, node_index - 1 if up else node_index + 2, True)

    return True
