import sys
import os
import fileinput
from shutil import copyfile
from PySide import QtGui
from src.view import View
from src.scene import Scene
from src.model import *

from aether.diagnostics import set_diagnostics_on
from aether.geometry import define_elem_geometry_2d, define_node_geometry_2d,define_data_geometry, define_rad_from_file, define_rad_from_geom, append_units
from aether.exports import export_node_geometry_2d, export_elem_geometry_2d,export_data_geometry
from aether.surface_fitting import fit_surface_geometry
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT

app = QtGui.QApplication(sys.argv)
scene = Scene()

datacloudModel = FileModel(scene, 'datacloud')
surfaceModel = FileModel(scene, 'surface')

# the keys in these dicts correspond to the accessibleName in Qt
landmarkCoords = {}
landmarkModels = {}
landmarkMaterials = {
    'apex': 'green',
    'basal': 'red',
    'lateral': 'blue',
    'ventral': 'yellow',
}

# callback functions for actions: load, show, landmark, fit, save
def load(ipdata, ipnode, ipelem):
    if ipdata:
        data = os.path.splitext(ipdata)[0]
        try:
            os.remove(data + '.exdata')
        except OSError:
            pass

        define_data_geometry(data)
        export_data_geometry(data, 'fitted')

        datacloudModel.load(data + '.exdata')
        datacloudModel.visualizePoints('nodes', 'white', 0)

    if ipnode and ipelem:
        node = os.path.splitext(ipnode)[0]
        elem = os.path.splitext(ipelem)[0]
        try:
            os.remove(node + '.exnode')
        except OSError:
            pass

        try:
            os.remove(elem + '.exelem')
        except OSError:
            pass

        define_node_geometry_2d(ipnode)
        define_elem_geometry_2d(elem, 'unit')
        export_node_geometry_2d(node, 'fitted', 0)
        export_elem_geometry_2d(elem, 'fitted', 0, 0)

        surfaceModel.load(node + '.exnode', elem + '.exelem')
        surfaceModel.visualizeLines('lines', 'gold')
        surfaceModel.visualizeSurfaces('lines', 'transBlue')

def show(datacloud, mesh):
    datacloudModel.setVisibility(datacloud)
    surfaceModel.setVisibility(mesh)

def landmark(widget, landmark, x, y):
    selectTol = 5  # number of pixels around clicked area that are probed for datacloud points
    sceneviewer = widget.getSceneviewer()
    scenepicker = widget.getScenepicker()
    scenepicker.setSceneviewerRectangle(sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
        x - selectTol, y - selectTol, x + selectTol, y + selectTol)

    graphics = scenepicker.getNearestGraphics()
    if graphics.getType() == 1:  # selecting node
        node = scenepicker.getNearestNode()
        coords = datacloudModel.getNodeCoordinates(node.getIdentifier())
        
        if landmark not in landmarkModels:
            landmarkModels[landmark] = NodeModel(scene, landmark)
        model = landmarkModels[landmark]
        model.setNodeCoordinates(1, coords)
        model.visualizePoints('nodes', landmarkMaterials[landmark], 6)  # 6 is the size of the sphere
        
        if landmark not in landmarkCoords:
            landmarkCoords[landmark] = coords

        print('Setting landmark %s to %s' % (landmark, coords))
        return True
    return False

def fit(ipdata, ipnode, ipelem, iterations):
    for landmark in landmarkCoords:
        coords = landmarkCoords[landmark]
        print('Fitting with landmark %s = %s' % (landmark, coords))

    mapname = 'example/LUL_map'

    elem = os.path.splitext(ipelem)[0]
    data = os.path.splitext(ipdata)[0]
    define_node_geometry_2d(ipnode)
    define_elem_geometry_2d(elem, 'unit')
    define_data_geometry(data)

    fit_surface_geometry(iterations, mapname)

    export_node_geometry_2d('.tmp', 'fitted', 0)
    export_elem_geometry_2d('.tmp', 'fitted', 0, 0)

    f = fileinput.FileInput('.tmp.exnode', inplace=True)
    for line in f:
        print(line.replace('************', '0.0'))
    f.close()

    surfaceModel.load('.tmp.exnode', '.tmp.exelem')

def save(exnode, exelem):
    node = os.path.splitext(exnode)[0]
    elem = os.path.splitext(exelem)[0]
    export_node_geometry_2d(node, 'fitted', 0)
    export_elem_geometry_2d(elem, 'fitted', 0, 0)
    print('Saved mesh as %s and %s' % (exnode, exelem))


view = View(scene)
view.loadCallback(load)
view.showCallback(show)
view.landmarkCallback(landmark)
view.fitCallback(fit)
view.saveCallback(save)
view.setOutputs('out.exnode', 'out.exelem')
view.setInfo("""
<h2>Lung fitting</h2>
<p>This GUI provides an easy interface for the surface_fitting Fortran code in lungsim. It allows the visualization of the data cloud and fitted surface mesh and allows configuring the fitting algorithm.</p>
<p>Created for use within the Auckland Bioengineering Institute at the University of Auckland.</p>
<h3>Usage</h3>
<p>Select the data cloud (.ipdata) and template mesh (.ipnode and .ipelem) files and press Load. Both the data cloud and surface mesh are visible in the 3D view and their visibility can be toggled with the checkboxes.</p>
<p>The number of iterations can be set for the fitting algorithm and optionally there is the possibility to select landmark nodes to supply to the fitting algorithm (not yet supported). Click on the Fit button to start the fitting procedure with its output redirected to the console.</p>
<p>You can select landmarks by hiding the surface mesh and then clicking one of the landmark buttons. Then click on a data cloud point to select the location for the landmark node. Do this for all landmarks and the nodes will show up with matching colors.</p>
<p>When the surface mesh has a good fit with the data cloud you can export the data by clicking Save after selecting the output file names (.exnode and .exelem).</p>
""")
view.show()
sys.exit(app.exec_())


# Print errors
num = model._logger.getNumberOfMessages()
for i in range(0, num):
    print model._logger.getMessageTextAtIndex(i)
