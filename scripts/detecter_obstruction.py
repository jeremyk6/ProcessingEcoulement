from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterVectorLayer, QgsProcessingParameterRasterLayer, QgsProcessingParameterMultipleLayers, QgsProcessingParameterNumber, QgsProcessingParameterVectorDestination
from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFields, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

class DetecterObstructions(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils', types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterRasterLayer('mnt', 'MNT'))
        self.addParameter(QgsProcessingParameterNumber('echantillons_nb', 'Nombre d\'échantillons', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=99, defaultValue=20))
        self.addParameter(QgsProcessingParameterNumber('seuil_diff', 'Seuil de différence', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=5, defaultValue=1))
        self.addParameter(QgsProcessingParameterNumber('seuil_rug', 'Seuil de rugosité', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=5, defaultValue=1.5))
        self.addParameter(QgsProcessingParameterVectorDestination('OUTPUT', 'Profils repérés'))

    def processAlgorithm(self, parameters, context, model_feedback):      
        # entrées
        profils_l = self.parameterAsVectorLayer(parameters, 'profils', context)
        mnt = self.parameterAsRasterLayer(parameters, 'mnt', context)
        
        # sorties
        output = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)

        # paramètres
        echantillons_nb = parameters['echantillons_nb'] # nombre d'échantillons
        seuil_diff = parameters['seuil_diff']
        seuil_rug = parameters['seuil_rug']

        # variables propres à Processing
        feedback = QgsProcessingMultiStepFeedback(profils_l.featureCount()*2, model_feedback)
        status = 0
        results = {}

        # l'algo SAGA Cross Profiles ajoute à chaque profil un attribut LINE qui permet d'identifier pour chaque profil la ligne dont il est issu
        # permet de traiter les profils de cours d'eau à cours d'eau
        if profils_l.fields().indexOf('LINE')<0:
            feedback.reportError("Les profils en entrée doivent contenir un attribut numérique LINE qui identifie chaque cours d'eau de manière unique !", True)
            return{}

        # préparation de la sortie
        id = 1
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("obstruct", QVariant.Int))
        writer = QgsVectorFileWriter(output, "System", fields, QgsWkbTypes.LineString, QgsCoordinateReferenceSystem(2154), "ESRI Shapefile")

        # on récupère les identifiants uniques de lignes pour traiter les profils par cours d'eau
        lines_ids = profils_l.uniqueValues(profils_l.fields().indexOf('LINE'))
        
        for line_id in lines_ids:

            # variables liées aux traitements
            low = None # dernière valeur d'altitude non-obstruée
            ids = []   # liste des identifiants de profils obstrués
            plist = [] # liste des X derniers profils 
            p2 = None  # id du deuxième profil traité
            count = 0

            # pour chaque cours d'eau
            for profil_f in profils_l.getFeatures("LINE = %s"%line_id):

                # ajout des points sur chaque profil
                profil_g = profil_f.geometry()
                freq = profil_g.length()/(echantillons_nb-1)
                echantillons_g = [QgsGeometry().fromPointXY(profil_g.asMultiPolyline()[0][0])]
                for i in range(1, echantillons_nb-1):
                    echantillons_g.append(profil_g.interpolate(freq*i))
                echantillons_g.append(QgsGeometry().fromPointXY(profil_g.asMultiPolyline()[0][-1]))

                # on affecte aux points la valeur du MNT correspondante
                elevations = []
                for echantillon_g in echantillons_g:                
                    elevation = mnt.dataProvider().sample(echantillon_g.asPoint(), 1)[0]
                    elevations.append(elevation)

                # exécuté pour le tout premier profil qui va déterminer la première valeur d'altitude considérée
                if low == None:
                    low = min(elevations)
                    plist.append(profil_f)
                # détection des obstructions
                else:
                    # seuil utilisé pour détecter les ruptures franches et limiter les "petites détections"
                    if min(elevations) <= low+seuil_diff:
                        # en cas de longue portion souterraine, la condition d'écoulement peut être remplie alors que le CE est toujours souterrain (cas sur le Malvan à Cagnes)
                        # on vérifie alors si le terrain est relativement plat (rugosité faible) et, si c'est le cas, on maintient l'obstruction
                        # pose problème sur les CE peu profonds
                        if not plist and (max(elevations)-min(elevations))<seuil_rug:
                            ids.append(profil_f.id())
                        # il y a écoulement
                        else:
                            low = min(elevations)
                            plist.append(profil_f.id())
                    else: # il n'y a pas écoulement
                        ids.append(profil_f.id()) 
                        # s'il y a un groupe de 5 (ou moins) profils non-obstrués au milieu de profils obstrués, on les ajoute au traitement
                        if len(plist) <= 5:
                            ids += plist
                        del plist[:]
                    # récupération de l'id du deuxième profil
                    if count == 1:
                        p2 = profil_f.id()

                status += 1
                count += 1
                feedback.setCurrentStep(status)
                if feedback.isCanceled():
                    return {}

            # si le second profil est obstrué, on considère qu'il y a erreur et on ne traite pas le CE
            # lorsque le cas arrive, il s'agit souvent d'un CE non-présent sur le MNT et le traitement est erronné
            if p2 in ids:
                del ids[:]

            # post processing pour étendre la détection à x profils amont/aval pour permettre l'interpolation
            # extention modulable par la variable ext ci-dessous
            ext = 2
            prev = []
            count = 0
            for profil_f in profils_l.getFeatures("LINE = %s"%line_id):
                if len(prev) > 0:
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
            # ecriture de chaque profil dans la nouvelle couche qui contient deux attributs :
            # id : identifie les profils obstrués contigus pour les traiter en groupe
            # obstruct : à 1 si le profil est obstrué, sinon à 0
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
