
/**
 * 
 * 
 * 
*/


var assetClassification = 'projects/imazon-simex/MAPBIOMAS/PAPER/IMPERMEAVEL/impermeavel';
var assetAmz = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';


/**
 * 
 * 
 * 
*/

var amzBiome = ee.FeatureCollection(assetAmz)
    .filter(ee.Filter.eq('Bioma', 'Amazônia')); 

var years = [
  2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014,
  2013, 2011, 2010, 2009, 2008, 2007, 2006, 2005,
  2004, 2003, 1999, 1998, 1997, 1996, 1995, 1994,
  1993, 1992, 1990, 1989, 1988, 1987, 1986
].reverse();

var idInt = ee.List.sequence(1, years.length, 1);
var idx = idInt.map(function(id) {return ee.String(ee.Number(id).int())});
var dict = ee.Dictionary.fromLists(idx, years); 


var classification = ee.ImageCollection(assetClassification)
    .filter(ee.Filter.eq('version', 3))
    .toBands()
    .rename(years.map(function(year){
        return 'classification_'+ String(year);
    })
);
 
/**
 * 
 * temporal filter
 * 
*/  

var iter = ee.List(idInt).slice(1, 30, 1).iterate(function(id, result) {
  
  id = ee.Number(id).int();

  result = ee.Image(result).unmask(0)
  
  var pYear = dict.get(ee.Number(id).subtract(1));
  var cYear = dict.get(ee.Number(id));
  var nYear = dict.get(ee.Number(id).add(1));
  
  var pYearInt = ee.Number(pYear).int();
  var cYearInt = ee.Number(cYear).int();
  var nYearInt = ee.Number(nYear).int();
  
  var pBand = ee.String('classification_').cat(ee.String(pYearInt));
  var cBand = ee.String('classification_').cat(ee.String(cYearInt));
  var nBand = ee.String('classification_').cat(ee.String(nYearInt));
  
  var current = result.select(cBand);
  var previous = classification.select(pBand).unmask(0);
  var next = classification.select(nBand).unmask(0);

  // ------------------------------------------------------------------------
  // rules

  var rule1 = previous.eq(0).and(current.eq(1)).and(next.eq(0));
  var rule2 = previous.eq(0).and(current.eq(0)).and(next.eq(1));

  var ruleNot = current.eq(1);

  // ------------------------------------------------------------------------

  var ruleApply = ee.Algorithms.If(
    cYearInt.lt(ee.Number(2021).int()),
    rule1.or(rule2),
    ruleNot
  )
  
  
  // ------------------------------------------------------------------------
  // apply rules
  
  var filtered = current.where(ruleApply, 0).selfMask();
  
  
  return result.addBands(filtered, [cBand], true);
  
}, classification);

var imageFiltered = ee.Image(iter).selfMask().clip(amzBiome);


/**
 * 
 * visualization params
 * 
*/

var visParams = {
  palette: ['black', 'red'],
  min:0, max:1,
  bands:['classification_2020']
};

var visParams2 = {
  palette: ['black', 'white'],
  min:0, max:1,
  bands:['classification_2020']
};

/**
 * 
 * display data
 * 
*/

Map.addLayer(classification.clip(amzBiome), visParams);
Map.addLayer(imageFiltered, visParams2);

