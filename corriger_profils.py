from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterMultipleLayers, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
from statistics import mean
import processing

class CorrigerProfils(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterNumber('nlissage', 'Nombre d\'entités à lisser', type=QgsProcessingParameterNumber.Integer, minValue=2, defaultValue=2))

    def processAlgorithm(self, parameters, context, model_feedback):
        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        
        # entrées
        profils = self.parameterAsVectorLayer(parameters, 'profils', context)
        nlissage = self.parameterAsInt(parameters, 'nlissage', context)
        feedback.pushInfo(str(profils))
        
        # sorties
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        # traitement
        azimuths = []
        nazimuths = []

        profils.startEditing()
        for profil in profils.getFeatures():
                pg1 = profil.geometry()
                pl1 = pg1.asPolyline()
                azimuths.append(pl1[0].azimuth(pl1[1]))
                nazimuths.append(pl1[0].azimuth(pl1[1]))
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        for i in range(len(azimuths)-nlissage+1):
            m = mean(nazimuths[i:i+nlissage])
            nazimuths[i:i+nlissage] = [m]*nlissage
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        for profil, azimuth, nazimuth in zip(profils.getFeatures(),azimuths,nazimuths):
            transform = azimuth-nazimuth
            pg1 = profil.geometry()
            pg1.rotate(-transform, pg1.centroid().asPoint())
            profil.setGeometry(pg1)
            profils.updateFeature(profil)     
        profils.commitChanges()
        feedback.setCurrentStep(3)

        return {}
                

    def name(self):
        return 'Corriger les profils'

    def displayName(self):
        return 'Corriger les profils'

    def group(self):
        return 'Stage IGN'

    def groupId(self):
        return 'Stage IGN'

    def createInstance(self):
        return CorrigerProfils()
