

var assetSamples = 'projects/mapbiomas-workspace/VALIDACAO/mapbiomas_85k_col2_points_w_edge_and_edited_v1'
var assetC8 = 'projects/imazon-simex/LULC/COLLECTION8/integrated-wl';
var assetOutput = 'projects/imazon-simex/LULC/COLLECTION8/integrated-paper';





/**
 * 
 * config
 * 
 */




var folder = 'accuracy_paper'

// mapped classes
var targetClasses = {
  '3':'Forest',
  '4':'Shrubland',
  '6': 'Flooded Forest',
  '11':'Wetland',
  '12':'Natural Grassland',
  '15':'Pastureland',
  '18':'Cropland',
  '22':'Bareland and Impervious',
  '29':'Rock Outcrop',
  '33':'Water'
}

// lapig class samples
var normalizeClasses = {
    "AFLORAMENTO ROCHOSO": 29,
    "APICUM": 22,
    "CAMPO ALAGADO E ÁREA PANTANOSA": 11,
    "CANA": 18,
    "FLORESTA INUNDÁVEL": 6,
    "FLORESTA PLANTADA": 18,
    "FORMAÇÃO CAMPESTRE": 12,
    "FORMAÇÃO FLORESTAL": 3,
    "FORMAÇÃO SAVÂNICA": 4,
    "INFRAESTRUTURA URBANA": 22,
    "LAVOURA PERENE": 18,
    "LAVOURA TEMPORÁRIA": 18,
    "MANGUE": 3,
    "MINERAÇÃO": 22,
    "NÃO OBSERVADO": 0,
    "OUTRA FORMAÇÃO NÃO FLORESTAL": 12,
    "OUTRA ÁREA NÃO VEGETADA": 22,
    "PASTAGEM": 15,
    "RIO, LAGO E OCEANO": 33,
    "VEGETAÇÃO URBANA": 3
}

var biome = 'Amazônia';

var versionClassification = '13';

var years = [
    2021,2020,2019,2018,
    2017,2016,2015,2014,2013,
    2012,2011,2010,2009,2008,
    2007,2006,2005,2004,2003,
    2002, 2001, 2000,
    1999, 1998, 1997, 1996,
    1995, 1994, 1993, 1992,
    1991, 1990, 1989, 1988,
    1987, 1986, 1985
];

var selectors = [
    'reference','year','BIOMA','CARTA','N_TGRT_ID', 'LON', 'LAT','PROB_AMOS',
     'border',
    'PESO_AMOS','POINTEDITE','AMOSTRAS','REINSP','NEW_PROB','ADJ_FACTOR','PESO_VOT'
]





/**
 * 
 * input data
 * 
 */




var samples = ee.FeatureCollection(assetSamples)
        .filter('BIOMA == "Amazônia"');

var classification = ee.ImageCollection(assetC8)
    .filter('version == "' + versionClassification + '"');





/**
 * 
 * helper functions
 * 
 */

// get proportion of slope classes by tile
function joinProperties(primary, secondary, key, selectors) {

    // Use an equals filter to specify how the collections match.
    var toyFilter = ee.Filter.equals({
        leftField: key,
        rightField: key
    });

    // Define the join.
    var innerJoin = ee.Join.saveAll('primary', 'secondary');

    // Apply the join.
    var joined =  innerJoin.apply(primary, secondary, toyFilter);
    
    joined = joined.map(function(feat) {
      
      var tile = feat.get('CARTA');
      
      var col = ee.FeatureCollection(ee.List(feat.get('primary')));
      
      var slopesCount = col.aggregate_histogram('DECLIVIDAD');
      
      feat = feat.set(slopesCount).set('primary', '')
      
      return feat.set('CARTA', tile)
      
    })
    
    return ee.FeatureCollection(joined)

}

/**
 * 
 * iterate over years
 * 
 */

years.forEach(function(year) {

    var cYear = 'CLASS_' + String(year);
    var countYear = 'COUNT_' + String(year);
    var borderYear = 'BORDA_' + String(year);


    var classificationYear = ee.Image(classification.filter('year == ' + String(year)).first())

    var tiles = samples.aggregate_histogram('CARTA').keys();
    // var slopeRanges = samples.aggregate_histogram('DECLIVIDAD').keys()
    
    
    // step 1 get tiles per slope ranges
    var featTiles = ee.List(tiles).map(function(feat) {return ee.Feature(null, {'CARTA': feat})});
        featTiles = ee.FeatureCollection(featTiles);

    // step 2 join tiles and slopes
    var tilesBySlopesAll = joinProperties(featTiles, samples, 'CARTA', ['DECLIVIDAD'])

    
    var samplesClsValues = samples.remap(
      ee.Dictionary(normalizeClasses).keys(), 
      ee.Dictionary(normalizeClasses).values(), 
      cYear
    );
    
    samplesClsValues = samplesClsValues.map(function(feat) {

        var tile = feat.get('CARTA');
        var slope = feat.get('DECLIVIDAD');

        var border = ee.Algorithms.If(
           ee.String(feat.get(borderYear)).equals('TRUE'),
            1, 0
        )

        var sampleProb = ee.Number(1).divide(ee.Number.parse(feat.get('PESO_AMOS')));
        var countVote = ee.Number.parse(feat.get(countYear));

        //var slopeTotalTile = tilesBySlopesAll
        //    .filter(ee.Filter.eq('CARTA', ee.String(tile)));
        
        //slopeTotalTile = ee.Feature(slopeTotalTile.first())
        //slopeTotalTile = ee.Number(slopeTotalTile.get(ee.String(slope)));

        //var adjFactor = slopeTotalTile.divide(slopeTotalTile);
        //var newProb = sampleProb.multiply(ee.Number.parse(adjFactor))

        // vote weight
        var conditionOne = ee.Algorithms.If(countVote.eq(3), ee.Number(1).divide(3), 1);
        var conditionTwo = ee.Algorithms.If(countVote.eq(2), 0.5, conditionOne);

        var voteWeight = ee.Algorithms.If(countVote.eq(1), 1, conditionTwo);
            voteWeight = sampleProb.multiply(ee.Number.parse(voteWeight));

        feat = feat.set({
            'NEW_PROB':sampleProb,
            'PESO_VOT':voteWeight, 
            'ADJ_FACTOR': 1,
            'year': year,
            'reference': feat.get(cYear),
            'border': border
        })

        return feat
    });
    
    var result = classificationYear.sampleRegions({
        collection: samplesClsValues, 
        properties: selectors, 
        scale: 30, 
        geometries: false
    })

    Export.table.toDrive({
        collection:result, 
        description:'acc_mapbiomas_' + year, 
        folder: folder,
        fileFormat: 'csv'
    })
});





