
var assetImage = 'users/jailson/impervious/classification/impervious_classification_2021_3';
var assetCol1 = 'users/jailson/impervious/classification';
var assetCol2 = 'projects/imazon-simex/MAPBIOMAS/PAPER/IMPERMEAVEL/impermeavel_grid';
var assetGrid = 'users/jailson/hyper_grids';
var assetAmz = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';


var years = [
  '1986',
  '1987',
  '1988',
  // ...
]

/**
 * 
 * 
*/

function spatialFilter(image, params) {

    // gera uma camada com pixels conectados
    var pxRuido = image.eq(params['class_target'])
        .selfMask()
        .connectedPixelCount(params['px_connected'] + 1, true);
    
    // filtra os pixels conectados de acordo com o limiar
    pxRuido = pxRuido.mask(pxRuido.lte(params['px_connected']));
    
    // calcula a area de cada obj de pixel conectado
    pxRuido = pxRuido.multiply(params['obj_size'])
        .divide(params['coef_coversao'])
    
    // filtra os pixels conectados de acordo com o limiar
    pxRuido = pxRuido.mask(pxRuido.lte(params['area_minima']));
    
    return image.where(pxRuido, params['class_to']).byte();

}

function majorityFilter(image) {
  
  var kernel = ee.Kernel.manhattan(3);
  
  image = image.reduceNeighborhood({
    reducer: ee.Reducer.mode(), 
    kernel: kernel
  });
  
  image = image.reproject('epsg:4326', null, 30)
  
  return image.selfMask()
  
}

/**
 * 
 * 
*/


var amzBiome = ee.FeatureCollection(assetAmz).filter(ee.Filter.eq('Bioma', 'Amazônia')); 

var grids = ee.ImageCollection(assetGrid)

var assetOutput = 'projects/imazon-simex/MAPBIOMAS/PAPER/IMPERMEAVEL/impermeavel';

var version = '3'

/**
 * 
 * years
 * 
*/

years.forEach(function(year) {
  

  var imagev2 = ee.ImageCollection(assetCol2)
      .filter(ee.Filter.eq('year', year)).mosaic();
      
  imagev2 = majorityFilter(imagev2)
  
  var classified = imagev2.selfMask()//.mask(wp.gt(0.5)).selfMask()
  
    
  classified = classified.byte();
  classified = classified
      .set('biome', 'AMAZONIA')
      .set('collection_id', 8.0)
      .set('territory', 'BRAZIL')
      .set('source', 'IMAZON')
      .set('version', 2)
      .set('year', parseInt(year))
      .set('description', 'classificacao de áreas construidas sem máscara.');
        
  var desc = 'impervious_' + year + '_' + version 
  
  Export.image.toAsset({
    image: classified,
    description: desc,
    assetId: assetOutput + '/' + desc,
    pyramidingPolicy: {'.default': 'mode'},
    scale: 30,
    region: geometry,
    maxPixels:1e13
  })

});






/**
 * 
 * 
*/






