var assets = require('users/jailson/utils:assets');
    assets = assets.assets.samples;
    
var c = require('users/jailson/utils:calculations');

/*
*
*
*/

function toPoints(fc) {
  var img = ee.Image().paint(fc, 'class').rename('class')
  
  var pts = img.sampleRegions({
    collection: fc, 
    properties:['class'], 
    scale:50,
    geometries:true
  });
  
  return pts
}

function toStratPoints(fc, classValues, classPoints) {
  var img = ee.Image().paint(fc, 'class').rename('class')
  
  var pts = img.stratifiedSample({
    'numPoints': 1,
    'classBand': 'class',
    'classValues': classValues,
    'classPoints': classPoints,
    'region': fc.geometry(1),
    'scale': 30,
    'seed': 1,
    'dropNulls': true,
    'geometries': true,
  });
  
  return pts
}

/*
*
* assets 
*
*/

var assetAmz = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';
var assetMosaics = 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2';
var assetGrid = 'projects/imazon-simex/SAD/DATABASE/VECTOR/AMZ_grid'
var assetRoi = 'users/jailson/mapbiomas/samples/afloramento/roi';
var assetRockTnc = 'users/jailson/mapbiomas/samples/afloramento/amostras_afloramento_manual_pts';

/*
*
* data
*
*/

var nSamples = 30000

var featureSpace = [
  "gv_median", 
  "gvs_median",
  "soil_median", 
  "npv_median", 
  "shade_median", 
  "ndfi_median",
];

var classValues = [1, 2];
var classPts = [nSamples * 0.3, nSamples * 0.7]

/*
*
*/

var territory = ee.FeatureCollection(assetRoi);
var amzBiome = ee.FeatureCollection(assetAmz).filter(ee.Filter.eq('Bioma', 'Amazônia')); 

var mosaic = ee.ImageCollection(assetMosaics).filter(ee.Filter.and(
    ee.Filter.eq('biome', 'AMAZONIA'),
    ee.Filter.eq('collection', 7),
    ee.Filter.eq('year', 2021)
)).filterBounds(amzBiome).mosaic().clip(amzBiome); print(mosaic)

var dem = ee.Image("USGS/SRTMGL1_003").select('elevation').mask(mosaic.select('red_median'));
var slope = ee.Terrain.slope(dem).rename('slope');

// --------------------------------------------------------------------------------------------------------------

function radians(img) { return img.toFloat().multiply(3.1415927).divide(180); }

var srtm = ee.Image("USGS/SRTMGL1_003").clip(amzBiome); 
var gaussianKernel = ee.Kernel.gaussian(3, 2, 'pixels', true, 2);
var terrain = ee.call('Terrain', srtm.convolve(gaussianKernel));

var slope_ = radians(terrain.select(['slope']))
    .lt(0.076);

  slope_ = slope_
    .focal_max({radius: 50, units: 'meters'})
    .focal_min({radius: 50, units: 'meters'});

var hand30_1000 =  ee.Image("users/gena/GlobalHAND/30m/hand-1000");
var hand_class = hand30_1000.addBands(slope_).expression(
  "(b(0) <= 5.3) ? 0 : (b(0) <= 15 && b(0) > 5.3 ) ? 1 : (b(0) > 15 && b(1) == 0 ) ? 2 : (b(0) > 15 && b(1) == 1 ) ? 3 : 0"
).clip(amzBiome).rename('hand_class');

// --------------------------------------------------------------------------------------------------------------

var fs = mosaic.select(featureSpace).addBands(dem).addBands(slope).addBands(hand_class);

var featspace = fs


/*
*
* sampling
*
*/

//var rock = ee.FeatureCollection(assetRockTnc);
//var noRock = ee.FeatureCollection([no_afloramento]);


var samples = ee.FeatureCollection([r, n]);
var samplesPts = toPoints(samples)

//Export.table.toAsset(samplesPts, 'amostras_afloramento_manual_pts_v3')
Export.table.toAsset(ee.FeatureCollection([ee.Feature(geometry)]), 'pts')

var pxValues = featspace.sampleRegions({
  collection: samples, properties:['class'], scale:30, geometries:true
});


var rfParams = {
    'numberOfTrees': 50, //100
    'variablesPerSplit': 10,
    'minLeafPopulation': 25,
    'seed': 1
}

var classifier = ee.Classifier.smileRandomForest(rfParams).train(pxValues, 'class');
var classified = featspace.classify(classifier);


/*
| -------------------------------------------------------------------------------------------------------------
| spatial filters
| -------------------------------------------------------------------------------------------------------------
*/



var connected_px = 100; // min connected pixels
var min_area = 1; // min area = 1 ha
var obj_size = ee.Image.pixelArea();

var px_noise = classified.eq(2).selfMask().connectedPixelCount(connected_px + 1, true); // get connected pixels
    px_noise = px_noise.mask(px_noise.lt(connected_px)); // masks the filtered pixels
    px_noise = px_noise.multiply(obj_size).divide(ee.Image(10000)); // get pixel area in ha
    px_noise = px_noise.mask(px_noise.lte(min_area)); // masks according the min area (1ha)


var kernel = ee.Kernel.circle({radius: 1}); // creates a circle kernel
var opened = classified
             .focal_min({kernel: kernel, iterations: 5})
             .focal_max({kernel: kernel, iterations: 5});


var classified_filtered = classified.where(px_noise, opened); // replace the noise pixel

px_noise = classified.eq(1).selfMask().connectedPixelCount(connected_px + 1, true); // get connected pixels
px_noise = px_noise.mask(px_noise.lt(connected_px)); // masks the filtered pixels
px_noise = px_noise.multiply(obj_size).divide(ee.Image(10000)); // get pixel area in ha
px_noise = px_noise.mask(px_noise.lte(min_area)); // masks according the min area (1ha)

classified_filtered = classified_filtered.where(px_noise, 2).byte();

 
/*
*
* vis
*
*/

var visMos = {
  'bands': ['swir1_median','nir_median','red_median'],
  'gain': [0.08, 0.06, 0.2],
  'gamma': 0.85
};

var visAlos = {
  palette: '000040,0000ff,00ffff,ffffff,17ff08,f0ff04,ff7906,f13232,d70000,a50026',
  min:1,
  max:500
};

var visRockRef = {palette:['white'], min:1, max:1}

var visSlope = {
  min:1,
  max:30.018444061279297,
  palette:['000040','0000ff','00ffff','ffffff','17ff08','f0ff04','ff7906','f13232','d70000','a50026']
}

var visDem = {
  min:100,
  max:674,
  palette:['000040','0000ff','00ffff','ffffff','17ff08','f0ff04','ff7906','f13232','d70000','a50026']
}


/*
*
*
*/



Map.addLayer(mosaic, visMos, 'mosaic', false)
//Map.addLayer(classified, visRockRef, 'afloramento')
Map.addLayer(classified_filtered.mask(classified_filtered.eq(1)), visRockRef, 'afloramento', true, 0.65)
Map.addLayer(dem, visDem, 'dem', false);
Map.addLayer(slope, visSlope, 'slope', false)
