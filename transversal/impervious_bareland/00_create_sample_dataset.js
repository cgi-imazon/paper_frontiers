/**
 * 
 * this script creates a dataset of impervious/bareland samples based on
 * Google DYNAMICWORLD map https://www.nature.com/articles/s41597-022-01307-4
 * 
 */

// assets
var assetAmz = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';
var assetDynamic = 'GOOGLE/DYNAMICWORLD/V1';
var assetOutput = 'users/jailson/impervious/samples_imp'

/**
 * 
 * config information
 * 
*/

var version = '2'

var year = 2022;

var classValues = [
  0, 1, 2, 3, 4, 5, 6, 7
];

var classPoints = [
  5000,
  5000,
  5000,
  5000,
  5000,
  5000,
  10000,
  5000
];

/**
 * 
 * input data
 * 
 */


var biome = ee.FeatureCollection(assetAmz)
    .filter(ee.Filter.eq('Bioma', 'Amazônia'));
    
var lulc = ee.Image(assetMapbiomas)
    .clip(biome)
    .select('classification_' + String(year));
    
var dynamic = ee.ImageCollection(assetDynamic)   
    .filterDate(String(year) + '-01-01', String(year) + '-12-30')
    .filterBounds(biome.geometry())

// extract mode from all classified scenes
dynamic = dynamic.select('label')
dynamic = dynamic.reduce(ee.Reducer.mode()).clip(biome)
dynamic = dynamic.select(['label_mode'], ['label'])


/**
 * 
 * get stratified samples
 * 
 */

var noBuiltSamples = dynamic.stratifiedSample({
  numPoints: 40000,
  classBand: 'label',
  region: biome.geometry(),
  scale: 30,
  geometries: true,
  classValues: classValues,
  classPoints: classPoints
})

noBuiltSamples = noBuiltSamples.remap([0, 1, 2, 3, 4, 5, 6, 7], [0, 0, 0, 0, 0, 0, 1, 0], 'label');


var samplesStyled = ee.FeatureCollection([
  noBuiltSamples.filter(ee.Filter.eq('label', 0)).map(function(feat) {
    return feat.set('style',{'color': '#ffffff'})
  }),
  noBuiltSamples.filter(ee.Filter.eq('label', 1)).map(function(feat) {
    return feat.set('style',{'color': '#ff0000'})
  }),
]);

/**
 * 
 * Export sample dataset
 * 
 */

var desc = 'built_samples_' + String(year) + '_' + version;

Export.table.toAsset(noBuiltSamples, desc, assetOutput + '/' + desc)





































