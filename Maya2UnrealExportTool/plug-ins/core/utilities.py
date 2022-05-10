import threading
from .dependencies import unreal
from .dependencies.rpc import maya_server

def start_RPC_servers():
    unreal.bootstrap_unreal_with_rpc_server()

    # start the blender rpc server if its not already running
    if 'MayaRPCServer' not in [thread.name for thread in threading.enumerate()]:
        rpc_server = maya_server.RPCServer()
        rpc_server.start(threaded=True)
