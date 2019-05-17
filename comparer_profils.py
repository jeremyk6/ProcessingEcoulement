from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingOutputHtml, QgsProcessingParameterVectorLayer, QgsProcessingOutputHtml, QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber, QgsProcessingParameterFileDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing
import statistics
from yattag import Doc, indent

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
        nombre_ponts = 3
        nombre_points = 20
        
        # sorties
        output = self.parameterAsFileOutput(parameters, 'OUTPUT', context)
        doc, tag, text, line = Doc().ttl()
        
        # traitement
        moyennes_ecarts = []
        ecarts_types = []
        for npont in range(nombre_ponts): # traitement par pont
            me = []
            et = []
            for nordre in range(nombre_points): # traitement par ordre du point dans le pont
                pts = []
                i = 0
                for point_f in points.getFeatures("pont = %s and ordre = %s"%(npont,nordre)): # traitement des 3 points du même ordre
                    pts.append(point_f.attributes()[-1])
                    i += 1
                me.append((abs(pts[0]-pts[1])+abs(pts[0]-pts[2])+abs(pts[1]-pts[2]))/3) # moyenne des écarts sur le point
                et.append(statistics.stdev(pts))
            moyennes_ecarts.append(me)
            ecarts_types.append(et)
        
        # ecriture du document HTML
        with tag('html'):
            with tag('head'):
                with tag('style'):
                    text('p, h1 { margin: 10px; } table, th, td { border-collapse: collapse; border: 1px solid black; padding: 5px; }')
            with tag('body'):
                for npont in range(nombre_ponts): # traitement par pont
                    line('h1', 'Pont %s'%npont)
                    with tag('table'):
                        with tag('tr'):
                            line('td', 'Moyennes des écarts')
                            for nordre in range(nombre_points): # traitement par ordre du point dans le pont
                                line('td', round(moyennes_ecarts[npont][nordre], 2))
                        with tag('tr'):
                            line('td', 'Écarts types')
                            for nordre in range(nombre_points): # traitement par ordre du point dans le pont
                                line('td', round(ecarts_types[npont][nordre], 2))
                    line('p', 'Moyenne des moyennes des écarts sur le pont : %s'%round(statistics.mean(moyennes_ecarts[npont]), 2))
                    line('p', 'Moyenne des écarts types sur le pont : %s'%round(statistics.mean(ecarts_types[npont]), 2))
        file = open(output, "w")
        file.write(indent(doc.getvalue()))
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
