import maya.api.OpenMaya as OM
import maya.cmds as cmds
import maya.mel as mel


def export_scene_meshes():
    it_nodes = OM.MItDependencyNodes(OM.MFn.kMesh)
    while not it_nodes.isDone():
        obj = it_nodes.thisNode()
        it_nodes.next()


def export_selected_mesh():
    selection_list = OM.MGlobal.getActiveSelectionList()
    it_selection = OM.MItSelectionList(selection_list)
    while not it_selection.isDone():
        node = it_selection.getDependNode()

        it_selection.next()


def export_fbx(path):
    pass