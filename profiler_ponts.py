from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class ProfilerPonts(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('berges', 'Lignes de berges', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterVectorLayer('ponts', 'Ponts linéaires', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterNumber('extension', 'Distance d\'extension des ponts (m)', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=100, defaultValue=20))
        self.addParameter(QgsProcessingParameterNumber('distance', 'Distance de décalage (m)', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=100, defaultValue=50))
        self.addParameter(QgsProcessingParameterVectorDestination('OUTPUT', 'Ponts décalés'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        
        # entrées
        ponts = parameters['ponts']
        berges = parameters['berges']
        
        # sorties
        lines = []
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        # paramètres
        extension = parameters['extension']
        distance = parameters['distance']
        
        # traitement
        id = 0
        for pont_f in ponts.getFeatures():
            pont_g = pont_f.geometry().extendLine(extension,extension) # extension du pont pour assurer son intersection avec les berges
            l0 = []
            l1 = []
            l2 = []
            for berge_f in berges.getFeatures(): # pour chaque pont on traite une berge, puis l'autre
                berge_g = berge_f.geometry()
                if berge_g.intersects(pont_g): # on vérifie l'intersection, si absence d'intersection on renvoie une erreur et on stoppe l'algorithme
                    point_g = berge_g.intersection(pont_g)
                    line_distance = berge_g.lineLocatePoint(point_g)
                    p1, p2 = berge_g.interpolate(line_distance+distance), berge_g.interpolate(line_distance-distance)
                    l0.append(p1.asPoint())
                    l1.append(point_g.asPoint())
                    l2.append(p2.asPoint())
                else:
                    feedback.reportError("Le pont %s n'intersecte pas avec les berges !" % pont_f.id(), True)
                    return {}
            lines.append((QgsGeometry.fromPolylineXY(l0), [id, 'Profil']))
            lines.append((QgsGeometry.fromPolylineXY(l1), [id, 'Pont']))
            lines.append((QgsGeometry.fromPolylineXY(l2), [id, 'Profil']))
            id += 1
            
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # écriture des données en sortie
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("type", QVariant.String))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.LineString, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")
        for line, attributes in lines:
            f = QgsFeature()
            f.setGeometry(line)
            f.setAttributes(attributes)
            writer.addFeature(f)
            
        feedback.setCurrentStep(2)
        
        results['OUTPUT']=output
        return results
                

    def name(self):
        return 'Profiler les ponts'

    def displayName(self):
        return 'Profiler les ponts'

    def group(self):
        return 'Stage IGN'

    def groupId(self):
        return 'Stage IGN'

    def createInstance(self):
        return ProfilerPonts()
