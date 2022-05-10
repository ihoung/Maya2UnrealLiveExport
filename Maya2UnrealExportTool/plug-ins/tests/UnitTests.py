import maya.standalone
import unittest

class TestMayaScene(unittest.TestCase):
    def setUp(self):
        print("Set up tests for maya scene.")


class TestLiveLink(unittest.TestCase):
    def setUp(self):
        print("Set up tests for live link.")


if __name__ == '__main__':
    maya.standalone.initialize(name='python')
    unittest.main()
    maya.standalone.uninitialize()