


/**
 * 
 * functions here
 * 
*/



function shuffle(collection) {
  
  collection = collection.randomColumn('random', 1)
      .sort('random', true);
      
  collection = collection.map(function(feat) {
    return feat.set('new_id', ee.Number(feat.get('random')).multiply(1000000000).round())
  });
  
  var randomIdList = ee.List(collection.reduceColumns(ee.Reducer.toList(), ['new_id'])
      .get('list'));
      
  var sequentialIdList = ee.List.sequence(1, collection.size());
  
  var shuffled = collection.remap(randomIdList, sequentialIdList, 'new_id')
  
  return shuffled
}

function shuffleArr(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

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
    
    return image.where(pxRuido, params['to_class']).byte();

}

function majorityFilter(image) {
  
  var kernel = ee.Kernel.manhattan(1);
  
  image = image.reduceNeighborhood({
    reducer: ee.Reducer.mode(), 
    kernel: kernel
  });
  
  return image.reproject('epsg:4326', null, 30)
  
}

/**
 * 
 * assets
 * 
*/



var year = '2023';

var assetSp = 'users/jailson/impervious/samples_by_year/imp_sp_' + '2021' +'_3';
var assetGrid = 'users/jailson/hyper_grids';
var assetMosaics = 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2';
var assetAmz = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';
var assetImpervious = 'users/jailson/impervious/classification-c2';


/**
 * 
 * config
 * 
*/

var totalSamples = 8000

var samplesParams = {
  '0': totalSamples * 0.85,
  '1': totalSamples * 0.15
}

/**
 * 
 * load data 
 * 
*/

var listProcessed = ee.ImageCollection(assetImpervious)
    .filter(ee.Filter.eq('version', 1))
    .filter(ee.Filter.eq('year', parseInt(year)))
    .reduceColumns(ee.Reducer.toList(), ['system:index'])
    .get('list')


listProcessed = ee.List(listProcessed).map(function(index) {
  return ee.String(index).slice(16, 21)
});


print(listProcessed)



var grids = ee.ImageCollection(assetGrid)
    .filter(ee.Filter.inList('system:index', listProcessed).not())
    .filterBounds(geometry2)

var amzBiome = ee.FeatureCollection(assetAmz).filter(ee.Filter.eq('Bioma', 'Amazônia')); 

var mosaic = ee.ImageCollection(assetMosaics).filter(ee.Filter.and(
    ee.Filter.eq('biome', 'AMAZONIA'),
    ee.Filter.eq('collection', 8),
    ee.Filter.eq('year', parseInt(year))
)).mosaic().clip(geometry2); 

var samplesTrain = ee.FeatureCollection(assetSp);

var listGrids = grids.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list');

/**
 * 
 * make feature stacke mosaic
 * 
*/


var fs = mosaic.select([
  "gv_median", 
  "gvs_median",
  "soil_median", 
  "npv_median", 
  "shade_median", 
  "ndfi_median",
]);


samplesTrain = shuffle(samplesTrain)




/**
 * 
 * 
 * 
*/


listGrids.evaluate(function(listGrids) {
  
  listGrids.forEach(function(grid) {
    
    
    var currentGrid = grids.filter(ee.Filter.eq('system:index', grid));
    var currentImage = fs.clip(currentGrid.geometry());
    
    // get ramdom grids
    var ramdomSamplesList = shuffleArr(listGrids)
        ramdomSamplesList = ramdomSamplesList.slice(0, parseInt(listGrids.length * 0.3));
        
    var ramdonGridSp = samplesTrain.filter(ee.Filter.inList('grid', ramdomSamplesList))
    
    
    
    // current grid samples
    var currentGridSp = samplesTrain.filter(ee.Filter.eq('grid', grid));
    
    var samplesSelected = ramdonGridSp.merge(currentGridSp);
    
    samplesSelected = ee.FeatureCollection([
        samplesSelected.filter(ee.Filter.eq('label', 0)).limit(samplesParams['0']),
        samplesSelected.filter(ee.Filter.eq('label', 1)).limit(samplesParams['1']),
    ])
    
    samplesSelected = samplesSelected.flatten()



    var classifier = ee.Classifier.smileRandomForest(100).train(samplesSelected, 'label', [
      "gv_median", 
      "gvs_median",
      "soil_median", 
      "npv_median", 
      "shade_median", 
      "ndfi_median"
    ]);
  
    var classified = currentImage.classify(classifier)
        classified = classified.byte();
        classified = classified
            .set('biome', 'AMAZONIA')
            .set('collection_id', 8.0)
            .set('territory', 'BRAZIL')
            .set('source', 'IMAZON')
            .set('version', 1)
            .set('year', year)
            .set('description', 'classificacao de áreas construidas.');
            
    

    
    Map.addLayer(classified.randomVisualizer(), {}, grid)
    
    var desc = 'impervious_grid_' + grid + '_' + year + '_1' 

    Export.image.toAsset({
      image: classified,
      description: desc,
      assetId: 'users/jailson/impervious/classification-c2/' + desc,
      pyramidingPolicy: {'.default': 'mode'},
      scale: 30,
      region: currentGrid.geometry(),
      maxPixels:1e13
    })

  });
  
});