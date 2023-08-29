#!/usr/bin/env python

# Import earthengine API
import ee
import math

# Initialise
ee.Initialize()


def _addVariables(image):
    """Calcula a diferença (em anos) do ano inicial da coleção em relação ao ano de cada imagem,
    criando uma banda chamada 't'. Calcula também o seno e cosseno do tempo, criando as bandas
    cos e sin.

    Parameters:
        collection (ee.ImageCollection):...
        dateStart (str):...

    Returns:
        ee.ImageCollection: ...
    """

    dateStart = ee.Date(image.get('dateStart'))

    date = ee.Date(image.get('system:time_start'))

    years = date.difference(dateStart, 'year')

    image = image.addBands(ee.Image(years).rename('t').float())\
        .addBands(ee.Image.constant(1))

    timeRadians = image.select('t').multiply(2 * math.pi)

    cos = timeRadians.cos().rename('cos')
    sin = timeRadians.sin().rename('sin')

    image = image.addBands(cos).addBands(sin)

    return image.copyProperties(image, ['system:time_start'])


def addVariablesInterate(collection, dateStart):
    """Iterates over a collection and ...

    Parameters:
        collection (ee.ImageCollection):...
        dateStart (str):...

    Returns:
        ee.ImageCollection: ...
    """

    collection = collection \
        .map(lambda image: image.set('dateStart', dateStart)) \
        .map(_addVariables)

    return collection

#TODO: get a better name for this function. I sugest "fitHarmonicFunctions"
def functionCalculus(collection, index):
    """"Calcula o fit de funções harmônicas, a partir da regressão linear
        entre um índice passado como parametro (ndvi, ndfi, nbr, evi) e as bandas
        't','cos','sin'

        Parameters:
            collection (ee.ImageCollection):...
            index (str):...

        Returns:
            list: 
    """

    independents = ee.List(['constant', 't', 'cos', 'sin'])

    dependent = ee.String(index)

    trend = collection.select(independents.add(dependent)) \
        .reduce(ee.Reducer.linearRegression(independents.length(), 1))

    coefficients = trend.select('coefficients') \
        .arrayProject([0]) \
        .arrayFlatten([independents])

    detrended = collection.map(
        lambda image:
            image.select(dependent).subtract(image.select(independents)
                                             .multiply(coefficients)
                                             .reduce('sum')
                                             ).rename(dependent).copyProperties(image, ['system:time_start'])
    )

    fittedHarmonic = collection.map(
        lambda image:
            image.addBands(
                image.select(independents)
                .multiply(coefficients)
                .reduce('sum')
                .rename('fitted')
            )
    )

    return [detrended, fittedHarmonic]
