import datetime
from typing import List, Dict
import uuid
import pickle

from . import tools

import re

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
    QgsTask
)


# class Snapshot(TypedDict):
#     at_time: datetime.datetime
#     name: str
#     include_rasters: bool
#     include_vector_layers: bool
#     vector_layers_in_memory: bool
#     tree: dict
#     id: int


class Snapshooter(QgsTask):
    LAYER_DETAILS_KEYS = ['filepath', 'name', 'provider', 'type', 'features', 'attributes']
    SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), 'Snapshots/')

    def __init__(self, name: str, include_rasters: bool, include_vector_layers: bool, vector_layers_in_memory: bool,
                 starting_point: QgsLayerTreeGroup = None, callback_func=None):
        super().__init__(f'Snapshot {name}, Raster: {str(include_rasters)}, VectorLayers: {str(include_vector_layers)}, \
        Vector layers in memory: {str(vector_layers_in_memory)}')

        self.new_snapshot = {}
        self.snapshot_layer_symbology = {}
        self.starting_point = starting_point
        self.name = name
        self.include_rasters = include_rasters
        self.include_vector_layers = include_vector_layers
        self.vector_layers_in_memory = vector_layers_in_memory

        self.callback_func = callback_func
        self.task_done = False

    def run(self) -> bool:
        check = False
        try:
            self._build_dictionary(
                self.new_snapshot,
                tools.get_layer_tree() if self.starting_point is None else self.starting_point,
                self.include_rasters,
                self.include_vector_layers,
                self.vector_layers_in_memory,
                self.snapshot_layer_symbology
            )
            check = True
        except Exception:
            check = False
        finally:
            self.finished(check)
            return check

    def _generate_snapshot_id(self, time: datetime.datetime) -> str:
        return (self.name
                + str(time)
                + str(self.include_rasters)
                + str(self.include_vector_layers)
                + str(self.vector_layers_in_memory)
                + uuid.uuid4().hex
        )

    def finished(self, result: bool):
        if self.task_done:
            return

        if not result:
            if self.callback_func is not None:
                self.callback_func({})

        current_time = datetime.datetime.now()

        snapshot_id = self._generate_snapshot_id(current_time)

        snapshot_details = {
            'at_time': current_time,
            'name': self.name,
            'include_rasters': self.include_rasters,
            'include_vector_layers': self.include_vector_layers,
            'vector_layers_in_memory': self.vector_layers_in_memory,
            'id': snapshot_id
        }
        filepath = Snapshooter.SNAPSHOT_DIR + re.sub('[^a-zA-Z0-9]+', '', snapshot_id) + '.snp'

        with open(filepath, 'wb') as file:
            pickle.dump(snapshot_details, file, protocol=4)
            pickle.dump(self.new_snapshot, file, protocol=4)
            pickle.dump(self.snapshot_layer_symbology, file, protocol=4)

        if self.callback_func is not None:
            self.callback_func(snapshot_details)

        self.task_done = True

    @classmethod
    def get_all_snapshots_details(cls):
        snapshot_details = []
        for file in os.listdir(Snapshooter.SNAPSHOT_DIR):
            if file.endswith('.snp'):
                filepath = os.path.join(Snapshooter.SNAPSHOT_DIR, file)
                try:
                    with open(filepath, 'rb') as f:
                        snapshot_details.append(pickle.load(f))
                except Exception:
                    continue
        return snapshot_details

    @classmethod
    def delete_snapshot(cls, id_: int) -> bool:
        delete_filepath = None

        for file in os.listdir(Snapshooter.SNAPSHOT_DIR):
            if file.endswith('.snp'):
                filepath = os.path.join(Snapshooter.SNAPSHOT_DIR, file)
                try:
                    with open(filepath, 'rb') as f:
                        details = pickle.load(f)
                        if details['id'] == id_:
                            delete_filepath = filepath
                            break
                except Exception:
                    continue

        if delete_filepath is None:
            return False

        try:
            os.remove(delete_filepath)
            return True
        except OSError:
            return False

    @classmethod
    def get_snapshot(cls, id_: int):
        """-> Tuple[Dict, Snapshot]"""
        snap = None
        details = None
        symbology = None

        for file in os.listdir(Snapshooter.SNAPSHOT_DIR):
            if file.endswith('.snp'):
                filepath = os.path.join(Snapshooter.SNAPSHOT_DIR, file)
                try:
                    with open(filepath, 'rb') as f:
                        details = pickle.load(f)
                        if details['id'] == id_:
                            snap = pickle.load(f)
                            try:
                                symbology = pickle.load(f)
                            except EOFError:
                                symbology = None
                            break
                except Exception:
                    continue

        if snap is None:
            details = None

        return details, snap, symbology

    def _build_dictionary(
            self,
            current,
            root=None,
            include_rasters: bool = True,
            include_vector_layers: bool = True,
            vector_layers_in_memory: bool = False,
            symbology=None
    ):
        if root is None:
            return

        for node in root.children():
            if self.isCanceled():
                raise RuntimeError

            # integer(0, 1) - is layer visibility toggled on or off
            # group/layer name within parenthesis
            # id to keep unique values in dictionary keys
            key = f"{int(tools.is_node_visible(node))}({node.name()}){id(node)}"

            if tools.is_node_a_group(node):
                if key not in current.keys():
                    current[key] = {}
                self._build_dictionary(current[key], node, include_rasters, include_vector_layers, vector_layers_in_memory, symbology)
                continue

            if tools.is_node_a_layer(node):
                layer = node.layer()
                if not layer.isValid():
                    continue

                symbology[key] = tools.stringify_qdom(tools.get_named_style_as_qdom(layer))

                if include_rasters and tools.is_layer_a_raster(layer):
                    current[key] = self.get_layer_details(layer)
                    continue

                if include_vector_layers and tools.is_layer_a_vector_layer(layer):
                    layer_details = self.get_layer_details(layer)

                    if vector_layers_in_memory:
                        current[key] = self.get_layer_details(layer, True, True, True)
                        continue

                    if layer_details['filepath'].startswith('memory'):  # or vector_layers_in_memory:
                        current[key] = self.get_layer_details(layer, True)  # tools.make_in_memory_copy_of_vector_layer(layer)
                        continue

                    current[key] = layer_details
                    continue

    @staticmethod
    def get_layer_details(layer: QgsLayerTreeLayer, copy_features: bool = False, copy_attributes: bool = False,
                          create_filepath_for_memory_layer: bool = False) -> Dict:
        def convert_attributes_to_dict_list(attrs: List) -> List[Dict]:
            return [tools.convert_qgis_field_to_dict(attr) for attr in attrs]

        return {
            "filepath": tools.get_layer_filepath(layer) if not create_filepath_for_memory_layer else tools.get_vector_layer_filepath_for_memory_layer(layer),
            "name": layer.name(),
            "provider": tools.get_layer_provider(layer),
            "type": tools.get_layer_type(layer),
            "features": tools.get_layer_features(layer) if copy_features else [],
            "attributes": convert_attributes_to_dict_list(tools.get_layer_attributes(layer)) if copy_attributes else [],
            "crs": tools.get_layer_crs_as_wkt(layer),
        }
