#
import ee
import sys
import os
import pandas as pd
from pprint import pprint

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath('../../'))

from modules.Collection import getCollection
from modules.BandNames import getBandNames
from modules.CloudAndShadowMaskC2 import getMasks
from modules.SMA_NDFI import *

ee.Initialize()

ASSET_MAPBIOMAS = 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1'

ASSET_BIOMES = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019'

ASSET_SAMPLES = 'projects/imazon-simex/LULC/SAMPLES/COLLECTION6/REVISED_AND_URBAN'

ASSET_OUTPUT = 'projects/imazon-simex/LULC/SAMPLES/COLLECTION7/TRAINED_BY_SCENE'

ASSET_TILES = 'projects/mapbiomas-workspace/AUXILIAR/landsat-mask'

# year and training year
YEARS = [
    # [2021, 2020],
    [2022, 2020],
]

TILES = [
    # 221061, 221062, 221063, 221064
]

# versao 2 - amostras lapig + amostras urbano
SAMPLES_VERSION = '2'

#
SAMPLES_OUTPUT_VERSION = '1'

# landsat short names
SATELLITE_IDS = [
    'l5', 
    'l7', 
    'l8', 
    'l9'
    ]

# endemembers used to unmix data
ENDMEMBERS = {
    'l5': ENDMEMBERS_L5,
    'l7': ENDMEMBERS_L7,
    'l8': ENDMEMBERS_L8,
    'l9': ENDMEMBERS_L8,
}

# landsat collection ids
COLLECTION_IDS = {
    'l5': 'LANDSAT/LT05/C02/T1_L2',
    'l7': 'LANDSAT/LE07/C02/T1_L2',
    'l8': 'LANDSAT/LC08/C02/T1_L2',
    'l9': 'LANDSAT/LC09/C02/T1_L2',
}

SAMPLES_CLASS_IDS = [
    [3, 3],
    [4, 4],
    [14, 4],
    [12, 12],
    [13, 12],
    [15, 15],
    [18, 18],
    [20, 18],
    [24, 25],
    [25, 25],
    [33, 33]
]

MAPBIOMAS_CLASS_IDS = [
    [3, 3],
    [5, 3],
    [4, 4],
    [12, 12],
    [15, 15],
    [18, 18],
    [19, 18],
    [39, 18],
    [20, 18],
    [40, 18],
    [41, 18],
    [36, 18],
    [46, 18],
    [47, 18],
    [48, 18],
    [23, 25],
    [24, 25],
    [25, 25],
    [30, 25],
    [33, 33],
    [31, 33]
]

SEGMENT_BANDS = [
    "blue",
    "green",
    "red",
    "nir",
    "swir1",
    "swir2"
]

def applyCloudAndShadowMask(collection):

    # Get cloud and shadow masks
    collectionWithMasks = getMasks(collection,
                                   cloudFlag=True,
                                   cloudScore=True,
                                   cloudShadowFlag=True,
                                   cloudShadowTdom=True,
                                   zScoreThresh=-1,
                                   shadowSumThresh=4000,
                                   dilatePixels=2,
                                   cloudHeights=ee.List.sequence(
                                       200, 10000, 500),
                                   cloudBand='cloudFlagMask')

    # collectionWithMasks = collectionWithMasks.select(specCloudBands)

    # get collection without clouds
    collectionWithoutClouds = collectionWithMasks.map(
        lambda image: image.mask(
            image.select([
                'cloudFlagMask',
                'cloudScoreMask',
                'cloudShadowFlagMask',
                'cloudShadowTdomMask'
            ]).reduce(ee.Reducer.anyNonZero()).eq(0)
        )
    )

    return collectionWithoutClouds


def getSegments(image, size=16):

    seeds = ee.Algorithms.Image.Segmentation.seedGrid(
        size=size,
        gridType='square'
    )

    snic = ee.Algorithms.Image.Segmentation.SNIC(
        image=image,
        size=size,
        compactness=1,
        connectivity=8,
        neighborhoodSize=2*size,
        seeds=seeds
    )

    snic = ee.Image(snic)
    # snic = ee.Image(
    #     snic.copyProperties(image)
    #         .copyProperties(image, ['system:footprint'])
    #         .copyProperties(image, ['system:time_start']))

    return snic.select(['clusters'], ['segments'])


def getSimilarMask(segments, samples):

    samplesSegments = segments.sampleRegions(
        collection=samples,
        properties=['class']
    )

    segmentsValues = ee.List(
        samplesSegments
        .reduceColumns(
            ee.Reducer.toList().repeat(2),
            ['class', 'segments']
        ).get('list')
    )

    similiarMask = segments.remap(
        segmentsValues.get(1),
        segmentsValues.get(0), 0)

    return similiarMask.rename(['class'])


#
#
#
dfAreas = pd.read_csv('../collection-7/data/areas.csv')
print(dfAreas)

if len(TILES) == 0:
    TILES = list(pd.unique(dfAreas['tile']))
#
#
#
amazon = ee.FeatureCollection(ASSET_BIOMES)\
    .filter(ee.Filter.eq('Bioma', 'Amazônia'))
#
#
samplesClassIdsIn = list(
    map(lambda classid: classid[0], SAMPLES_CLASS_IDS))
samplesClassIdsOut = list(
    map(lambda classid: classid[1], SAMPLES_CLASS_IDS))
#
#
mapbiomasClassIdsIn = list(
    map(lambda classid: classid[0], MAPBIOMAS_CLASS_IDS))
mapbiomasClassIdsOut = list(
    map(lambda classid: classid[1], MAPBIOMAS_CLASS_IDS))

#
#
mapbiomas = ee.Image(ASSET_MAPBIOMAS)

mapbiomas = mapbiomas.bandNames()\
    .iterate(
        lambda band, image:
            ee.Image(image).addBands(
                ee.Image(mapbiomas
                         .select([band])
                         .remap(mapbiomasClassIdsIn, mapbiomasClassIdsOut)
                         .rename([band]))
            ),
        ee.Image().select()
)

mapbiomas = ee.Image(mapbiomas)

# loads ladsat tiles collection
tilesCollection = ee.ImageCollection(ASSET_TILES)\
    .filter(ee.Filter.bounds(amazon))\
    .filter(ee.Filter.eq('version', '2'))

for year, trainingYear in YEARS:

    assetSamples = '{}/samples-amazon-collection-6-{}-{}'.format(
        ASSET_SAMPLES, trainingYear, SAMPLES_VERSION)

    samples = ee.FeatureCollection(assetSamples)
    
    bandMapbiomas = 'classification_{}'.format(trainingYear)

    for tile in TILES:
        tileMask = tilesCollection.filterMetadata('tile', 'equals', int(tile))
        tileMask = ee.Image(tileMask.first())
        
        tileGeometry = tileMask.geometry()
        centroid = tileGeometry.centroid()

        for satelliteId in SATELLITE_IDS:
            try:
                # returns a collection containing the specified parameters
                collection = getCollection(COLLECTION_IDS[satelliteId],
                                            dateStart=str(year)+'-01-01',
                                            dateEnd=str(year)+'-12-31',
                                            cloudCover=50,
                                            geometry=centroid)

                print('Number of images:', collection.size().getInfo())

                # returns the pattern of band names
                bands = getBandNames(satelliteId + 'c2')

                # selects the images bands and rename it
                collection = collection.select(
                    bands['bandNames'],
                    bands['newNames']
                )

                # remove clouds and shadows
                collectionWithoutClouds = applyCloudAndShadowMask(collection)

                # build the feature space bands
                featureSpaceCollection = collectionWithoutClouds\
                    .map(lambda image:
                            image.addBands(srcImg=getSMAFractions(image, ENDMEMBERS[satelliteId]), overwrite=True))\
                    .map(lambda image:
                            image.addBands(srcImg=getNDFI(image), overwrite=True))\
                    .map(lambda image:
                            image.addBands(srcImg=getCSFI(image), overwrite=True))

                # lists the image ids
                imageIds = collection.reduceColumns(
                    ee.Reducer.toList(), ['system:index'])

                imageIds = imageIds.get('list').getInfo()

                for imageId in imageIds:
                    #
                    newSamplesName = '{}_{}'.format(imageId, SAMPLES_OUTPUT_VERSION)

                    assetId = '{}/{}/{}'.format(ASSET_OUTPUT,
                                                year, newSamplesName)

                    try:
                        assetInfo = ee.data.getAsset(assetId)
                    except Exception as e:
                        print('Processing image:', imageId)

                        # step 1: get the image
                        image = featureSpaceCollection.filterMetadata(
                            'system:index', 'equals', imageId)

                        image = ee.Image(image.first())

                        geometry = image.geometry()

                        # step 2: filter samples
                        samplesSubset = samples.filterBounds(geometry)\
                            .remap(
                                samplesClassIdsIn,
                                samplesClassIdsOut,
                                'class'
                        )

                        # print('Number of samples:', samplesSubset.size().getInfo())

                        # step 3: generate segments
                        segments = getSegments(image.select(SEGMENT_BANDS), 16)

                        # step 4: get similarity mask
                        similarMask = getSimilarMask(
                            segments, samplesSubset)

                        # step 5: validate similarity mask
                        percentil = segments.addBands(mapbiomas, [bandMapbiomas])\
                            .reduceConnectedComponents(ee.Reducer.percentile([5, 95]), 'segments')

                        validated = segments.addBands(mapbiomas, [bandMapbiomas])\
                            .reduceConnectedComponents(ee.Reducer.mode(), 'segments')

                        validated = validated.multiply(
                            percentil.select(0).eq(percentil.select(1)).eq(1))

                        similarMaskValidated = similarMask.mask(
                            similarMask.eq(validated)).selfMask().rename('class')

                        # step 6: generate new samples dataset
                        newSamples = image\
                            .addBands(similarMaskValidated)\
                            .sample(
                                region=geometry,
                                scale=30,
                                factor=0.05,
                                dropNulls=True,
                                geometries=True,
                                tileScale=16

                            )
                            
                        task = ee.batch.Export.table.toAsset(
                            collection=newSamples,
                            description=newSamplesName,
                            assetId=assetId,
                        )

                        print('Exporting {}...'.format(newSamplesName))

                        task.start()
            except Exception as e:
                print(e)
