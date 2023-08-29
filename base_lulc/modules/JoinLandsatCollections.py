#!/usr/bin/env python

# Import earthengine API
import ee

# Initialise
ee.Initialize()


def JoinLandsatCollections(coll1, coll2):
    """Concatenates the bands of the images in secondary collection with
    the band of images in primary collection

    Parameters:
        collection1 (ee.ImageCollection): Primary image collection that
            will receive de new bands
        collection2 (ee.ImageCollection): Secondary image collection that
            will give the bands

    Returns:
        ee.ImageCollection: Image collection with joined band
    """

    eqfilter = ee.Filter.equals({
        'rightField': 'system:time_start',
        'leftField': 'system:time_start'
    })

    join = ee.Join.inner()

    joinedCollection = ee.ImageCollection(join.apply(coll1, coll2, eqfilter))\
        .map(lambda element: ee.Image.cat(element.get('primary'), element.get('secondary')))\
        .sort('system:time_start')

    return joinedCollection
