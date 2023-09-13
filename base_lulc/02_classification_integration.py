#
import ee
import pandas as pd
import sys

sys.setrecursionlimit(10000)

ASSETS = {
    'feature_space': 'projects/imazon-simex/LULC/COLLECTION7/feature-space',
    # 'n_observations': 'projects/imazon-simex/LULC/quality',
    'n_observations': 'projects/mapbiomas-workspace/COLECAO7/qualidade',
    'tiles': 'projects/mapbiomas-workspace/AUXILIAR/landsat-mask',
    'samples_folder': 'projects/imazon-simex/LULC/SAMPLES/COLLECTION6/INTEGRATE',
    'output': 'projects/imazon-simex/LULC/COLLECTION7/integrated'
}

INPUT_VERSION = '4'

# 1 - primeira versão 2021
# 2 - 2021 com balanceamento de amostras pela area (beta)
# 3 - 2021 com balanceamento de amostras pela area
# 4 - 2021 com balanceamento de amostras pela area (> pastagem e savana)
# 5 - 2021 com balanceamento de amostras pela area (> pastagem e agua)
# 6 - cenas revisadas
# 7 - cenas revisadas, metadados ajustados
# 8 - cenas selecionadas entre as versoes 1, 5 e 7

OUTPUT_VERSION = '8'

CLASS_IDS = [
    3,  # forest
    4,  # savanna
    12,  # grassland
    15,  # pasture
    18,  # agriculture
    33  # water
]

# number of samples
N_SAMPLES = 5000

# # minimum number of samples per classe
dfMinSamples = pd.DataFrame([
    {'class':  3, 'min_samples': N_SAMPLES * 0.20},
    {'class':  4, 'min_samples': N_SAMPLES * 0.05},
    {'class': 12, 'min_samples': N_SAMPLES * 0.10},
    {'class': 15, 'min_samples': N_SAMPLES * 0.20},
    {'class': 18, 'min_samples': N_SAMPLES * 0.10},
    {'class': 33, 'min_samples': N_SAMPLES * 0.15},
])

# # versao 4
# dfMinSamples = pd.DataFrame([
#     {'class':  3, 'min_samples': N_SAMPLES * 0.20},
#     {'class':  4, 'min_samples': N_SAMPLES * 0.10},
#     {'class': 12, 'min_samples': N_SAMPLES * 0.10},
#     {'class': 15, 'min_samples': N_SAMPLES * 0.30},
#     {'class': 19, 'min_samples': N_SAMPLES * 0.20},
#     {'class': 33, 'min_samples': N_SAMPLES * 0.20},
# ])

# # versao 5
# dfMinSamples = pd.DataFrame([
#     {'class':  3, 'min_samples': N_SAMPLES * 0.20},
#     {'class':  4, 'min_samples': N_SAMPLES * 0.10},
#     {'class': 12, 'min_samples': N_SAMPLES * 0.10},
#     {'class': 15, 'min_samples': N_SAMPLES * 0.40},
#     {'class': 18, 'min_samples': N_SAMPLES * 0.20},
#     {'class': 33, 'min_samples': N_SAMPLES * 0.30},
# ])

# versao 7
# dfMinSamples = pd.DataFrame([
#     {'class':  3, 'min_samples': N_SAMPLES * 1.0},
#     {'class':  4, 'min_samples': N_SAMPLES * 0.0},
#     {'class': 12, 'min_samples': N_SAMPLES * 0.10},
#     {'class': 15, 'min_samples': N_SAMPLES * 1.0},
#     {'class': 18, 'min_samples': N_SAMPLES * 0.10},
#     {'class': 33, 'min_samples': N_SAMPLES * 0.30},
# ])

YEARS = [
    # 1985, 1986, 1987, 1988,
    # 1989, 1990, 1991, 1992,
    # 1993, 1994, 1995, 1996,
    # 1997, 1998, 1999, 2000,
    # 2001, 2002, 2003, 2004,
    # 2005, 2006, 2007, 2008,
    # 2009, 2010, 2011, 2012,
    # 2013, 2014, 2015, 2016,
    # 2017, 2018, 2019, 2020,
    # 2021,
    2022
]

SAMPLES_LIST = [
    # "samples-amazon-collection-6-2020-2", "samples-amazon-collection-6-2019-2",
    "samples-amazon-collection-6-2018-2", "samples-amazon-collection-6-2017-2",
    "samples-amazon-collection-6-2016-2", "samples-amazon-collection-6-2015-2",
    "samples-amazon-collection-6-2014-2", "samples-amazon-collection-6-2013-2",
    "samples-amazon-collection-6-2012-2", "samples-amazon-collection-6-2011-2",
    "samples-amazon-collection-6-2010-2", "samples-amazon-collection-6-2009-2",
    "samples-amazon-collection-6-2008-2", "samples-amazon-collection-6-2007-2",
    "samples-amazon-collection-6-2006-2", "samples-amazon-collection-6-2005-2",
    # "samples-amazon-collection-6-2004-2", "samples-amazon-collection-6-2003-2",
    # "samples-amazon-collection-6-2002-2", "samples-amazon-collection-6-2001-2",
    # "samples-amazon-collection-6-2000-2", "samples-amazon-collection-6-1999-2",
    # "samples-amazon-collection-6-1998-2", "samples-amazon-collection-6-1997-2",
    # "samples-amazon-collection-6-1996-2", "samples-amazon-collection-6-1995-2",
    # "samples-amazon-collection-6-1994-2", "samples-amazon-collection-6-1993-2",
    # "samples-amazon-collection-6-1992-2", "samples-amazon-collection-6-1991-2",
    # "samples-amazon-collection-6-1990-2", "samples-amazon-collection-6-1989-2",
    # "samples-amazon-collection-6-1988-2", "samples-amazon-collection-6-1987-2",
    # "samples-amazon-collection-6-1986-2",  # "samples-amazon-collection-6-1985-2",
]

# tiles reprocessados para a colecao 7.0
TILE_LIST = [
    # "226060", "226066", "227068", "227062",
    # "001060", "224066", "224062", "224065",
    # "220063", "220062", "221062", "222065",
    # "222066", "223066", "223067", "223069",
    # "223060", "224060", "224068", "224069",
    # "224061", "225058", "225059", "225060",
    # "226057", "226061", "226070", "227070",
    # "227071", "227072", "227061", "228061",
    # "222062", "222063", "222067", "223061",
    # "223062", "223063", "223068", "224063",
    # "224064", "224070", "225061", "225062",
    # "225063", "225064", "225070", "226059",
    # "226062", "226063", "226064", "226065",
    # "226068", "227058", "227059", "227060",
    # "227063", "227064", "227065", "227067",
    # "228058", "228060", "228063", "228064",
    # "228067", "228068", "228072", "229060",
    # "229061", "229063", "229064", "229066",
    # "225065", "226067", "226069", "228062",
    # "228065", "228066", "228069", "229065",
    # "223064", "223065", "224067", "225066",
    # "225067", "225068", "225069", "226058",
    # "227066", "227069", "228059", "229069",
    # "228070", "228071", "229070", "229071",
    # "229058", "229059", "229062", "230069",
    # "001057", "001058", "001059", "001061",
    # "001062", "001063", "001064", "001065",
    # "001066", "001067", "001068", "002057",
    # "002059", "002060", "002061", "002062",
    # "002063", "002064", "002065", "002066",
    # "002067", "002068", "221064", "222061",
    # "229067", "229068", "230058", "230059",
    # "230060", "230061", "230063", "230064",
    # "230065", "230066", "230067", "230070",
    # "003060", "003061", "003062", "003063",
    # "003064", "003065", "003066", "003067",
    # "003068", "004058", "004059", "004060",
    # "004061", "004062", "004063", "004064",
    # "004065", "004066", "004067", "005059",
    # "005060", "005063", "005064", "005065",
    # "005066", "005067", "006063", "006064",
    # "006065", "006066",
    "232061", "232056", "233057", "233061",
    "231062", "231064", "232066", "233059",
    "233066", "221061", "221063", "222064",
    "230062", "230068", "231059", "231068",
    "232063", "232065", "232068", "232069",
    "231057", "231058", "231066", "231069",
    "232058", "232057", "232059", "232060",
    "233060", "233068",
    "231060", "231061", "231063", "231065",
    "231067", "232062", "232064", "232067",
    "233058", "233062", "233063", "233064",
    "233065", "233067", "003058", "003059",
]

# TILE_LIST = [
#     "228063",
#     "227063",
#     "227062",
#     "227061",
#     "228061",
#     "226062",
#     "226063",
#     "225062",
#     "224063",
#     "225063",
#     "224065",
#     "224066",
# ]

# TILE_LIST = [
    # "231069", "230069",
    # "228066", "228065",
    # "224062", "232061",
    # "231059", "224060",
    # "224061", "225060",
    # "225059", "229065",
    # "224067", "224066",
    # "224065", "224064",
    # "231068", "232068",
    # "226058", "227061",
    # "001057", "233068"
# ]

FEATURE_SPACE = [
    'mode',
    'mode_secondary',
    'transitions_year',
    'distinct_year',
    'observations_year',
    'occurrence_forest_year',
    'occurrence_savanna_year',
    'occurrence_grassland_year',
    'occurrence_pasture_year',
    'occurrence_agriculture_year',
    'occurrence_water_year',
    #'transitions_total',
    #'distinct_total',
    # 'observations_total',
    #'occurrence_forest_total',
    #'occurrence_savanna_total',
    #'occurrence_grassland_total',
    #'occurrence_pasture_total',
    #'occurrence_agriculture_total',
    #'occurrence_water_total',
]

ee.Initialize()


def shuffle(collection, seed=1):
    """
    """

    shuffled = collection.randomColumn('random', seed)\
        .sort('random', True)

    return shuffled


# read areas table
dfAreas = pd.read_csv('../collection-7/data/areas.csv')

print(dfAreas)

# 1. Legend adjustment for Amazon classes
INDEX = ['year', 'tile']

dfAreas = dfAreas.replace(
    {'class': {20: 18, 36: 18, 39: 18, 41: 18, 24: 25, 9: 3}})

# aggregate areas by class, tile and year
dfAgg = dfAreas.groupby(['year', 'tile', 'class']).agg(
    {'area': 'sum'}).reset_index()

# calculate the total area per tile and year
dfTotal = dfAreas.groupby(INDEX).agg({'area': 'sum'}).reset_index()

# merges the dfAgg with dfTotal
df = pd.merge(dfAgg, dfTotal, how="outer", on=INDEX, suffixes=(None, '_total'))

# 2. Calculate the proportion of each class
df['proportion'] = df['area'].div(df['area_total'])

df[(df['tile'] == 226069) & (df['year'] == 2021)]

# 3. Number of samples based on proportions of area
# calculates the number of samples based on proportions
df['n_samples'] = df['proportion'].mul(N_SAMPLES).round()

# merges minimum samples per class to data table
df = pd.merge(df, dfMinSamples, how="outer", on="class")

# replace n_samples column with the highest value betwen min_samples and n_samples
df.loc[df['min_samples'] > df['n_samples'], 'n_samples'] = df['min_samples']

print(df)

n_observations = ee.ImageCollection(ASSETS['n_observations'])

# samples
lookupIn = [12, 15, 18, 19, 24, 25, 29, 3, 33, 4, 6, 9]
# lookupOut = [12, 15, 18, 18, 25, 25, 12, 3, 33, 4, 3, 3]
lookupOut = [12, 15, 18, 18, 15, 15, 12, 3, 33, 4, 3, 3]

samples = map(
    lambda sampleName:
        ee.FeatureCollection(ASSETS['samples_folder'] + "/" + sampleName)
        .remap(lookupIn, lookupOut, 'class'),
    SAMPLES_LIST
)

samples = ee.FeatureCollection(list(samples)).flatten()

print(samples.size().getInfo())

#
#
outputCollection = ee.ImageCollection(ASSETS['output'])
names = outputCollection.aggregate_array('system:index').getInfo()
#
#
for tile in TILE_LIST:

    try:

        tile_mask = ee.Image('{}/{}-2'.format(ASSETS['tiles'], int(tile)))
        centroid = tile_mask.geometry().centroid()

        for year in YEARS:

            samples = shuffle(samples, seed=1)

            dfTileYear = df[(df['tile'] == float(tile)) & (
                df['year'] == year)]

            nSamplesClass = list(
                dfTileYear[['class', 'n_samples']].values.tolist())

            samplesFinal = ee.FeatureCollection([])

            for classId, nSamples in nSamplesClass:
                samplesFinal = samplesFinal.merge(samples.filter(
                    ee.Filter.eq('class', classId)).limit(nSamples))

            # image feature space
            image = ee.Image('{}/{}-{}-{}'.format(
                ASSETS['feature_space'], int(tile), year, INPUT_VERSION))

            image = image.select(FEATURE_SPACE)

            # traning the classifier
            classifier = ee.Classifier.smileRandomForest(
                numberOfTrees=50,
            ).train(samples, 'class', FEATURE_SPACE)

            integrated = image\
                .select(FEATURE_SPACE)\
                .classify(classifier)

            integrated = image.select('mode')\
                .where(integrated.neq(0), integrated)\
                .rename(['classification'])

            integrated = integrated.mask(tile_mask)

            geometry = tile_mask.geometry()

            name = '{}-{}-{}'.format(int(tile), year, OUTPUT_VERSION)

            integrated = integrated.toByte()\
                .set('version', OUTPUT_VERSION)\
                .set('year', year)\
                .set('tile', tile)

            task = ee.batch.Export.image.toAsset(
                image=integrated,
                description=name,
                assetId='{}/{}'.format(ASSETS['output'], name),
                pyramidingPolicy={".default": "mode"},
                region=geometry.getInfo()['coordinates'],
                scale=30,
            )

            if name not in names:
                print('Exporting {}...'.format(name))
                task.start()
    except Exception as error:
        print(error)