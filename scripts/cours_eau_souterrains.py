from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber, QgsProcessingParameterRasterDestination
import processing


class IntgrerUnCoursDeauSouterrain(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('MNT', 'MNT', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('profils', 'Profils', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('rsolution', 'Résolution', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=5))
        self.addParameter(QgsProcessingParameterRasterDestination('OUTPUT', 'MNT intégré', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # WELCOME TO THE FANTASY ZONE

        # Extraire par attribut
        alg_params = {
            'FIELD': 'id',
            'INPUT': parameters['profils'],
            'OPERATOR': 1,
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraireParAttribut'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Séparer une couche vecteur
        alg_params = {
            'FIELD': 'id',
            'INPUT': outputs['ExtraireParAttribut']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SparerUneCoucheVecteur'] = processing.run('qgis:splitvectorlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        layers = outputs['SparerUneCoucheVecteur']['OUTPUT_LAYERS']
        to_merge = []
        for layer in layers:
            # Interpoler les valeurs d'une série de profils
            alg_params = {
                'echantillons_nb': 20,
                'mnt': parameters['MNT'],
                'profils': layer,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['InterpolerLesValeursDuneSrieDeProfils'] = processing.run('script:Interpoler les valeurs d\'une série de profils', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            # Interpolation TIN
            alg_params = {
                'EXTENT': parameters['MNT'],
                'INTERPOLATION_DATA': outputs['InterpolerLesValeursDuneSrieDeProfils']['OUTPUT']+'::~::0::~::0::~::0', # format d'INTERPOLATION_DATA, non-documenté
                'METHOD': 0,
                'PIXEL_SIZE': parameters['rsolution'],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['InterpolationTin'] = processing.run('qgis:tininterpolation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            to_merge.append(outputs['InterpolationTin']['OUTPUT'])

        # Fusionner
        alg_params = {
            'DATA_TYPE': 5,
            'EXTRA': '',
            'INPUT': to_merge,
            'NODATA_INPUT': None,
            'NODATA_OUTPUT': None,
            'OPTIONS': '',
            'PCT': False,
            'SEPARATE': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Fusionner'] = processing.run('gdal:merge', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # r.null
        alg_params = {
            '-c': False,
            '-f': False,
            '-i': False,
            '-n': False,
            '-r': False,
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'map': outputs['Fusionner']['OUTPUT'],
            'null': None,
            'setnull': '0',
            'output': 'D:\out.tif'
        }
        outputs['Rnull'] = processing.run('grass7:r.null', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        print(outputs['Rnull'])

        '''
        # Recaler un raster
        alg_params = {
            'Rasterrecaler': outputs['InterpolationTin']['OUTPUT'],
            'Rastersource': parameters['MNT'],
            'rsolutionpixellaire': parameters['rsolution'],
            'gdal:warpreproject_1:Raster recalé': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecalerUnRaster'] = processing.run('model:Recaler un raster', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        '''

        # Intégrer un MNT
        alg_params = {
            'MNTintgrer': outputs['Rnull']['output'],
            'MNToriginal': parameters['MNT'],
            'seuildediffrence': 1,
            'gdal:rastercalculator_1:MNT intégré': parameters['OUTPUT']
        }
        outputs['IntgrerUnMnt'] = processing.run('model:Intégrer un MNT', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        results['OUTPUT'] = outputs['IntgrerUnMnt']['gdal:rastercalculator_1:MNT intégré']

        return results

    def name(self):
        return 'Intégrer un cours d\'eau souterrain'

    def displayName(self):
        return 'Intégrer un cours d\'eau souterrain'

    def group(self):
        return 'Stage IGN'

    def groupId(self):
        return 'Stage IGN'

    def createInstance(self):
        return IntgrerUnCoursDeauSouterrain()
