var palettes = require('users/mapbiomas/modules:Palettes.js');


// assets
var asset = 'projects/imazon-simex/LULC/COLLECTION8/integrated-paper';



// config session
var version = '2'

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



// vis params
var vis = {
    min:0, max:62,
    palette: palettes.get('classification7')
}


// interate over years to visualize annual classification
years.forEach(function(year) {
  
    var classification = ee.ImageCollection(asset)
        .filter('version == "' + version + '"')
        .filter('year == ' + String(year));
        
    
    var image = ee.Image(classification.first());
    
    Map.addLayer(image, vis, 'classification - ' + String(year), false)
  
});










