// GEE Link: https://code.earthengine.google.com/92693cf53978ae117c6cd482f758bbd0

//var anos = ['1985', '1986', '1987','1988', '1989', '1990','1991', '1992', '1993','1994', '1995', '1996','1997', '1998', '1999','2000', '2001', '2002','2003', '2004', '2005','2006', '2007', '2008','2009', '2010', '2011','2012', '2013', '2014','2015', '2016', '2017', '2018']
var anos = ['1985', '1986', '1987','1988', '1989', '1990','1991', '1992', '1993','1994', '1995', '1996','1997', '1998', '1999','2000', '2001', '2002','2003', '2004', '2005','2006', '2007', '2008','2009', '2010', '2011','2012', '2013', '2014','2015', '2016', '2017', '2018','2019','2020','2021']

var excludedClasses = [
    "Não Observado",
    "Erro",
    "Desmatamento",
    'Regeneração',
    "No Observado",
    "Error",
    "No observado",
    ".",
    '.',
    'NA',
];

var classes = ee.Dictionary({
  "Desmatamento":0,
  "Bosque Inundable": 6,
  "Bosque inundable": 6,
  "Formación Campestre": 12,
  "Formação Campestre": 12,
  "Formación campestre": 12,
  "Formación Campestre o Sabana": 12,
  "Formación sabánica/ Bosque abierto":4,
  "Formación Forestal": 3,
  "Formação Florestal": 3,
  "Formación forestal": 3,
  "Formação Savânica": 4,
  "Floresta Plantada": 9,
  "Pastos": 15,
  'Agricultura': 18,
  "Formación Natural No Forestal Inundable": 11,
  "Formación natural no forestal inundable": 11,
  "Área Úmida Natural Não Florestal": 11,
  "Glaciar": 34,
  "Manglar": 5,
  "Mangue": 5,
  "Mosaico de Agricultura y/o Pasto": 21,
  "Mosaico de agricultura y pasto":21,
  "Cultura Semi-Perene": 18,
  "Cultura Perene": 18,
  "Pastagem Cultivada": 15,
  "Cultura Anual": 18,
  "No Observado": 0,
  "No observado": 0,
  "Não Observado": 0,
  "Otra Formación Natural No Forestal": 13,
  "Otra formación natural no forestal": 13,
  'Otra área sin vegetación':25,
  "Outra Formação Natural Não Florestal": 13,
  "Otra Formación no Forestal": 13,
  "Otra formación no forestal": 13,
  "Río, Lago u Océano": 33,
  "Rio, Lago e Oceano": 33,
  "Rio, lago u océano":33,
  "Aquicultura": 33,
  "Sin consolidar": 0,
  "Não consolidado": 0,
  "Zonas sin vegetación": 22,
  "Área sin Vegetación": 22,
  "Área sin vegetación": 22,
  "Outra Área Não Vegetada": 25,
  "Afloramento Rochoso": 29,
  "Afloramientos rocosos":29,
  "Praia e Duna": 22,
  'Palma aceitera':35,
  "Infraestrutura Urbana": 24,
  'Infraestructura urbana': 24,
  "Infraestructura Urbana":24,
  "Mineração": 30,
  "Minería":30
});

//var assetSamples = 'projects/mapbiomas-workspace/VALIDACAO/MAPBIOMAS_100K_POINTS_utf8';
//var assetMapBiomas = 'projects/mapbiomas-workspace/public/collection4/mapbiomas_collection40_integration_v1'
//var assetMapBiomas = 'projects/mapbiomas-workspace/COLECAO4_1/mapbiomas-collection41-integration-v8'

//var assetSamples = 'users/vieiramesquita/MAPBIOMAS/mapbiomas_amazonia_50K_RAISG_plus_Brasil_v4'
var assetSamples = 'projects/mapbiomas-workspace/VALIDACAO/mapbiomas_amazonia_50K_RAISG_plus_Brasil_v10'
var assetMapBiomas = 'projects/mapbiomas-raisg/public/collection4/mapbiomas_raisg_panamazonia_collection4_integration_v1'

//var folder = 'ACC_COL4_VF1'
var folder = 'PANAMAZONIA_COL4_ACC_v3'

print(ee.FeatureCollection(assetSamples).first())

//Map.addLayer(ee.Image(assetMapBiomas).select('classification_2020').rename('classification'))

anos.forEach(function(Year){
//for (var Year in anos){
  var year = Year;
  var ano = Year;

  var samples = ee.FeatureCollection(assetSamples)
  
  var cartas_unique = samples.aggregate_histogram('CARTA').keys()
  var declividade_strats = samples.aggregate_histogram('DECLIVIDAD').keys()
  
  var carta_stratsize_total = ee.Dictionary(
    cartas_unique.iterate(function(carta, cartas_remade){
        return ee.Dictionary(cartas_remade)
            .set(carta, samples.filter(ee.Filter.eq('CARTA', carta)).aggregate_histogram('DECLIVIDAD'))
  }, ee.Dictionary()))
  
  
  samples = samples.filter(ee.Filter.inList('CLASS_' + ano, excludedClasses).not())
                   .map(function (feature) {
                        return feature.set('year', ano)
                                      .set('reference', classes.get(feature.get('CLASS_' + ano)))
                                      //.set('COUNTRY',ee.Algorithms.If(ee.List([feature.get('COUNTRY')]).contains(''), 'Brazil', feature.get('COUNTRY')));
                         })
                         .filter(ee.Filter.neq('BORDA_' + ano,'TRUE'))

  samples = ee.FeatureCollection(ee.Algorithms.If(ee.Number.parse(year).gt(2018), samples.filter(ee.Filter.neq('COUNTRY','Brazil')),samples))
  
  //print(ee.FeatureCollection(samples).aggregate_histogram('COUNTRY'))
  //print(ee.FeatureCollection(samples).aggregate_histogram('CLASS_' + ano))
  //print(ee.FeatureCollection(samples).filter(ee.Filter.neq('COUNTRY','Brazil')).aggregate_histogram('COUNT_' + ano))
  
  var carta_stratsize_filtered = ee.Dictionary(cartas_unique.iterate(function(carta,cartas_remade){
    return ee.Dictionary(cartas_remade).set(carta,samples.filter(ee.Filter.eq('CARTA',carta))
    .aggregate_histogram('DECLIVIDAD'))
  },ee.Dictionary()))
  
  samples = samples.map(function(feat){
    
    feat = ee.Feature(feat)
    
    var carta = feat.get('CARTA')
    var strat = feat.get('DECLIVIDAD')
    var amos_prob = ee.Number(1).divide(ee.Number.parse(feat.get('PESO_AMOS')))
    //var year = ee.Number.format(ano)
    
    var vote_count = ee.Number.parse(feat.get(ee.String('COUNT_').cat(ano)))
  
    var strat_total_size = ee.Number(ee.Dictionary(carta_stratsize_total.get(carta)).get(strat))
    var strat_filtered_size = ee.Number(ee.Dictionary(carta_stratsize_filtered.get(carta)).get(strat))
    
    
    
    var adj_factor = strat_filtered_size.divide(strat_total_size)
    var new_prob = amos_prob.multiply(ee.Number.parse(adj_factor))
    
    //var tot_matrix = ee.Algorithms.If(ee.String(feat.get('POINTEDITE')).match('FALSE'), 6, 8)
    //var tot_votes = ee.Algorithms.If(ee.String(feat.get('POINTEDITE')).match('FALSE'), 3, 4)
  
    var vote_weight = ee.Algorithms.If(vote_count.eq(1), 1,
      ee.Algorithms.If(vote_count.eq(2), 0.5,
        ee.Algorithms.If(vote_count.eq(3), ee.Number(1).divide(3), 1)
      )
    )
    var peso_voto = amos_prob.multiply(ee.Number.parse(vote_weight))//((vote_count.multiply(tot_votes)).subtract(tot_votes)).divide(tot_matrix)
    return feat.set({'NEW_PROB':new_prob,'PESO_VOT':peso_voto, 'ADJ_FACTOR': adj_factor})
    
  })
  
  //print(ee.FeatureCollection(samples).aggregate_histogram('PESO_VOT'))
  
  var mapbiomas = ee.Image(assetMapBiomas).select('classification_'+ano).rename('classification')

  var result = mapbiomas.sampleRegions({
                          collection: samples, 
                          properties: ['reference','year','BIOMA','CARTA','N_TGRT_ID', 'LON', 'LAT','PROB_AMOS','PESO_AMOS','POINTEDITE','AMOSTRAS','REINSP','NEW_PROB','ADJ_FACTOR','PESO_VOT','COUNTRY'], 
                          scale: 30, 
                          geometries: false
                    })

  //print(result.limit(10))

  Export.table.toDrive({
    collection:result, 
    description:'acc_mapbiomas_' + ano, 
    folder: folder,
    fileFormat: 'csv'
  })
  
})