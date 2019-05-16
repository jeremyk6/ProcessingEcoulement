from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingOutputHtml, QgsProcessingParameterVectorLayer, QgsProcessingOutputHtml, QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber, QgsProcessingParameterFileDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class ComparerProfils(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils', types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFileDestination('OUTPUT', 'Comparaison', 'HTML files (*.html)'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        
        # entrées
        points = parameters['profils']
        
        # sorties
        output = self.parameterAsFileOutput(parameters, 'OUTPUT', context)
        
        # traitement
        
        html = "<html>"
        html += "<head>"
        html += '''<style>
        table {
          border-collapse: collapse;
        }

        table, th, td {
          border: 1px solid black;
        }
        </style>
        '''
        html += "</head>"
        html += "<body>"
        for npont in range(5): # traitement par pont
            html += "<p>Pont %s<br/>"%npont
            html += "<table>"
            html += "<tr>"
            moyenne_pont = 0
            for nordre in range(20): # traitement par ordre du point dans le pont
                pts = []
                for point_f in points.getFeatures("pont = %s and ordre = %s"%(npont,nordre)): # traitement des 3 points du même ordre
                    pts.append(point_f.attributes()[-1])
                moyenne_points = (abs(pts[0]-pts[1])+abs(pts[0]-pts[2])+abs(pts[1]-pts[2]))/3
                moyenne_pont += moyenne_points
                html += "<td>%s</td>"%round(moyenne_points,2)
            html += "</tr>"
            html += "</table>"
            moyenne_pont /= 20
            html += "Moyenne des écarts sur le pont : %s</p>"%round(moyenne_pont,2)
                
        html += "</body>"
        html += "</html>"
        file = open(output, "w")
        file.write(html)
        file.close()
        
        
        results['OUTPUT']=output
        return results

    def name(self):
        return 'Comparer des profils'

    def displayName(self):
        return 'Comparer des profils'

    def group(self):
        return 'Stage IGN'

    def groupId(self):
        return 'Stage IGN'

    def createInstance(self):
        return ComparerProfils()
