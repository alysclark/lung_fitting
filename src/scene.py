from opencmiss.zinc.context import Context
from opencmiss.zinc.material import Material

from .model import Model

class Scene(object):

    def __init__(self):
        self._context = Context("Scene")
        self._initialize()

    def getContext(self):
        return self._context

    def getScene(self):
        return self._context.getDefaultRegion().getScene()

    def _initialize(self):
        tess = self._context.getTessellationmodule().getDefaultTessellation()
        tess.setRefinementFactors(12)

        self._materialModule = self._context.getMaterialmodule()
        self._materialModule.defineStandardMaterials()

        material = self._materialModule.createMaterial()
        material.setName('solidBlue')
        material.setManaged(True)
        material.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.0, 0.2, 0.6])
        material.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.0, 0.7, 1.0])
        material.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        material.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.1, 0.1, 0.1])
        material.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)

        material = self._materialModule.createMaterial()
        material.setName('transBlue')
        material.setManaged(True)
        material.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.0, 0.2, 0.6])
        material.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.0, 0.7, 1.0])
        material.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        material.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.1, 0.1, 0.1])
        material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.3)
        material.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)

        material = self._materialModule.createMaterial()
        material.setName('solidTissue')
        material.setManaged(True)
        material.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.9, 0.7, 0.5])
        material.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.9, 0.7, 0.5])
        material.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        material.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.2, 0.2, 0.3])
        material.setAttributeReal(Material.ATTRIBUTE_ALPHA, 1.0)
        material.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)

        glyphmodule = self._context.getGlyphmodule()
        glyphmodule.defineStandardGlyphs()

