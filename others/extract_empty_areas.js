
var assetMosaics = 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2';
var assetBiome = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019'



var years = [
    1985, 1986, 1987, 1988,
    1989, 1990, 1991, 1992,
    1993, 1994, 1995, 1996,
    1997, 1998, 1999, 2000,
    2001, 2002, 2003, 2004,
    2005, 2006, 2007, 2008,
    2009, 2010, 2011, 2012,
    2013, 2014, 2015, 2016,
    2017, 2018, 
    2019, 2020,
    2021, 2022
];



var biome = ee.Feature(ee.FeatureCollection(assetBiome)
    .filter('Bioma == "Amazônia"').first());








var vis = {
  bands:['swir1_median'],
  gain: [0.08]
};

years.forEach(function(year) {
  
  var mosaicYear = ee.ImageCollection(assetMosaics)
      .filter('biome == "AMAZONIA"')
      .filter('year == ' + String(year))
      .select('swir1_median')
      .min()
      .clip(biome.geometry());
  
  var binary = mosaicYear.unmask(1000000).eq(1000000).selfMask().clip(biome.geometry());
  
  var pxArea = ee.Image.pixelArea().divide(10000).multiply(binary);
  
  var area = pxArea.reduceRegion({
      reducer: ee.Reducer.sum(),
      scale:30,
      geometry: biome.geometry(),
      maxPixels:1e13
  });
  
  var areaR = ee.Feature(null, {
    'year': year,
    'area_ha': area.get('area'),
  })
  
  var areas = ee.FeatureCollection([areaR]);
  
  Map.addLayer(binary, {min:0,max:1}, 'cloud', false)

  Export.table.toDrive({
    collection: areas, description: 'TABLE_CLOUD_REMAIN_' + String(year),fileFormat:'CSV'})

});










