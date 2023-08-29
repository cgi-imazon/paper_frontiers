#!/usr/bin/env python

# Import earthengine API
import ee

# Initialise
ee.Initialize()


def getNBR(image):
    """Calculate the NBR index

    Parameters:
        image (ee.Image): Reflectance image containing the bands:
        blue, red, green, nir, swir1, swir2

    Returns:
        ee.Image: Image containing the input bands and nbr band
    """

    exp = "(nir - swir2) / (nir + swir2)"

    nbr = image.expression(exp, {
        'nir': image.select('nir'),
        'swir2': image.select('swir2')
    })

    nbr = nbr.rename("nbr").float()

    return image.addBands(nbr)


def getNDVI(image):
    """Calculate the NDVI index

    Parameters:
        image (ee.Image): Reflectance image containing the bands:
        blue, red, green, nir, swir1, swir2

    Returns:
        ee.Image: Image containing the input bands and ndvi band
    """

    exp = "(nir - red)/(nir + red)"

    ndvi = image.expression(exp, {
        'nir': image.select('nir'),
        'red': image.select('red'),
        'blue': image.select('blue')
    })

    ndvi = ndvi.rename("ndvi").float()

    return image.addBands(ndvi)


def getEVI(image):
    """Calculate the NBR index

    Parameters:
        image (ee.Image): Reflectance image containing the bands:
        blue, red, green, nir, swir1, swir2

    Returns:
        ee.Image: Image containing the input bands and nbr band
    """

    exp = "2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)"

    evi = image.expression(exp, {
        'nir': image.select('nir'),
        'red': image.select('red'),
        'blue': image.select('blue')
    })

    evi = evi.rename("evi").float()

    return image.addBands(evi)
