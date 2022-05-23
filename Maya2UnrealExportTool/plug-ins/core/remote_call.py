# Rewrite import part of unreal remote call in dependencies.unreal,
# whose data parse is complex for other DCC tools except for Blender.
# Only import model mesh (static mesh) currently, mostly using default import setting in unreal

from imp import reload
import os
import json
import time
import sys
import inspect

try:
    import unreal
except (ModuleNotFoundError if sys.version_info.major == 3 else ImportError):
    pass

import dependencies.unreal as ue
from dependencies.rpc import factory
from dependencies.unreal import Unreal

reload(ue)
reload(factory)


class UnrealImportAsset(Unreal):
    def __init__(self, file_path, asset_data, property_data):
        """
        Initializes the import with asset data and property data.

        :param str file_path: The full path to the file to import.
        :param dict asset_data: A dictionary that contains various data about the asset.
        :param PropertyData property_data: A property data instance that contains all property values of the tool.
        """
        self._file_path = file_path
        self._asset_data = asset_data
        self._property_data = property_data
        self._import_task = unreal.AssetImportTask()
        self._options = None

    def set_static_mesh_import_options(self):
        """
        Sets the static mesh import options.
        """
        if not self._asset_data.get('skeletal_mesh') and not self._asset_data.get('animation'):
            self._options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
            self._options.static_mesh_import_data.import_mesh_lo_ds = False

            import_data = unreal.FbxStaticMeshImportData()
            self.set_settings(
                self._property_data.get('static_mesh_import_data', {}),
                import_data
            )
            self._options.static_mesh_import_data = import_data

            self._options.set_editor_property('import_as_skeletal', False)
            self._options.set_editor_property('import_animations', False)

    def set_fbx_import_task_options(self):
        """
        Sets the FBX import options.
        """
        self._import_task.set_editor_property('filename', self._file_path)
        self._import_task.set_editor_property('destination_path', self._asset_data.get('asset_folder'))
        self._import_task.set_editor_property('replace_existing', True)
        self._import_task.set_editor_property('replace_existing_settings', True)
        self._import_task.set_editor_property(
            'automated',
            not self._property_data.get('advanced_ui_import', {}).get('value', False)
        )
        self._import_task.set_editor_property('save', True)

        import_mesh = self._asset_data.get('import_mesh', False)

        # set the options
        self._options = unreal.FbxImportUI()
        self._options.set_editor_property('import_mesh', import_mesh)
        # not import textures and material currently
        self._options.set_editor_property('import_materials', False)
        self._options.set_editor_property('import_textures', False)
        # unreal.FbxStaticMeshImportData
        self._options.static_mesh_import_data.set_editor_property('combine_meshes', True)
        self._options.static_mesh_import_data.set_editor_property('auto_generate_collision', True)

        # set the static mesh import options
        self.set_static_mesh_import_options()

    def run_import(self):
        # assign the options object to the import task and import the asset
        self._import_task.options = self._options
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([self._import_task])
        return list(self._import_task.get_editor_property('imported_object_paths'))


@factory.remote_class(ue.remote_unreal_decorator)
class UnrealRemoteCalls:
    @staticmethod
    def asset_exists(asset_path):
        """
        Checks to see if an asset exist in unreal.

        :param str asset_path: The path to the unreal asset.
        :return bool: Whether or not the asset exists.
        """
        return unreal.EditorAssetLibrary.does_asset_exist(asset_path)

    @staticmethod
    def directory_exists(asset_path):
        """
        Checks to see if a directory exist in unreal.

        :param str asset_path: The path to the unreal asset.
        :return bool: Whether or not the asset exists.
        """
        # TODO fix this when the unreal API is fixed where it queries the registry correctly
        #  https://jira.it.epicgames.com/browse/UE-142234
        # return unreal.EditorAssetLibrary.does_directory_exist(asset_path)
        return True

    @staticmethod
    def delete_asset(asset_path):
        """
        Deletes an asset in unreal.

        :param str asset_path: The path to the unreal asset.
        :return bool: Whether or not the asset was deleted.
        """
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            unreal.EditorAssetLibrary.delete_asset(asset_path)

    @staticmethod
    def delete_directory(directory_path):
        """
        Deletes an folder and its contents in unreal.

        :param str directory_path: The game path to the unreal project folder.
        :return bool: Whether or not the directory was deleted.
        """
        # API BUG:cant check if exists https://jira.it.epicgames.com/browse/UE-142234
        # if unreal.EditorAssetLibrary.does_directory_exist(directory_path):
        unreal.EditorAssetLibrary.delete_directory(directory_path)

    @staticmethod
    def import_asset(file_path, asset_data, property_data, file_type='fbx'):
        """
        Imports an asset to unreal based on the asset data in the provided dictionary.

        :param str file_path: The full path to the file to import.
        :param dict asset_data: A dictionary of import parameters.
        :param dict property_data: A dictionary representation of the properties.
        :param str file_type: The import file type.
        """
        unreal_import_asset = UnrealImportAsset(
            file_path=file_path,
            asset_data=asset_data,
            property_data=property_data
        )
        if file_type.lower() == 'fbx':
            unreal_import_asset.set_fbx_import_task_options()

        # run the import task
        return unreal_import_asset.run_import()

    @staticmethod
    def create_asset(asset_path, asset_class=None, asset_factory=None, unique_name=True):
        """
        Creates a new unreal asset.

        :param str asset_path: The project path to the asset.
        :param str asset_class: The name of the unreal asset class.
        :param str asset_factory: The name of the unreal factory.
        :param bool unique_name: Whether or not the check if the name is unique before creating the asset.
        """
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        if unique_name:
            asset_path, _ = asset_tools.create_unique_asset_name(
                base_package_name=asset_path,
                suffix=''
            )
        path = asset_path.rsplit("/", 1)[0]
        name = asset_path.rsplit("/", 1)[1]
        asset_tools.create_asset(
            asset_name=name,
            package_path=path,
            asset_class=asset_class,
            factory=asset_factory
        )

    @staticmethod
    def get_project_path():
        return unreal.Paths.project_dir()

    @staticmethod
    def create_and_open_new_level(asset_path):
        unreal.EditorLevelLibrary.new_level(asset_path)

    @staticmethod
    def load_level(asset_path):
        unreal.EditorLevelLibrary.save_current_level()
        unreal.EditorLevelLibrary.load_level(asset_path)

    @staticmethod
    def add_asset_to_current_level(transformation_data, asset_path):
        # actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(10.0, 20.0, 30.0), unreal.Rotator(0.0, 0.0, 0.0))
        # mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
        # mesh = unreal.EditorAssetLibrary.load_asset('/Game/Meshes/test_pTorus')
        # mesh_component.set_static_mesh(mesh)
        for mesh_name, transformation in transformation_data.items():
            location_data = transformation.get('location', (0.0, 0.0, 0.0))
            rotation_data = transformation.get('rotation', (0.0, 0.0, 0.0))
            scale_data = transformation.get('scale', (1.0, 1.0, 1.0))
            location = unreal.Vector(location_data[0], location_data[2], location_data[1])
            rotation = unreal.Rotator(rotation_data[0], rotation_data[2], rotation_data[1])
            scale = unreal.Vector(scale_data[0], scale_data[2], scale_data[1])
            # spawn actor(object) in current level
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
            mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            mesh_component.set_world_scale3d(scale)
            mesh = unreal.EditorAssetLibrary.load_asset(os.path.join(asset_path, mesh_name).replace(os.sep,'/'))
            mesh_component.set_static_mesh(mesh)
