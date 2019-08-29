from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterVectorDestination, QgsProcessingMultiStepFeedback, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber, QgsProcessingParameterRasterDestination
import processing


class IntgrerUnCoursDeauSouterrain(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('MNT', 'MNT', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils repérés', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('rsolution', 'Résolution', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=5))
        self.addParameter(QgsProcessingParameterRasterDestination('OUTPUT', 'MNT intégré', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Extraire par attribut
        # On récupère les profils dont l'id ≠ 0 (uniquement les profils obstrués)
        alg_params = {
            'FIELD': 'id',
            'INPUT': parameters['profils'],
            'OPERATOR': 1,
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraireParAttribut'] = processing.run('native:extractbyattribute', alg_params, context=context, is_child_algorithm=True)

        # Séparer une couche vecteur
        # On divise la couche en X couches, une par id d'obstruction
        alg_params = {
            'FIELD': 'id',
            'INPUT': outputs['ExtraireParAttribut']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SparerUneCoucheVecteur'] = processing.run('qgis:splitvectorlayer', alg_params, context=context, is_child_algorithm=True)
        layers = outputs['SparerUneCoucheVecteur']['OUTPUT_LAYERS']

        feedback = QgsProcessingMultiStepFeedback(len(layers)+4, model_feedback)
        status = 0

        to_merge = []
        for layer in layers: # pour chaque groupe de profils obstrués
        
            # Interpoler les valeurs d'une série de profils
            # On interpole linéairement les profils entre le premier et le dernier profil
            alg_params = {
                'echantillons_nb': 20,
                'mnt': parameters['MNT'],
                'profils': layer,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['InterpolerLesValeursDuneSrieDeProfils'] = processing.run('script:Interpoler les valeurs d\'une série de profils', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            # Interpolation TIN
            # On passe du nuage de points obtenu au traitement précédent à un raster par interpolation TIN
            alg_params = {
                'EXTENT': parameters['MNT'],
                'INTERPOLATION_DATA': outputs['InterpolerLesValeursDuneSrieDeProfils']['OUTPUT']+'::~::0::~::0::~::0', # format d'INTERPOLATION_DATA, non-documenté
                'METHOD': 0,
                'PIXEL_SIZE': parameters['rsolution'],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['InterpolationTin'] = processing.run('qgis:tininterpolation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            # Recaler un raster
            # Le raster précédent n'est pas calé sur les pixels du MNT original, on le recale
            alg_params = {
                'Rasterrecaler': outputs['InterpolationTin']['OUTPUT'],
                'Rastersource': parameters['MNT'],
                'rsolutionpixellaire': parameters['rsolution'],
                'gdal:warpreproject_1:Recalé': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['RecalerUnRaster'] = processing.run('model:Caler un raster sur une référence', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            
            # On ajoute le morceau de MNT obtenu à une liste de MNT à intégrer à la fin
            to_merge.append(outputs['RecalerUnRaster']['gdal:warpreproject_1:Recalé'])

            status += 1
            feedback.setCurrentStep(status)
            if feedback.isCanceled():
                return {}

        status += 1
        feedback.setCurrentStep(status)
        if feedback.isCanceled():
            return {}

        # Intégrer un MNT
        # On intègre de manière incrémentale les MNT intermédiaires calculés précédemment
        mnt = parameters['MNT']
        for layer in to_merge:
            outval = QgsProcessing.TEMPORARY_OUTPUT
            if layer == to_merge[-1]: # Quand on arrive au dernier MNT à ajouter, la sortie obtenue est la sortie finale
                outval = parameters['OUTPUT']
            alg_params = {
                'MNTintgrer': layer,
                'MNToriginal': mnt,
                'seuildediffrence': 1,
                'gdal:rastercalculator_1:Fusionné': outval
            }
            outputs['IntgrerUnMnt'] = processing.run('model:Fusionner deux MNT', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            mnt = outputs['IntgrerUnMnt']['gdal:rastercalculator_1:Fusionné']

        status += 1
        feedback.setCurrentStep(status)
        if feedback.isCanceled():
            return {}
        
        results['OUTPUT'] = mnt#outputs['IntgrerUnMnt']['gdal:rastercalculator_1:MNT intégré']

        return results

    def name(self):
        return 'Intégrer un cours d\'eau souterrain'

    def displayName(self):
        return 'Intégrer un cours d\'eau souterrain'

    def group(self):
        return 'Traitements de MNT'

    def groupId(self):
        return 'Traitements de MNT'

    def createInstance(self):
        return IntgrerUnCoursDeauSouterrain()
