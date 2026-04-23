import maya.cmds as mc
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Qt
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance

def GetMayaMainWindow()->QMainWindow: #gets mayas main window
    mayaMainWindow = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaMainWindow), QMainWindow)

def RemoveWidgetWithName(objectname):
    for widget in GetMayaMainWindow().findChildren(QWidget, objectname):
        widget.deleteLater()

class MayaWidget(QWidget): #inheritance
    def __init__(self):
        super().__init__(parent=GetMayaMainWindow())
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Maya Widget") # makes a window for the widget
        RemoveWidgetWithName(self.GetWidgetHash())
        self.setObjectName(self.GetWidgetHash())

    def GetWidgetHash(self):
        return "9ba372a377f74ec83756c0bb38071e4f9fca3fb597f64b1b23af44c6d70191b9"
