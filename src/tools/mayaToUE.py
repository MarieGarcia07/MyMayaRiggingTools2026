from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout
from core.MayaWidget import MayaWidget
import maya.cmds as mc

class MayaToUE:
    def __init__(self):
        self.meshes = []
        self.rootJnt = ""
        self.clips = []

    def SetSelectedAsMesh(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("Please select the mesh(es) of the rig")
        
        for obj in selection:
            shapes = mc.listRelatives(obj, s=True)
            if not shapes or mc.objectType(shapes[0]) != "mesh":
                raise Exception(f"{obj} is not a mesh, please select the mesh(es) of the rig")
            
        self.meshes = selection

class MayaToUEWidget(MayaWidget):
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("MayaToUE")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        meshSelectlayout = QHBoxLayout()
        self.masterLayout.addLayout(meshSelectlayout)
        meshSelectlayout.addWidget(QLabel("Mesh:"))
        self.meshSelectLineEdit = QLineEdit()
        self.meshSelectLineEdit.setEnabled(False)
        meshSelectlayout.addWidget(self.meshSelectLineEdit)
        meshSelectBtn = QPushButton("<<<")
        meshSelectlayout.addWidget(meshSelectBtn)
        meshSelectBtn.clicked.connect(self.MeshSelectBtnClicked)

    def MeshSelectBtnClicked(self):
        self.mayaToUE.SetSelectedAsMesh()
        self.meshSelectLineEdit.setText(",".join(self.mayaToUE.meshes))
    
    def GetWidgetHash(self):
        return "16ad9c14d958586e32b5ca04a80ef51a82f299c9701126735c261f156fc0bab4"
    
def Run():
    mayaToUEWidget = MayaToUEWidget()
    mayaToUEWidget.show()

Run()
    
