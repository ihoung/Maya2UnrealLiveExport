import os
import maya.api.OpenMaya as OM


def get_unreal_format_path(abspath, project_path):
    if os.path.relpath(abspath, project_path).startswith(os.pardir):
        print("Absolute path is not a subpath of the project path!")
        return abspath
    content_path = os.path.join(project_path, 'Content')
    relative_path = os.path.relpath(abspath, content_path)
    return os.path.join('/Game', relative_path).replace(os.sep, '/')


def check_transformation_data(data):
    location = data.get('location', None)
    rotation = data.get('rotation', None)
    scale = data.get('scale', None)
    if (type(location) is tuple and type(rotation) is tuple and type(scale) is tuple 
        and len(location) == 3 and len(rotation) == 3 and len(scale) == 3):
        return True
    return False


def get_maya_node_transformation(nodeFn):
    if type(nodeFn) is not OM.MFnDagNode:
        return None
    transformation = OM.MFnTransform(nodeFn.getPath())
    data = {
        'location': tuple(transformation.translation(OM.MSpace.kWorld)),
        'rotation': tuple(transformation.rotation(OM.MSpace.kTransform)),
        'scale': tuple(transformation.scale())
    }
    return data


def get_maya_mesh_node_name(nodeFn):
    if type(nodeFn) is not OM.MFnDagNode:
        return ''
    node_name = nodeFn.name()
    if node_name.endswith('Shape'):
        return node_name[:-len('Shape')]
    return ''