from imp import reload
import os
import sys
from functools import partial
import shutil

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtGui import QColor, QFont
from PySide2.QtUiTools import QUiLoader
from shiboken2 import wrapInstance

from core import controller, export, utilities
if sys.version_info <= (3,4):
    reload(controller)
    reload(export)
    reload(utilities)

maya_useNewAPI = True


def get_main_window():
    window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window), QtWidgets.QWidget)


class ExportWindow(QtWidgets.QWidget):
    def __init__(self, parent=get_main_window()):
        if sys.version_info.major == 3:
            super().__init__(parent)
        else: # python 2
            super(ExportWindow, self).__init__(parent)

        app_root = os.environ.get("M2U_EXPORT_PLUGIN_ROOT")
        loader = QUiLoader()
        file = QFile(app_root + "/ui/form.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, parentWidget=self)
        file.close()
        self.setWindowFlags(QtCore.Qt.Tool)

        self.ui.show()
        self.ui.btn_detectProjPath.clicked.connect(self.get_project_path)
        self.ui.btn_ProjectPathBrowser.clicked.connect(partial(self.open_dir_browser, 'Project'))
        self.ui.checkBox_newLevel.stateChanged.connect(self.check_generating_new_level)
        self.ui.btn_MapPathBrowser.clicked.connect(partial(self.open_dir_browser, 'Map'))
        self.ui.btn_ModelPathBrowser.clicked.connect(partial(self.open_dir_browser, 'Model'))
        self.ui.btn_FbxPathBrowser.clicked.connect(partial(self.open_dir_browser, 'FBX')) 
        self.ui.checkBox_keepFbx.stateChanged.connect(self.check_fbx_storage_state)
        self.ui.btn_restartLink.clicked.connect(self.restart_unreal_link)
        self.ui.btn_exportScene.clicked.connect(self.export_scene)
        self.ui.btn_exportSelected.clicked.connect(self.export_selected_asset)
        self.ui.btn_cancel.clicked.connect(self.close)

        self.generate_new_level = True
        self.keep_fbx = False

    def open_dir_browser(self, browser_type):
        dir_path = cmds.fileDialog2(caption='Select Your Directory',fileMode=3, okCaption='Confirm')
        if dir_path is None:
            return
        dir_path = dir_path[0]
        if browser_type == 'Project':
            self.set_project_path(dir_path)
        elif browser_type == 'Map':
            self.ui.text_MapPath.setPlainText(dir_path)
        elif browser_type == 'Model':
            self.ui.text_ModelPath.setPlainText(dir_path)
        elif browser_type == 'FBX':
            self.ui.text_FbxPath.setPlainText(dir_path)

    def set_project_path(self, dir_path):
        # If directory dosen't contain a 'Content' folder, it is absolutely not a Unreal project.
        content_dir = dir_path + "/Content/"
        if not os.path.exists(content_dir):
            cmds.confirmDialog(title="Error", message="Can't find 'Content' folder. Invalid path of Unreal project!")
        else:
            # If detect 'Content' folder, add other asset paths automatically.
            # Default folders are 'Maps', 'Meshes', 'Textures' and 'Materials'.
            # If a folder name cannot be found, its path need to be added manually.
            self.ui.text_ProjectPath.setPlainText(dir_path)
            if os.path.exists(content_dir + "Maps"):
                self.ui.text_MapPath.setPlainText(content_dir + "Maps")
            if os.path.exists(content_dir + "Meshes"):
                self.ui.text_ModelPath.setPlainText(content_dir + "Meshes")
            if os.path.exists(content_dir + "FBXs"):
                self.ui.text_FbxPath.setPlainText(content_dir + "FBXs")

    def check_generating_new_level(self):
        if self.ui.checkBox_newLevel.isChecked():
            self.generate_new_level = True
            self.ui.text_levelMapName.setEnabled(True)
        else:
            self.generate_new_level = False
            self.ui.text_levelMapName.setEnabled(False)

    def check_fbx_storage_state(self):
        if self.ui.checkBox_keepFbx.isChecked():
            self.ui.text_FbxPath.setEnabled(True)
            self.ui.btn_FbxPathBrowser.setEnabled(True)
            self.keep_fbx = True
        else:
            self.ui.text_FbxPath.setEnabled(False)
            self.ui.btn_FbxPathBrowser.setEnabled(False)
            self.keep_fbx = False

    def check_export_path(self):
        content_dir = self.ui.text_ProjectPath.toPlainText() + "/Content/"
        map_dir = self.ui.text_MapPath.toPlainText()
        model_dir = self.ui.text_ModelPath.toPlainText()
        # Check if paths are valid.
        msgInfo = ""
        if not os.path.exists(content_dir):
            msgInfo += "Can't find 'Content' folder. Invalid path of Unreal project!\n"
        if self.generate_new_level and (not os.path.exists(map_dir) or os.path.relpath(map_dir, content_dir).startswith(os.pardir)):
            msgInfo += "Invalid Map path!\n"
        if not os.path.exists(model_dir) or os.path.relpath(model_dir, content_dir).startswith(os.pardir):
            msgInfo += "Invalid Model path!\n"
        if self.keep_fbx and not os.path.exists(self.ui.text_FbxPath.toPlainText()):
            msgInfo += "Invalid FBX path!\n"
        if msgInfo:
            cmds.confirmDialog(title="Error", message=msgInfo)
            return False
        return True

    def export_selected_asset(self):
        if len(cmds.ls(sl=True)) == 0:
            cmds.confirmDialog(title="No Selection", message='No object selected!')
            return
        if self.check_export_path():
            project_dir = self.ui.text_ProjectPath.toPlainText()
            if self.keep_fbx:
                fbx_dir = self.ui.text_FbxPath.toPlainText()
            else:
                fbx_dir = os.path.join(project_dir, "Content", "Fbx_temp").replace(os.sep,'/')
                if not os.path.exists(fbx_dir):
                    os.mkdir(fbx_dir)
            import_dir = os.path.abspath(self.ui.text_ModelPath.toPlainText())
            # export assets to the corresponding folders
            export.export_selected_mesh(fbx_dir, import_dir, project_dir)
            # Delete temporary fbx files if don't want to keep them
            if not self.keep_fbx and os.path.exists(fbx_dir):
                shutil.rmtree(fbx_dir) 

    def export_scene(self):
        if self.check_export_path():
            new_level_name = self.ui.text_levelMapName.toPlainText()
            if self.generate_new_level and not new_level_name:
                cmds.confirmDialog(title="Error", message='New level name is empty!')
                return
            project_dir = self.ui.text_ProjectPath.toPlainText()
            if self.keep_fbx:
                fbx_dir = self.ui.text_FbxPath.toPlainText()
            else:
                project_dir = self.ui.text_ProjectPath.toPlainText()
                fbx_dir = os.path.join(project_dir, "Content", "Fbx_temp").replace(os.sep,'/')
                if not os.path.exists(fbx_dir):
                    os.mkdir(fbx_dir)
            import_dir = os.path.abspath(self.ui.text_ModelPath.toPlainText())
            transformation_data = export.export_scene_meshes(fbx_dir, import_dir, project_dir)
            map_dir = self.ui.text_MapPath.toPlainText()
            controller.add_asset_into_level(
                transformation_data, 
                self.generate_new_level, 
                new_level_name+'.umap',
                utilities.get_unreal_format_path(map_dir, project_dir)
            )
            # Delete temporary fbx files if don't want to keep them
            if not self.keep_fbx and os.path.exists(fbx_dir):
                shutil.rmtree(fbx_dir)

    def restart_unreal_link(self):
        controller.start_RPC_servers()
    
    def get_project_path(self):
        project_path = controller.get_current_project_path()
        if project_path is None:
            cmds.confirmDialog(title="Warning", message='No Opened Unreal Editor!')
            return
        self.set_project_path(project_path)


class M2UExport(OpenMaya.MPxCommand):
    CMD_NAME = "M2UExport"
    ui = None

    def __init__(self):
        if sys.version_info.major == 3:
            super().__init__()
        else:
            super(M2UExport, self).__init__()
        ui = None

    @classmethod
    def doIt(cls, args):
        """
        Called when the command is executed in script
        """
        if M2UExport.ui is None:
            M2UExport.ui = ExportWindow()
        M2UExport.ui.showNormal()

    @classmethod
    def creator(cls):
        """
        Think of this as a factory
        """
        return M2UExport()

    @classmethod
    def cleanup(cls):
        # cleanup the UI and call the destructors
        if M2UExport.ui is not None:
            M2UExport.ui.deleteLater()



def initializePlugin(plugin):
    vendor = "YiyangHuang"
    version = "1.0.0"
    if os.environ.get("M2U_EXPORT_PLUGIN_ROOT") is None:
        OpenMaya.MGlobal.displayError(
            "Module Environment not set ensure M2U_EXPORT_PLUGIN_ROOT is set in module file"
        )
        # throw exception and let maya deal with it
        raise

    plugin_fn = OpenMaya.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerCommand(M2UExport.CMD_NAME, M2UExport.creator)
        # cmds.evalDeferred("cmds.M2UExport()")
        cmds.evalDeferred("cmds.menu('M2UExportSetting', label='Unreal Export Tool', parent='MayaWindow', pmc=cmds.M2UExport)")
    except:
        OpenMaya.MGlobal.displayError(
            "Failed to register command: {0}".format(M2UExport.CMD_NAME)
        )


def uninitializePlugin(plugin):
    # cleanup the dialog first
    M2UExport.cleanup()
    plugin_fn = OpenMaya.MFnPlugin(plugin)
    try:
        cmds.evalDeferred("cmds.deleteUI('M2UExportSetting')")
        plugin_fn.deregisterCommand(M2UExport.CMD_NAME)
    except:
        OpenMaya.MGlobal.displayError(
            "Failed to deregister command: {0}".format(M2UExport.CMD_NAME)
        )


if __name__ == '__main__':
    plugin_name = "Maya2UnrealExportTool"

    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(
            plugin_name
        )
    )
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(
            plugin_name
        )
    )
