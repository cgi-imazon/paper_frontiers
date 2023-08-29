#!/usr/bin/env python

# Import earthengine API
import ee

# Initialise
ee.Initialize()


def _applyDam(image, imageReduced):
    """"Apply the DAM algorithm for one image

    Parameters:
        image (ee.Image): image on date[i]
        imageReduced (ee.Image): central tendecy image

    Returns:
        ee.Image: dam image classification
    """

    imageReduced = ee.Image(imageReduced)

    min = ee.Number(imageReduced.get('min'))
    max = ee.Number(imageReduced.get('max'))
    bandName = ee.Number(imageReduced.get('bandName'))

    image = ee.Image(image) \
        .select([bandName]) \
        .unmask(imageReduced.select(['reduced']))

    difference = imageReduced \
        .select(['reduced']) \
        .subtract(image) \
        .abs()

    degradation = difference.gte(min).And(difference.lte(max))
    deforestation = difference.gt(max)

    classified = degradation.where(deforestation.eq(1), 2)

    bandName = ee.String('b').cat(ee.String(image.get('date')))

    return imageReduced.addBands(classified.rename([bandName]))


def classify(collection,
             reducer=ee.Reducer.median(),
             bandName=None,
             min=15,
             max=35):
    """"Iterates over a collection and calculates DAM algorithm for each image

    Parameters:
        collection (ee.ImageCollection): collection containing index band
        reducer (ee.Reducer): ee.Reducer to central tendency
        bandName (str): index band name
        min (int): min threshold for classification
        max (int): max threshold for classification

    Returns:
        ee.Image: multiband image containing all detections by date
    """

    imageReduced = collection.select([bandName]) \
        .reduce(reducer) \
        .rename('reduced') \
        .set('bandName', bandName) \
        .set('min', min) \
        .set('max', max)

    classification = collection.iterate(_applyDam, imageReduced)

    return ee.Image(classification)
