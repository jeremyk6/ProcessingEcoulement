from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterRasterLayer, QgsProcessingParameterMultipleLayers, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class DetecterObstructions(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterRasterLayer('mnt', 'MNT'))
        self.addParameter(QgsProcessingParameterNumber('echantillons_nb', 'Nombre d\'Échantillons', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=99, defaultValue=20))
        self.addParameter(QgsProcessingParameterNumber('seuil', 'Seuil de différence', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=5, defaultValue=1))
        self.addParameter(QgsProcessingParameterVectorDestination('OUTPUT', 'Profils repérés'))

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
        seuil = parameters['seuil']

        # traitement
        low = None
        ids = []
        plist = []
        previous = None
        diff = 0
        # échantillonnage des points sur chaque profil
        for profil_f in profils.getFeatures():
            profil_g = profil_f.geometry()
            freq = profil_g.length()/(echantillons_nb-1)
            echantillons_g = [QgsGeometry().fromPointXY(profil_g.asPolyline()[0])]
            for i in range(1, echantillons_nb-1):
                echantillons_g.append(profil_g.interpolate(freq*i))
            echantillons_g.append(QgsGeometry().fromPointXY(profil_g.asPolyline()[-1]))
            elevations = []
            for echantillon_g in echantillons_g:                
                elevation = mnt.dataProvider().sample(echantillon_g.asPoint(), 1)[0]
                elevations.append(elevation)
            if low == None:
                low = min(elevations)
                plist.append(profil_f)
            else:
                #if not plist and abs(((min(previous)-min(elevations))-diff)/diff)>0.55:
                #    ids.append(profil_f.id())
                #elif [i for i in elevations if i <= low+seuil]:
                if [i for i in elevations if i <= low+seuil]:
                    low = min(elevations)
                    plist.append(profil_f.id())
                else:
                    ids.append(profil_f.id())
                    if len(plist) <= 5: 
                        ids += plist
                    if plist:
                        diff = min(elevations)-low
                    del plist[:]
            previous = elevations
            # ↑ TODO : si le dernier profil est souterrain, différence entre les deux min. pour estimer s'il est toujours souterrain

            
            
            
            
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # écriture des données en sortie
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("obstruct", QVariant.Int))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.LineString, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")
        id = 1
        for profil_f in profils.getFeatures():
            if profil_f.id() not in ids:
                profil_f.setAttributes([0,0])
                id += 1
            else:
                profil_f.setAttributes([id,1])
            writer.addFeature(profil_f)
            
        feedback.setCurrentStep(2)
        
        results['OUTPUT']=output
        return results
                

    def name(self):
        return 'Détecter les obstructions'

    def displayName(self):
        return 'Détecter les obstructions'

    def group(self):
        return 'Boîte à outils ponts'

    def groupId(self):
        return 'Boîte à outils ponts'

    def createInstance(self):
        return DetecterObstructions()
