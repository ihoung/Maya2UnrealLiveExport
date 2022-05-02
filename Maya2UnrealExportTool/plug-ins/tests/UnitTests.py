import maya.standalone
import unittest

class TestMayaScene(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print("setup tests.")


if __name__ == '__main__':
    maya.standalone.initialize(name='python')
    unittest.main()
    maya.standalone.uninitialize()