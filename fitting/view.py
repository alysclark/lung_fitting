from PySide import QtGui, QtCore
from .ui_view import Ui_View
import os

class View(QtGui.QWidget):
    def __init__(self, scene, parent=None):
        super(View, self).__init__(parent)
        self._inputFilenames = ['', '', '']
        self._outputFilenames = ['', '']
        self._path = '.'
        self._info = ''
        self._loadCallback = None
        self._showCallback = None
        self._landmarkCallback = None
        self._fitCallback = None
        self._saveCallback = None

        self._ui = Ui_View()
        self._ui.setupUi(self)

        self._scene = scene
        self._ui.sceneviewer_widget.setContext(scene.getContext())
        self._makeConnections()

    def setInfo(self, info):
        self._info = info

    def loadCallback(self, cb):
        self._loadCallback = cb

    def showCallback(self, cb):
        self._showCallback = cb

    def landmarkCallback(self, cb):
        self._landmarkCallback = cb

    def fitCallback(self, cb):
        self._fitCallback = cb

    def saveCallback(self, cb):
        self._saveCallback = cb

    def _makeConnections(self):
        self._ui.sceneviewer_widget.graphicsInitialized.connect(self._graphicsUpdate)
        self._ui.datacloudIpdata_pushButton.clicked.connect(self._datacloudIpdataClicked)
        self._ui.surfaceIpnode_pushButton.clicked.connect(self._surfaceIpnodeClicked)
        self._ui.surfaceIpelem_pushButton.clicked.connect(self._surfaceIpelemClicked)
        self._ui.load_pushButton.clicked.connect(self._loadClicked)
        self._ui.outputExnode_pushButton.clicked.connect(self._outputExnodeClicked)
        self._ui.outputExelem_pushButton.clicked.connect(self._outputExelemClicked)
        self._ui.fit_pushButton.clicked.connect(self._fitClicked)
        self._ui.save_pushButton.clicked.connect(self._saveClicked)
        self._ui.showDatacloud_checkBox.clicked.connect(self._showClicked)
        self._ui.showMesh_checkBox.clicked.connect(self._showClicked)
        self._ui.info_pushButton.clicked.connect(self._infoClicked)

        self._ui.info_pushButton.setIcon(QtGui.QIcon.fromTheme('dialog-information'))
        self._ui.info_pushButton.setText('')

        self._originalSceneviewerMousePressEvent = self._ui.sceneviewer_widget.mousePressEvent
        self._ui.sceneviewer_widget.mousePressEvent = self._sceneviewerMousePressEvent

        self._landmarksGroup = QtGui.QButtonGroup(self)
        for landmark_pushButton in self._ui.landmarks_groupBox.children():
            if type(landmark_pushButton) == QtGui.QPushButton:
                self._landmarksGroup.addButton(landmark_pushButton)
                landmark_pushButton.pressed.connect(self._landmarkButtonPressed)
                landmark_pushButton.released.connect(self._landmarkButtonReleased)

    def _graphicsUpdate(self):
        sceneviewer = self._ui.sceneviewer_widget.getSceneviewer()
        if sceneviewer is not None:
            self._ui.sceneviewer_widget.setScene(self._scene.getScene())
            sceneviewer.setLookatParametersNonSkew([1.9, -4.5, 2.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            sceneviewer.setTransparencyMode(sceneviewer.TRANSPARENCY_MODE_SLOW)
            sceneviewer.viewAll()

    def _datacloudIpdataClicked(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Open data cloud ipdata file', dir=self._path, filter='*.ipdata')
        if filename:
            self._ui.datacloudIpdata_lineEdit.setText(os.path.relpath(filename, os.getcwd()))
            self._inputFilenames[0] = str(filename)
            self._path = os.path.dirname(filename)

    def _surfaceIpnodeClicked(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Open surface ipnode file', dir=self._path, filter='*.ipnode')
        if filename:
            self._ui.surfaceIpnode_lineEdit.setText(os.path.relpath(filename, os.getcwd()))
            self._inputFilenames[1] = str(filename)
            self._path = os.path.dirname(filename)

    def _surfaceIpelemClicked(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Open surface ipelem file', dir=self._path, filter='*.ipelem')
        if filename:
            self._ui.surfaceIpelem_lineEdit.setText(os.path.relpath(filename, os.getcwd()))
            self._inputFilenames[2] = str(filename)
            self._path = os.path.dirname(filename)
    
    def _infoClicked(self):
        QtGui.QMessageBox.information(self, 'Information', self._info)

    def _loadClicked(self):
        if self._loadCallback:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self._loadCallback(self._inputFilenames[0], self._inputFilenames[1], self._inputFilenames[2])
            self._graphicsUpdate()
            QtGui.QApplication.restoreOverrideCursor()
    
    def _showClicked(self):
        if self._showCallback:
            datacloud = self._ui.showDatacloud_checkBox.isChecked()
            mesh = self._ui.showMesh_checkBox.isChecked()
            self._showCallback(datacloud, mesh)
    
    def _landmarkButtonPressed(self):
        button = self.sender()
        checkedButton = self._landmarksGroup.checkedButton()
        if checkedButton != None and checkedButton.objectName() == button.objectName():
            self._landmarksGroup.setExclusive(False)

    def _landmarkButtonReleased(self):
        button = self.sender()
        if self._landmarksGroup.exclusive() == False:
            button.setChecked(False)
            self._landmarksGroup.setExclusive(True)

    def setOutputs(self, exnode, exelem):
        self._ui.outputExnode_lineEdit.setText(os.path.relpath(exnode, os.getcwd()))
        self._ui.outputExelem_lineEdit.setText(os.path.relpath(exelem, os.getcwd()))
        self._outputFilenames[0] = str(exnode)
        self._outputFilenames[1] = str(exelem)
    
    def _outputExnodeClicked(self):
        filename, _ = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Save output exnode file', dir=self._path, filter='*.exnode')
        if filename:
            self._ui.outputExnode_lineEdit.setText(os.path.relpath(filename, os.getcwd()))
            self._outputFilenames[0] = str(filename)
            self._path = os.path.dirname(filename)

    def _outputExelemClicked(self):
        filename, _ = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Save output exelem file', dir=self._path, filter='*.exelem')
        if filename:
            self._ui.outputExelem_lineEdit.setText(os.path.relpath(filename, os.getcwd()))
            self._outputFilenames[1] = str(filename)
            self._path = os.path.dirname(filename)

    def _fitClicked(self):
        if self._fitCallback:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            iterations = self._ui.iterations_spinBox.value()
            self._fitCallback(self._inputFilenames[0], self._inputFilenames[1], self._inputFilenames[2], iterations)
            QtGui.QApplication.restoreOverrideCursor()

    def _saveClicked(self):
        if self._saveCallback:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self._saveCallback(self._outputFilenames[0], self._outputFilenames[1])
            QtGui.QApplication.restoreOverrideCursor()

    def _sceneviewerMousePressEvent(self, event):
        self._originalSceneviewerMousePressEvent(event)
        
        if self._landmarksGroup.checkedButton() != None:
            landmark = self._landmarksGroup.checkedButton().accessibleName()
            success = True
            if self._landmarkCallback != None:
                x = event.x();
                y = event.y();
                success = self._landmarkCallback(self._ui.sceneviewer_widget, landmark, x, y)
            
            if success:
                self._landmarksGroup.setExclusive(False)
                self._landmarksGroup.checkedButton().setChecked(False)
                self._landmarksGroup.setExclusive(True)
