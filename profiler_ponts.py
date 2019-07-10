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
        ponts = self.parameterAsVectorLayer(parameters, 'ponts', context)
        berges = self.parameterAsVectorLayer(parameters, 'berges', context)
        
        # sorties
        lines = []
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        # paramètres
        extension = parameters['extension']
        distance = parameters['distance']
        
        # traitement
        pont = 0
        for pont_f in ponts.getFeatures():
            pont_g = pont_f.geometry().extendLine(extension,extension) # extension du pont pour assurer son intersection avec les berges
            l0 = []
            l1 = []
            l2 = []
            bcount = 0
            for berge_f in berges.getFeatures(): # pour chaque pont on traite une berge, puis l'autre
                berge_g = berge_f.geometry()
                if berge_g.intersects(pont_g): # on vérifie l'intersection, si absence d'intersection on renvoie une erreur et on stoppe l'algorithme
                    point_g = berge_g.intersection(pont_g)
                    line_distance = berge_g.lineLocatePoint(point_g)
                    p1, p2 = berge_g.interpolate(line_distance+distance), berge_g.interpolate(line_distance-distance)
                    l1.append(point_g.asPoint())
                    if(bcount == 1 and (QgsGeometry.fromPolylineXY([l0[0], p1.asPoint()]).length() > QgsGeometry.fromPolylineXY([l0[0], p2.asPoint()]).length())):
                        l0.append(p2.asPoint())
                        l2.append(p1.asPoint())
                    else:
                        l0.append(p1.asPoint())
                        l2.append(p2.asPoint())
                    bcount += 1
            if bcount != 2:
                feedback.reportError("Le pont %s n'intersecte pas avec les berges !" % pont_f.id(), True)
                return {}
            lines.append((QgsGeometry.fromPolylineXY(l0), [0, pont, 'Profil']))
            lines.append((QgsGeometry.fromPolylineXY(l1), [1, pont, 'Pont']))
            lines.append((QgsGeometry.fromPolylineXY(l2), [2, pont, 'Profil']))
            pont += 1
            
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # écriture des données en sortie
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("pont", QVariant.Int))
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
        return 'Créer des profils de validation de ponts linéaires'

    def displayName(self):
        return 'Créer des profils de validation de ponts linéaires'

    def group(self):
        return 'Boîte à outils ponts'

    def groupId(self):
        return 'Boîte à outils ponts'

    def createInstance(self):
        return ProfilerPonts()
