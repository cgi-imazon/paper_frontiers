
/**
 * 
 * assets
 * 
*/

var year = '2021'

var assetMb = 'projects/imazon-simex/LULC/COLLECTION7/integrated-adj';
var assetSp = 'users/jailson/impervious/samples_by_year/imp_sp_' + year + '_2';

/**
 * 
 * 
 * 
*/

var lulc = ee.ImageCollection(assetMb)
    .filter(ee.Filter.eq('year', parseInt(year))).mosaic();
    
var samples = ee.FeatureCollection(assetSp);


var samplesSld = ee.FeatureCollection([
  samples.filter(ee.Filter.eq('label', 0)).map(function(feat) {
    return feat.set('style', {'color': '#ffffff'})
  }),
  samples.filter(ee.Filter.eq('label', 1)).map(function(feat) {
    return feat.set('style', {'color': '#ff0000'})
  })  
]).flatten();

samplesSld = samplesSld.style({styleProperty:'style'});
  
/**
 * 
 * filter samples 
 * 
*/ 

// keep this props
var props = [
  'version',
  'grid',
  'gv_median',
  'gvs_median',
  'label',
  'ndfi_median',
  'nir_median',
  'npv_median',
  'shade_median',
  'soil_median',
  'swir1_median',
  'year'
]

var builtSp = samples.filter(ee.Filter.eq('label', 1));
var noBuilt = samples.filter(ee.Filter.eq('label', 0));

var nonNaturalAreas = lulc.neq(3)
  .and(lulc.neq(4))
  .and(lulc.neq(5))
  .and(lulc.neq(49))
  .and(lulc.neq(11))
  .and(lulc.neq(12))
  .and(lulc.neq(32))
  .and(lulc.neq(29))
  .and(lulc.neq(50))
  .and(lulc.neq(13))
  .and(lulc.neq(33));
    
nonNaturalAreas = nonNaturalAreas.selfMask().rename('no_natural');

// filter samples excluding forest and water classes
var samplesInNonNat = nonNaturalAreas.sampleRegions({
  collection: builtSp, 
  properties: null, 
  scale: 30, 
  geometries: true
});

samplesInNonNat = samplesInNonNat.select(props)

var samplesFiltered = samplesInNonNat.merge(noBuilt);

    
/**
 * 
 * 
 * 
*/

var vis = {
    min: 0,
    max: 62,
    palette: paletteMapBiomas,
    format: 'png'
};


/**
 * 
 * 
 * 
*/

Map.addLayer(lulc, vis, 'mapbiomas');
Map.addLayer(nonNaturalAreas, {}, 'naturalAreas');
Map.addLayer(samplesSld, {}, 'amostras');

/**
 * 
 * export samples
 * 
*/

var desc = 'imp_sp_' + year + '_3';

Export.table.toAsset(samplesFiltered, desc, 'users/jailson/impervious/samples_by_year/' + desc);

