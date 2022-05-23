from imp import reload
import json
import sys
import os
import threading

import remote_call
from dependencies import unreal
from dependencies.rpc import maya_server
from remote_call import UnrealRemoteCalls

if sys.version_info.major == 2:
    reload(unreal)
    reload(remote_call)


def start_RPC_servers():
    unreal.bootstrap_unreal_with_rpc_server()

    # start the blender rpc server if its not already running
    if 'MayaRPCServer' not in [thread.name for thread in threading.enumerate()]:
        rpc_server = maya_server.RPCServer()
        rpc_server.start(threaded=True)


def unreal_import_asset(file_path, asset_data, property_data):
    """
    Import FBX asset to Unreal
    
    file_path: full path of FBX file
    asset_data: information including file path, import data type etc. Data structure (optional keys)
        {
            'file_path': full path of FBX file (the same as parameter file_path above)
            'asset_folder': destination path of import folder (Root path is "./Game/". Don't use absolute path),
            'asset_path': f'{asset_folder}{asset_name}',
            'skeletal_mesh': bool value that if data contain skeletal mesh
            'skeleton_asset_path': path of skeletal mesh data,
            'lods': LODs data,
            'sockets': sockets data,
            'import_mesh': bool value
            'animation': bool value that if import animation (Don't include this key if only import static mesh)
        }
    property_data: import property in unreal. Data structure (optional keys)
        {
            a
        }
    """
    start_RPC_servers()
    # Convert unicode into str before sending to RPC client
    UnrealRemoteCalls.import_asset(str(file_path), asset_data, property_data)


def get_current_project_path():
    start_RPC_servers()
    return UnrealRemoteCalls.get_project_path()


def add_asset_into_level(transformation_data, mesh_asset_path, create_new_level=True, level_name='', level_dir_path=''):
    if create_new_level:
        if not level_name or not level_dir_path:
            return
        level_path = str(os.path.join(level_dir_path, level_name).replace(os.sep,'/'))
        if UnrealRemoteCalls.asset_exists(level_path):
            print('Level map "{}" already exists!'.format(level_name))
            UnrealRemoteCalls.load_level(level_path)
        else:
            UnrealRemoteCalls.create_and_open_new_level(level_path)
    UnrealRemoteCalls.add_asset_to_current_level((transformation_data), str(mesh_asset_path))
