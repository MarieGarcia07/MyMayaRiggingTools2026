from core.MayaWidget import MayaWidget
import maya.cmds as mc
from maya.OpenMaya import MVector #same as Vector3 in Unity
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QColorDialog
import importlib
import core.MayaUtilities
importlib.reload(core.MayaUtilities)
from core.MayaUtilities import (CreateCircleControllerForJnt,
                                 CreateBoxControllerForJnt, 
                                 CreatePlusController, 
                                 ConfigureCtrlForJnt,
                                 GetObjectPositionAsVec)

class LimbRiggerWidget(MayaWidget): # the class to handle the widget for limb rigger
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limb Rigger")
        self.rigger = LimbRigger()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Select the 3 joints of the limb, from base to end, and then:"))

        self.infoLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.infoLayout)
        self.infoLayout.addWidget(QLabel("Name Base:"))

        self.nameBaseLineEdit = QLineEdit()
        self.infoLayout.addWidget(self.nameBaseLineEdit)

        self.setNameBaseBtn = QPushButton("Set Name Base")
        self.setNameBaseBtn.clicked.connect(self.SetNameBaseBtnClicked)
        self.infoLayout.addWidget(self.setNameBaseBtn)

        # add a color pick widget to the self.masterLayout
        self.colorBtn = QPushButton() #button
        self.colorBtn.setFixedSize(300,30) #size
        self.colorBtn.setStyleSheet("background-color: #ffffff;") #default color
        self.masterLayout.addWidget(self.colorBtn) #adds widget
        self.colorBtn.clicked.connect(self.ColorPicker) # listen for color change and connect to a function

        self.rigLimbBtn = QPushButton("Rig Limb")
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterLayout.addWidget(self.rigLimbBtn)
    
    def GetWidgetHash(self):
        return "e06a840f9d9bbbfe49d138d7e6f9f9659595537c41c8dc971c75627c6fcd7c64"
    
    def SetNameBaseBtnClicked(self):
        self.rigger.SetNameBase(self.nameBaseLineEdit.text())

    def RigLimbBtnClicked(self):
        self.rigger.RigLimb()

    def ColorPicker(self): # the function needs to update the color of limbRigger : self.rigger.controlColorRGB
        color = QColorDialog.getColor(parent=self) #opens the color picker while parenting the window to the maya window
        
        if color.isValid(): #checks if the user actually selected a color
            r = color.red() #extracts the RGB values in 0-255 range
            g = color.green()
            b = color.blue()

            self.rigger.controlColorRGB = (r/255.0, g/255.0, b/255.0) #stores the color in a format maya understands from the imported QWidgets

            self.colorBtn.setStyleSheet(f"background-color: {color.name()};") #updates button color

class LimbRigger(): # the class to handle the rigging job
    # the constructor that initializes
    def __init__(self):
        self.nameBase = ""
        self.controllerSize = 10
        self.blendControllerSize = 4
        self.controlColorRGB = [0,0,0]
    
    def SetNameBase(self, newNameBase):
        self.nameBase = newNameBase
        print(f"name base is set to: {self.nameBase}")

    def SetControllerSize(self, newControllerSize):
        self.controllerSize = newControllerSize
    
    def SetBlendControllerSize(self, newBlendControllerSize):
        self.blendControllerSize = newBlendControllerSize
    
    def RigLimb(self):
        print ("Start Rigging")
        rootJnt, midJnt, endJnt = mc.ls(sl = True)
        print(f"found root: {rootJnt}, mid: {midJnt}, and end: {endJnt}")
        rootCtrl, rootCtrlGrp = CreateCircleControllerForJnt(rootJnt, "fk_" + self.nameBase, self.controllerSize)
        midCtrl, midCtrlGrp = CreateCircleControllerForJnt(midJnt, "fk_" + self.nameBase, self.controllerSize)
        endCtrl, endCtrlGrp = CreateCircleControllerForJnt(endJnt, "fk_" + self.nameBase, self.controllerSize)

        mc.parent(endCtrlGrp, midCtrl)
        mc.parent(midCtrlGrp, rootCtrl)

        endIkCtrl, endIkCtrlGrp = CreateBoxControllerForJnt(endJnt, "ik_" + self.nameBase, self.controllerSize)

        ikFkBlendCtrlPrefix = self.nameBase + "_ikfkBlend"
        ikFkBlendController = CreatePlusController(ikFkBlendCtrlPrefix, self.blendControllerSize)
        ikFkBlendController, ikFkBlendControllerGrp = ConfigureCtrlForJnt(rootJnt, ikFkBlendController, False)

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikFkBlendController, ln=ikfkBlendAttrName, min=0, max=1, k=True)

        ikHandleName = "ikHandle_" + self.nameBase 
        mc.ikHandle(n=ikHandleName, sj = rootJnt, ee=endJnt, sol="ikRPsolver")

        rootJntLoc = GetObjectPositionAsVec(rootJnt)
        endJntLoc = GetObjectPositionAsVec(endJnt)

        poleVectorVals = mc.getAttr(f"{ikHandleName}.poleVector")[0]
        poleVecDir = MVector(poleVectorVals[0], poleVectorVals[1], poleVectorVals[2])
        poleVecDir.normalize() # make it a unit vector, a vector that has a length of 1

        rootToEndVec = endJntLoc - rootJntLoc
        rootToEndDist = rootToEndVec.length()

        poleVectorCtrlLoc = rootJntLoc + rootToEndVec/2.0 + poleVecDir * rootToEndDist

        poleVectorCtrlName = "ac_ik" + self.nameBase + "poleVector"
        mc.spaceLocator(n=poleVectorCtrlName)

        poleVectorCtrlGrpName = poleVectorCtrlName + "_grp"
        mc.group(poleVectorCtrlName, n= poleVectorCtrlGrpName)

        mc.setAttr(f"{poleVectorCtrlGrpName}.translate", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, type="double3")
        mc.poleVectorConstraint(poleVectorCtrlName, ikHandleName)

        mc.parent(ikHandleName, endIkCtrl)
        mc.setAttr(f"{ikHandleName}.v", 0)

        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{ikHandleName}.ikBlend")
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{endIkCtrlGrp}.v")
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{poleVectorCtrlGrpName}.v")

        reverseNodeName = f"{self.nameBase}_reverse"
        mc.createNode("reverse", n=reverseNodeName)
        
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{reverseNodeName}.inputX")
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{rootCtrlGrp}.v")

        orientConstraint = None
        wristConnections = mc.listConnections(endJnt)
        for connection in wristConnections:
            if mc.objectType(connection) == "orientConstraint":
                orientConstraint = connection
                break
        
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{orientConstraint}.{endIkCtrl}W1")
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{orientConstraint}.{endCtrl}W0")

        topGrpName = f"{self.nameBase}_rig_grp"
        mc.group(n=topGrpName, empty=True)

        mc.parent(rootCtrlGrp, topGrpName)
        mc.parent(ikFkBlendControllerGrp, topGrpName)
        mc.parent(endIkCtrlGrp, topGrpName)
        mc.parent(poleVectorCtrlGrpName, topGrpName)

        mc.setAttr(f"{topGrpName}.overrideEnabled", 1) #overrides display attribute
        mc.setAttr(f"{topGrpName}.overrideRGBColors", 1) #overrides attribute RGB colors instead of index
        r, g, b = self.controlColorRGB #sets the color to what was selected
        mc.setAttr(f"{topGrpName}.overrideColorRGB", r, g, b) # sets the actual color

        self.ApplyColorToControls(topGrpName) #applies color to the group

def Run():
    limbRiggerWidget = LimbRiggerWidget()
    limbRiggerWidget.show()

Run()

