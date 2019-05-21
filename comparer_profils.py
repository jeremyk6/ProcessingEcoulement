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
        
        # sorties
        output = self.parameterAsFileOutput(parameters, 'OUTPUT', context)
        doc, tag, text, line = Doc().ttl()
        donnees_html = []

        # attributs
        rasters = points.uniqueValues(points.dataProvider().fields().indexFromName('raster'))
        ponts = points.uniqueValues(points.dataProvider().fields().indexFromName('pont'))
        npoints = len(points.uniqueValues(points.dataProvider().fields().indexFromName('ordre')))
        
        # traitement
        tableau = []
        for pont in ponts: # traitement par pont
            t_pont = []
            for raster in rasters:
                t_raster = []
                t_raster.append([''])
                t_raster.append(['Ecart profil 1 - pont'])
                t_raster.append(['Ecart profil 2 - pont'])
                t_raster.append(['Ecart profil 1 - profil 2'])
                for i in range(npoints):
                    t_raster[0].append(i)
                t_raster[0].append('Moyenne')
                t_raster[0].append('Ecart-type')
                for nordre in range(npoints): # traitement par ordre du point dans le pont
                    pts = [] # traitement des 3 points du même ordre
                    for point_f in points.getFeatures("pont = %s and raster = '%s' and ordre = %s"%(pont, raster, nordre)):
                        pts.append(point_f.attributes()[-1]) 
                    ecart_p1_pont = (abs(pts[0]-pts[1])) # ecart entre le premier profil et le pont
                    ecart_p2_pont = (abs(pts[2]-pts[1])) # ecart entre le second profil et le pont
                    ecart_p1_p2   = (abs(pts[0]-pts[2])) # ecart entre les deux profils
                    t_raster[1].append(ecart_p1_pont)
                    t_raster[2].append(ecart_p2_pont)
                    t_raster[3].append(ecart_p1_p2)
                t_raster[1] += [statistics.mean(t_raster[1][1:-1]), statistics.stdev(t_raster[1][1:-1])]
                t_raster[2] += [statistics.mean(t_raster[2][1:-1]), statistics.stdev(t_raster[2][1:-1])]
                t_raster[3] += [statistics.mean(t_raster[3][1:-1]), statistics.stdev(t_raster[3][1:-1])]
                t_pont.append(t_raster)
            tableau.append(t_pont)
        
        # ecriture du document HTML
        with tag('html'):
            with tag('head'):
                with tag('style'):
                    text('p, h1 { margin: 10px; } table, th, td { border-collapse: collapse; border: 1px solid black; padding: 5px; }')
            with tag('body'):
                i_pont = 0
                for pont in ponts: # traitement par pont
                    line('h1', 'Pont %s'%pont)
                    i_raster = 0
                    for raster in rasters:
                        line('h2', raster)
                        with tag('table'):
                            for ligne in tableau[i_pont][i_raster]:
                                with tag('tr'):
                                    for cellule in ligne:
                                        if type(cellule) is not str:
                                            cellule = str(round(cellule, 2)) 
                                        line('td', cellule)
                        i_raster += 1
                    i_pont += 1
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
