from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class ProfilsDepuisLignes(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('lignes', 'Lignes', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterRasterLayer('mnt', 'MNT'))
        self.addParameter(QgsProcessingParameterNumber('echantillons_nb', 'Nombre d\'Échantillons', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=99, defaultValue=20))
        self.addParameter(QgsProcessingParameterVectorDestination('OUTPUT', 'Profils'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        
        # entrées
        lignes = parameters['lignes']
        mnt = parameters['mnt']
        
        # sorties
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        profils = []

        # paramètres
        echantillons_nb = parameters['echantillons_nb']
        
        # traitement
        for ligne_f in lignes.getFeatures():
            ligne_g = ligne_f.geometry()
            freq = ligne_g.length()/(echantillons_nb-1)
            echantillons_g = [QgsGeometry().fromPointXY(ligne_g.asMultiPolyline()[0][0])]
            for i in range(1, echantillons_nb-1):
                echantillons_g.append(ligne_g.interpolate(freq*i))
            echantillons_g.append(QgsGeometry().fromPointXY(ligne_g.asMultiPolyline()[0][-1]))
            feedback.pushInfo(str(echantillons_g))
            elevations = []
            for echantillon_g in echantillons_g:
                elevation = mnt.dataProvider().sample(echantillon_g.asPoint(), 1)[0]
                elevations.append(elevation)
            profils.append([echantillons_g, ligne_f.attributes(), elevations])
            
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # écriture des données en sortie
        fields = lignes.fields()
        fields.append(QgsField("elevation", QVariant.Double))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")
        for echantillons_g, attributes, elevations in profils:
            for echantillon_g, elevation in zip(echantillons_g, elevations): 
                f = QgsFeature()
                f.setGeometry(echantillon_g)
                echantillon_att = attributes
                echantillon_att.append(elevation)
                f.setAttributes(echantillon_att)
                writer.addFeature(f)
            
        feedback.setCurrentStep(2)
        
        results['OUTPUT']=output
        return results
                

    def name(self):
        return 'Profils depuis des lignes'

    def displayName(self):
        return 'Profils depuis des lignes'

    def group(self):
        return 'Stage IGN'

    def groupId(self):
        return 'Stage IGN'

    def createInstance(self):
        return ProfilsDepuisLignes()
