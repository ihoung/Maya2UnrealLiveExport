import maya.api.OpenMaya as OM
import maya.cmds as cmds
import maya.mel as mel


def export_scene_meshes(dirpath, keepFbx = False):
    if not dirpath:
        return

    # record current user selections to recover in the end
    selection_list = OM.MGlobal.getActiveSelectionList()

    export_transform_nodes = find_mesh_transforms()
    for node in export_transform_nodes:
        export_fbx(dirpath, node)

    # recover previous user selections
    OM.MGlobal.setActiveSelectionList(selection_list)


def export_selected_mesh(dirpath, keepFbx = False):
    if not dirpath:
        return

    selection_list = OM.MGlobal.getActiveSelectionList()
    it_selection = OM.MItSelectionList(selection_list)
    while not it_selection.isDone():
        node = it_selection.getDependNode()
        nodeFn = OM.MFnDagNode(node)
        export_fbx(dirpath, nodeFn)
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

    filepath = '{0}/{1}.fbx'.format(dirpath, nodeFn.name())
    print(filepath)
    mel.eval('FBXExport -f "{}" -s'.format(filepath))
    cmds.delete(duplication)