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
from dependencies.unreal import UnrealRemoteCalls


class TestMayaScene(unittest.TestCase):
    def setUp(self):
        print("Set up tests for maya scene.")

    def test_file_name(self):
        #open the file
        # file_path = os.path.relpath(__file__) + '/../../../../layout_correct size_new.mb'
        file_path = os.path.relpath(__file__) + '/../test_scene.ma'
        cmds.file(file_path, o=True, f=True)
        selection_list = export.find_mesh_transforms()
        selection_name_list = [node.name() for node in selection_list]
        # print(selection_name_list)
        self.assertEqual(u'test_pSphere' in selection_name_list, False)
        self.assertEqual(u'test_pTorus' in selection_name_list, True)
    

class TestLiveLink(unittest.TestCase):
    def setUp(self):
        print("Set up tests for live link.")

    def test_remote_call(self):
        # controller.start_RPC_servers()
        # UnrealRemoteCalls.import_asset('', None, None)
        pass


if __name__ == '__main__':
    maya.standalone.initialize(name='python')
    unittest.main()
    maya.standalone.uninitialize()