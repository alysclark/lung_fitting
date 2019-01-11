import os

from scaffoldmaker.utils.zinc_utils import *

from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.element import Element
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
    

class Model(object):
    def __init__(self, scene, name):
        self._context = scene.getContext()
        self._materialModule = self._context.getMaterialmodule()

        defaultRegion = self._context.getDefaultRegion()
        regionName = defaultRegion.findChildByName(name).getName()
        if regionName != None:
            defaultRegion.removeChild(region)
        self._region = defaultRegion.createChild(name)

        self._scene = self._region.getScene()
        self._field = None

    def setVisibility(self, visible):
        self._scene.setVisibilityFlag(visible)

    def setField(self, field):
        self._field = field

    def getNodeCoordinates(self, nid):
        fieldModule = self._region.getFieldmodule()
        nodeSet = fieldModule.findNodesetByName('nodes')
        node = nodeSet.findNodeByIdentifier(nid)
        fieldCache = fieldModule.createFieldcache()
        fieldCache.setNode(node)
        x = self._field.getNodeParameters(fieldCache, 1, Node.VALUE_LABEL_VALUE, 1, 1)
        y = self._field.getNodeParameters(fieldCache, 2, Node.VALUE_LABEL_VALUE, 1, 1)
        z = self._field.getNodeParameters(fieldCache, 3, Node.VALUE_LABEL_VALUE, 1, 1)
        return [x[1], y[1], z[1]]

    def visualizePoints(self, name, material, size=2):
        graphics = self._scene.createGraphicsPoints()
        graphics.setCoordinateField(self._field)
        graphics.setMaterial(self._materialModule.findMaterialByName(material))
        graphics.setName(name)
        graphics.setFieldDomainType(Field.DOMAIN_TYPE_NODES)

        samplingAttr = graphics.getGraphicssamplingattributes()
        samplingAttr.setElementPointSamplingMode(Element.POINT_SAMPLING_MODE_SET_LOCATION)
        samplingAttr.setLocation([0.0])

        if size > 0:
            glyph = self._context.getGlyphmodule().findGlyphByGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
            pointAttr = graphics.getGraphicspointattributes()
            pointAttr.setGlyph(glyph)
            pointAttr.setBaseSize([size, size, size])

    def visualizeLines(self, name, material):
        graphics = self._scene.createGraphicsLines()
        graphics.setCoordinateField(self._field)
        graphics.setMaterial(self._materialModule.findMaterialByName(material))
        graphics.setName(name)

    def visualizeSurfaces(self, name, material):
        graphics = self._scene.createGraphicsSurfaces()
        graphics.setCoordinateField(self._field)
        graphics.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        graphics.setMaterial(self._materialModule.findMaterialByName(material))
        graphics.setName(name)


class NodeModel(Model):
    def __init__(self, scene, name):
        Model.__init__(self, scene, name)
        
        fieldModule = self._region.getFieldmodule()
        field = fieldModule.createFieldFiniteElement(3)
        field.setName('coordinates')
        field.setManaged(True)
        self._nodeSet = fieldModule.findNodesetByName('nodes')
        self._nodeTemplate = self._nodeSet.createNodetemplate()
        self._nodeTemplate.defineField(field)

        self.setField(field)
    
    def setNodeCoordinates(self, nid, coords):
        node = self._nodeSet.findNodeByIdentifier(nid)
        if node.getIdentifier() == -1:
            node = self._nodeSet.createNode(nid, self._nodeTemplate)

        fieldModule = self._region.getFieldmodule()
        fieldCache = fieldModule.createFieldcache()
        fieldCache.setNode(node)
        self._field.setNodeParameters(fieldCache, 1, Node.VALUE_LABEL_VALUE, 1, coords[0])
        self._field.setNodeParameters(fieldCache, 2, Node.VALUE_LABEL_VALUE, 1, coords[1])
        self._field.setNodeParameters(fieldCache, 3, Node.VALUE_LABEL_VALUE, 1, coords[2])
        

class FileModel(Model):
    def __init__(self, scene, name):
        Model.__init__(self, scene, name)

    def load(self, ex1, ex2=None):
        self._region.readFile(ex1)
        if ex2 != None:
            self._region.readFile(ex2)

        fieldModule = self._region.getFieldmodule()
        field = fieldModule.findFieldByName('coordinates').castFiniteElement()
        self.setField(field)

