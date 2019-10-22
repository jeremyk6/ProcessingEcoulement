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

from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterRasterLayer, QgsProcessingParameterMultipleLayers, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class InterpolerValeursProfils(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterRasterLayer('mnt', 'MNT'))
        self.addParameter(QgsProcessingParameterNumber('echantillons_nb', 'Nombre d\'échantillons', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=99, defaultValue=20))
        self.addParameter(QgsProcessingParameterVectorDestination('OUTPUT', 'Nuage de points'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        
        # entrées
        profils = self.parameterAsVectorLayer(parameters, 'profils', context)
        mnt = self.parameterAsRasterLayer(parameters, 'mnt', context)
        
        # sorties
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)

        # paramètres
        echantillons_nb = parameters['echantillons_nb'] # nombre d'échantillons
        profils_pt = [] # géométries des points
        profils_sp = [] # valeur des points
        # les deux listes sont à deux dimension : chaque ligne correspond à un profil

        # traitement
        
        # discrétisation des points sur chaque profil
        for profil_f in profils.getFeatures():
            profil_g = profil_f.geometry()
            freq = profil_g.length()/(echantillons_nb-1)
            echantillons_g = [QgsGeometry().fromPointXY(profil_g.asMultiPolyline()[0][0])]
            for i in range(1, echantillons_nb-1):
                echantillons_g.append(profil_g.interpolate(freq*i))
            echantillons_g.append(QgsGeometry().fromPointXY(profil_g.asMultiPolyline()[0][-1]))
            # note pour ci-dessus : l'interpolation des premiers et derniers points sur une ligne peut parfois planter, on les place à la main pour lever le risque
            profils_pt.append(echantillons_g)
            elevations = []
            for echantillon_g in echantillons_g:                
                elevation = mnt.dataProvider().sample(echantillon_g.asPoint(), 1)[0]
                elevations.append(elevation)
            profils_sp.append(elevations)

        # interpolation linéaire : calcul des valeurs des points entre le premier et le dernier profil de point à point
        steps = []
        nb_profils = len(profils_sp)
        for i in range(0, echantillons_nb):
            # on récupère la valeur du point sur le premier et le dernier profil
            v1 = profils_sp[0][i]
            v2 = profils_sp[-1][i]
            # on détermine le pas de l'interpolation
            steps.append((v2-v1)/nb_profils)
        for i in range(1,nb_profils-1):
            for j in range(0, echantillons_nb):
                profils_sp[i][j] = profils_sp[i-1][j] + steps[j]
            
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # écriture des données en sortie
        fields = QgsFields()
        fields.append(QgsField("elevation", QVariant.Double))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")
        for i in range(0,nb_profils):
            for j in range(0, echantillons_nb):
                f = QgsFeature()
                f.setGeometry(profils_pt[i][j])
                f.setAttributes([profils_sp[i][j]])
                writer.addFeature(f)
            
        feedback.setCurrentStep(2)
        
        results['OUTPUT']=output
        return results
                

    def name(self):
        return 'Interpoler les valeurs d\'une série de profils'

    def displayName(self):
        return 'Interpoler les valeurs d\'une série de profils'

    def group(self):
        return 'Détections sur MNT'

    def groupId(self):
        return 'Détections sur MNT'

    def createInstance(self):
        return InterpolerValeursProfils()
