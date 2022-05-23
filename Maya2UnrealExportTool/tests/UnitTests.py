import maya.standalone
import unittest
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as OM
import os
import sys

sys.path.append(os.path.dirname(__file__) + r'/../plug-ins/core')
sys.path.append(os.path.dirname(__file__) + r'/../plug-ins/core/dependencies')
import export
import controller
import utilities
from dependencies.unreal import UnrealRemoteCalls


class TestMayaScene(unittest.TestCase):
    def setUp(self):
        print("Set up tests for maya scene.")
        #open the file
        # file_path = os.path.relpath(__file__) + '/../../../../layout_correct size_new.mb'
        file_path = os.path.relpath(__file__) + '/../test_scene.ma'
        cmds.file(file_path, o=True, f=True)

    def test_file_name(self):
        selection_list = export.find_mesh_transforms()
        selection_name_list = [node.name() for node in selection_list]
        # print(selection_name_list)
        self.assertEqual(u'test_pSphere' in selection_name_list, False)
        self.assertEqual(u'test_pTorus' in selection_name_list, True)

    def test_node_transformation(self):
        data = {}
        export.find_mesh_transforms(data)
        print(data)
    

class TestLiveLink(unittest.TestCase):
    def setUp(self):
        print("Set up tests for live link.")

    def test_remote_call(self):
        # controller.start_RPC_servers()
        # UnrealRemoteCalls.import_asset('', None, None)
        pass

    def test_ue_path(self):
        project_path = './A/B/'
        valid_target_path = './A/B/Content/Meshes'
        invalid_target_path = './A/C'
        valid_ue_path = utilities.get_unreal_format_path(valid_target_path, project_path)
        invalid_ue_path = utilities.get_unreal_format_path(invalid_target_path, project_path)
        self.assertEqual(valid_ue_path, '/Game/Meshes')
        self.assertEqual(invalid_ue_path, invalid_target_path)


if __name__ == '__main__':
    maya.standalone.initialize(name='python')
    unittest.main()
    maya.standalone.uninitialize()