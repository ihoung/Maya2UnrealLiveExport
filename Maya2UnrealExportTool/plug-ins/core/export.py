from imp import reload
import maya.api.OpenMaya as OM
import maya.cmds as cmds
import maya.mel as mel
import os
import sys

import controller
import utilities
if sys.version_info.major == 2:
    reload(controller)
    reload(utilities)


def export_scene_meshes(fbx_dir, import_dir, project_path):
    if not fbx_dir:
        return

    # record current user selections to recover in the end
    selection_list = OM.MGlobal.getActiveSelectionList()

    export_transform_nodes = find_mesh_transforms()
    for node in export_transform_nodes:
        export_fbx(fbx_dir, node)
        # import to unreal
        fbx_file_path = os.path.join(fbx_dir, node.name()+'.fbx').replace(os.sep,'/')
        mesh_data = create_mesh_data(node.name(), fbx_dir, import_dir, project_path)
        controller.unreal_import_asset(fbx_file_path, mesh_data, {})

    # recover previous user selections
    OM.MGlobal.setActiveSelectionList(selection_list)


def export_selected_mesh(fbx_dir, import_dir, project_path):
    if not fbx_dir:
        return

    selection_list = OM.MGlobal.getActiveSelectionList()
    it_selection = OM.MItSelectionList(selection_list)
    while not it_selection.isDone():
        node = it_selection.getDependNode()
        nodeFn = OM.MFnDagNode(node)
        export_fbx(fbx_dir, nodeFn)
        # import to unreal
        fbx_file_path = os.path.join(fbx_dir, nodeFn.name()+'.fbx').replace(os.sep,'/')
        mesh_data = create_mesh_data(nodeFn.name(), fbx_dir, import_dir, project_path)
        controller.unreal_import_asset(fbx_file_path, mesh_data, {})

        it_selection.next()
    
    OM.MGlobal.setActiveSelectionList(selection_list)


def find_mesh_transforms():
    dag_it = OM.MItDag(OM.MItDag.kBreadthFirst, OM.MFn.kTransform)
    selection_list = []
    while dag_it.depth() < 2:
        # dag_path = OM.MDagPath.getAPathTo(it_nodes.thisNode())
        child_dag_it = OM.MItDag()
        child_dag_it.reset(dag_it.currentItem(), OM.MItDag.kDepthFirst, OM.MFn.kMesh)
        while not child_dag_it.isDone():
            if child_dag_it.currentItem() is not dag_it.currentItem():
                nodeFn = OM.MFnDagNode(dag_it.currentItem())
                selection_list.append(nodeFn)
                break
            child_dag_it.next()
        dag_it.next()
    return selection_list


def export_fbx(dirpath, nodeFn):
    print('Start to export {0}'.format(nodeFn.name()))
    # select current node object to export
    export_selection = OM.MSelectionList()
    export_selection.add(nodeFn.getPath())
    OM.MGlobal.setActiveSelectionList(export_selection)

    # Duplicate and tranform object, and then export the duplication
    sl_obj = cmds.ls(sl=True)
    duplication = cmds.duplicate(sl_obj, returnRootsOnly=True)

    # Set position to origin
    temporaryObject = cmds.spaceLocator(name='gridCenter')
    cmds.select(duplication)
    cmds.move(temporaryObject)
    cmds.pointConstraint(temporaryObject, duplication)
    cmds.pointConstraint(remove=True)
    cmds.delete(temporaryObject)

    #freezes the transform setting all rotation,scales and position values to default
    cmds.makeIdentity( apply=True, translate=1, rotate=1, scale=1, normal=2 )
    cmds.delete(constructionHistory=True)

    # Convert file path to standard format, in case that FBXExport cannot recognize
    filepath = os.path.join(dirpath, nodeFn.name()+'.fbx').replace('\\','/')
    # print('Export FBX file: ' + filepath)
    mel.eval('FBXExport -f "{}" -s'.format(filepath))
    cmds.delete(duplication)


def create_mesh_data(asset_name, file_dir, import_path, project_path):
    # Convert import path to Unreal path format
    import_path = utilities.get_unreal_format_path(import_path, project_path)

    file_path = os.path.join(file_dir, asset_name+'.fbx')
    asset_path = os.path.join(import_path, asset_name+'.uasset')

    # Convert path format to unified format
    file_path = file_path.replace(os.sep,'/')
    import_path = import_path.replace(os.sep,'/')
    asset_path = asset_path.replace(os.sep,'/')
    # print('\n'.join([file_path, import_path, asset_path]))

    mesh_data = {
        'asset_type': 'MESH',
        'file_path': file_path,
        'asset_folder': import_path,
        'asset_path': asset_path,
        'import_mesh': True,
    }
    return mesh_data