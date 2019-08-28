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
        # entrées
        profils_l = self.parameterAsVectorLayer(parameters, 'profils', context)
        mnt = self.parameterAsRasterLayer(parameters, 'mnt', context)
        
        # sorties
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)

        # paramètres
        echantillons_nb = parameters['echantillons_nb'] # nombre d'échantillons
        seuil = parameters['seuil']

        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(profils_l.featureCount()*2, model_feedback)
        status = 0
        results = {}

        if profils_l.fields().indexOf('LINE')<0:
            feedback.reportError("Les profils en entrée doivent contenir un attribut numérique LINE qui identifie chaque cours d'eau de manière unique !", True)
            return{}

        # preparation de la sortie
        id = 1
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("obstruct", QVariant.Int))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.LineString, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")

        lines_ids = profils_l.uniqueValues(profils_l.fields().indexOf('LINE'))

        for line_id in lines_ids:

            # traitement
            low = None
            ids = []
            plist = []
            p2 = None
            count = 0
            # échantillonnage des points sur chaque profil
            for profil_f in profils_l.getFeatures("LINE = %s"%line_id):
                profil_g = profil_f.geometry()
                freq = profil_g.length()/(echantillons_nb-1)
                echantillons_g = [QgsGeometry().fromPointXY(profil_g.asMultiPolyline()[0][0])]
                for i in range(1, echantillons_nb-1):
                    echantillons_g.append(profil_g.interpolate(freq*i))
                echantillons_g.append(QgsGeometry().fromPointXY(profil_g.asMultiPolyline()[0][-1]))
                elevations = []
                for echantillon_g in echantillons_g:                
                    elevation = mnt.dataProvider().sample(echantillon_g.asPoint(), 1)[0]
                    elevations.append(elevation)
                if low == None:
                    low = min(elevations)
                    plist.append(profil_f)
                else:
                    if not plist and (max(elevations)-min(elevations))<1.5:
                        ids.append(profil_f.id())
                    elif min(elevations) <= low+seuil:
                        low = min(elevations)
                        plist.append(profil_f.id())
                    else:
                        ids.append(profil_f.id())
                        if len(plist) <= 5: 
                            ids += plist
                        del plist[:]
                    if count == 1:
                        p2 = profil_f.id()
                status += 1
                count += 1
                feedback.setCurrentStep(status)
                if feedback.isCanceled():
                    return {}

            if p2 in ids:
                del ids[:]

            # post processing à la R.A.C.H.E™ (https://www.la-rache.com/)
            # permet d'étendre la détection à x profils amont/aval pour permettre l'interpolation
            prev = []
            count = 0
            ext = 2
            for profil_f in profils_l.getFeatures("LINE = %s"%line_id):
                if len(prev) > 1:
                    if count == 0:
                        if profil_f.id() in ids and prev[-1] not in ids:
                            ids += prev
                        if profil_f.id() not in ids and prev[-1] in ids:
                            ids.append(profil_f.id())
                            count += 1
                    else:
                        if count < ext:
                            ids.append(profil_f.id())
                            count += 1
                        else:
                            count = 0
                prev.append(profil_f.id())
                if len(prev) > ext:
                    del prev[0]

            
            # attribution d'un identifiant unique à chaque groupe de profils souterrains
            # ecriture de chaque profil dans la nouvelle couche
            for profil_f in profils_l.getFeatures("LINE = %s"%line_id):
                if profil_f.id() not in ids:
                    profil_f.setAttributes([0,0])
                    id += 1
                else:
                    profil_f.setAttributes([id,1])
                writer.addFeature(profil_f)
                status += 1
                feedback.setCurrentStep(status)
                if feedback.isCanceled():
                    return {}
        
        results['OUTPUT']=output
        return results
                

    def name(self):
        return 'Détecter les obstructions sur une série de profils'

    def displayName(self):
        return 'Détecter les obstructions sur une série de profils'

    def group(self):
        return 'Détections sur MNT'

    def groupId(self):
        return 'Détections sur MNT'

    def createInstance(self):
        return DetecterObstructions()
