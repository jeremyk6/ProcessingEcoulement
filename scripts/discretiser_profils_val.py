# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterMultipleLayers, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class ProfilsDepuisLignes(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('lignes', 'Profils de validation', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterMultipleLayers('rasters', 'Rasters', layerType=QgsProcessing.TypeRaster))
        self.addParameter(QgsProcessingParameterNumber('echantillons_nb', 'Nombre d\'échantillons', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=99, defaultValue=20))
        self.addParameter(QgsProcessingParameterVectorDestination('OUTPUT', 'Profils discrétisés'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        
        # entrées
        lignes = self.parameterAsVectorLayer(parameters, 'lignes', context)
        rasters = parameters['rasters']
        
        # sorties
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        profils = []

        # paramètres
        echantillons_nb = parameters['echantillons_nb']
        
        # traitement
        if len(rasters) == 0:
            feedback.pushInfo("⚠ Il est nécessaire de fournir au moins un raster en entrée.\n")
            return {}
        for ligne_f in lignes.getFeatures():
            ligne_g = ligne_f.geometry()
            freq = ligne_g.length()/(echantillons_nb-1)
            echantillons_g = [QgsGeometry().fromPointXY(ligne_g.asMultiPolyline()[0][0])]
            for i in range(1, echantillons_nb-1):
                echantillons_g.append(ligne_g.interpolate(freq*i))
            echantillons_g.append(QgsGeometry().fromPointXY(ligne_g.asMultiPolyline()[0][-1]))
            feedback.pushInfo(str(echantillons_g))
            for raster in rasters:
                elevations = []
                for echantillon_g in echantillons_g:                
                    elevation = raster.dataProvider().sample(echantillon_g.asPoint(), 1)[0]
                    elevations.append(elevation)
                profils.append([echantillons_g, ligne_f.attributes(), raster.name(), elevations])
            
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # écriture des données en sortie
        fields = lignes.fields()
        fields.append(QgsField("ordre", QVariant.Int))
        fields.append(QgsField("raster", QVariant.String))
        fields.append(QgsField("elevation", QVariant.Double))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")
        for echantillons_g, attributes, raster_name, elevations in profils:
            ordre = 0
            for echantillon_g, elevation in zip(echantillons_g, elevations): 
                f = QgsFeature()
                f.setGeometry(echantillon_g)
                echantillon_att = attributes.copy()
                echantillon_att.append(ordre)
                echantillon_att.append(raster_name)
                echantillon_att.append(elevation)
                f.setAttributes(echantillon_att)
                feedback.pushInfo(str(f.attributes()))
                writer.addFeature(f)
                ordre += 1
            
        feedback.setCurrentStep(2)
        
        results['OUTPUT']=output
        return results
                

    def name(self):
        return '2. Discrétiser les profils de validation'

    def displayName(self):
        return '2. Discrétiser les profils de validation'

    def group(self):
        return 'Boîte à outils validation'

    def groupId(self):
        return 'Boîte à outils validation'

    def createInstance(self):
        return ProfilsDepuisLignes()
