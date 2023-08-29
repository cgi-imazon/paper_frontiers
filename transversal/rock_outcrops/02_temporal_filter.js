var assetAfl = 'users/jailson/mapbiomas/afloramento_theme';
var assetAmz = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';

/**
 * 
 * 
*/

var amzBiome = ee.FeatureCollection(assetAmz).filter(ee.Filter.eq('Bioma', 'Amazônia')); 

var afl = ee.ImageCollection(assetAfl);

/**
 * 
 * 
*/

afl = afl.toBands()
afl = afl.unmask(0)


var freqAfl = afl.reduce(ee.Reducer.sum()).rename('freq').clip(amzBiome);
var freqAflP = freqAfl.divide(afl.bandNames().length())

/**
 * 
 * rock outcrop mask 
*/

var thres = 7

var rockMask = freqAfl.where(freqAfl.lt(thres), 0).selfMask();
var rockMask2 = freqAflP.mask(freqAflP.gt(0.2)).selfMask()

var visAfl = {
    min:0,
    max:35,
    palette:["042333","2c3395","744992","b15f82","eb7958","fbb43d","e8fa5b"],
    bands:['freq']
}

var f = rockMask.visualize(visAfl);
var f2 = rockMask2.visualize({
    max:1,
    palette:["042333","2c3395","744992","b15f82","eb7958","fbb43d","e8fa5b"],
})

Map.addLayer(freqAfl.selfMask(), visAfl, 'frequency of rock', false);
Map.addLayer(f, {}, 'frequency thresh');
Map.addLayer(rockMask2, {
    min:0,
    max:0.4,
    palette:["042333","2c3395","744992","b15f82","eb7958","fbb43d","e8fa5b"],
}, 'frequency thresh 2');

Export.image.toAsset({
  image: f, 
  description: 'rock_mask', 
  pyramidingPolicy: {'.default': 'mode'}, 
  region: geometry, 
  scale:30, 
  maxPixels: 1e13
})









