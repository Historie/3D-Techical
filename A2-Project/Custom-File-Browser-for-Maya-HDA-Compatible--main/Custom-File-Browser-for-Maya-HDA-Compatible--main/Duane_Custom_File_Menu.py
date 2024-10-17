from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

# load houdini engine plugin
if cmds.pluginInfo("houdiniEngine", query=True) == False:
    cmds.loadPlugin("houdiniEngine")
    

def maya_main_window():
    # -----------------------------------------------------------
    # convert C++ Ptr to main maya window to a python objectee
    # -----------------------------------------------------------
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    
class OpenImportDialog(QtWidgets.QDialog):
    
    FILE_FILTERS = "HDA (*.hda *.hdanc);;Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary(*mb);;All Files (*.*)"
    selected_filter = "All Files (*.*)"
    dlg_instance = None
    
    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = OpenImportDialog()
        
        if cls.dlg_instance.isHidden():    
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
            
    def __init__(self, parent=maya_main_window()):
        super(OpenImportDialog, self).__init__(parent)
        
        self.setWindowTitle("Custom Open")
        self.setMinimumSize(450, 80)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint) # Get rid of the '?'
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton()
        self.select_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_file_path_btn.setToolTip("Select File")
        
        self.newScene_rb = QtWidgets.QRadioButton("New Scene")
        self.newScene_rb.setChecked(True)
        self.open_rb = QtWidgets.QRadioButton("Open Scene")
        self.loadHDA_rb = QtWidgets.QRadioButton("HDA Load")
        self.import_rb = QtWidgets.QRadioButton("Import")
        self.reference_rb = QtWidgets.QRadioButton("Reference")
        
        self.force_cb = QtWidgets.QCheckBox("Force")
        
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.close_btn = QtWidgets.QPushButton("Close")
    
    def create_layout(self):
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.select_file_path_btn)
        
        radio_btn_layout = QtWidgets.QHBoxLayout()
        radio_btn_layout.addWidget(self.newScene_rb)
        radio_btn_layout.addWidget(self.open_rb)
        radio_btn_layout.addWidget(self.loadHDA_rb)
        radio_btn_layout.addWidget(self.import_rb)
        radio_btn_layout.addWidget(self.reference_rb)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("File:", file_path_layout)
        form_layout.addRow("", radio_btn_layout)
        
        button_layout = QtWidgets.QHBoxLayout() 
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.close_btn)
        
        form_layout.addRow("", self.force_cb)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
    
    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)
        
        self.open_rb.toggled.connect(self.update_force_visibility)
        
        self.apply_btn.clicked.connect(self.load_file)
        self.close_btn.clicked.connect(self.close)
     
    def show_file_select_dialog(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "F:\Art_Software\Houdini\Houdini_HDAs", self.FILE_FILTERS, self.selected_filter)
        if file_path:
            self.filepath_le.setText(file_path)
      
    def update_force_visibility(self, checked):
        self.force_cb.setVisible(checked)
       
    def load_file(self):
        
        HDA_FILE01 = ".hda"
        HDA_FILE02 = ".hdanc"
        
        file_path = self.filepath_le.text()
        if not file_path and self.newScene_rb.isChecked() == False:
            return
            
        file_info = QtCore.QFileInfo(file_path)
        if not file_info.exists() and self.newScene_rb.isChecked() == False:
            om.MGlobal.displayError("File does not exist: {0}".format(file_path))
            return
        
        if self.newScene_rb.isChecked():
            self.new_file()
        elif self.loadHDA_rb.isChecked():
            self.load_HDA(file_path)
        elif self.open_rb.isChecked():
            self.open_file(file_path)
        elif self.import_rb.isChecked():
            self.import_file(file_path)
        else:
            self.reference_file(file_path)
    
    def new_file(self):
        cmds.file(f=True, new=True)
    
    def open_file(self, file_path):
        force = self.force_cb.isChecked()
        if not force and cmds.file(q=True, modified=True):
            result = QtWidgets.QMessageBox.question(self, "Modified", "Current scene has unsaved changes. Continue anyway?")
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                force = True
            else:   
                return
        
        cmds.file(file_path, open=True, ignoreVersion=True, force=force)
    
    def import_file(self, file_path):
        cmds.file(file_path, i=True, ignoreVersion=True)
    
    def reference_file(self, file_path):
        cmds.file(file_path, reference=True, ignoreVersion=True)
     
    def load_HDA(self, file_path):
        mel.eval('houdiniEngine_loadAssetLibrary(\"{}\")'.format(file_path))
        

# PRODUCTION OPEN/CLOSE
if __name__ == "__main__":
   
    try:
        open_import_dialog.close() #pylint: disable=E0601
        open_import_dialog.deleteLater()
    except:
        pass
        
    open_import_dialog = OpenImportDialog()
    open_import_dialog.show()
    
