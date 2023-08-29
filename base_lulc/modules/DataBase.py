#!/usr/bin/env python

# Import earthengine API
import ee

# Initialise
ee.Initialize()

PARCELA = 'ft:11DvHLk2KnQXTkLsViB-bdiqYqzt0Yy7w6MhOOd6v'
PBUFFER = 'ft:1vCQS62EE3PLsEtn7Vd8Vjcc6-Wh6ZABy5EadrjvU'
TOCONES = 'ft:1VOM2pmWncUV0rh2i6rZI6RyM60ie9UxfJxMXA1X5'
DERRIBE = 'ft:1qLAvVr0pbfxfzQ6w7hUM5nmiFwTDTD6-iS46PNWt'

parcela = ee.FeatureCollection(PARCELA)
pBuffer = ee.FeatureCollection(PBUFFER)
tocones = ee.FeatureCollection(TOCONES)
derribe = ee.FeatureCollection(DERRIBE)


def getTocon(provincia=None,
             nparcela=None,
             dano=None,
             pudricion=None):
    """"Filtrar tocones data tables
    Parameters:
        Provincias (str):...
        Nparcela (int):...
        Dano (int):...
        Pudricion (int):...

    Returns
        dictionary:...
    """

    eeFilter = ee.Filter.And()

    if provincia:
        eeFilter = ee.Filter.And(
            eeFilter, ee.Filter.eq('Provincia', provincia))

    if nparcela:
        eeFilter = ee.Filter.And(
            eeFilter, ee.Filter.eq('nParcela', nparcela))

    if dano:
        eeFilter = ee.Filter.And(
            eeFilter, ee.Filter.eq('dano', dano))

    if pudricion:
        eeFilter = ee.Filter.And(
            eeFilter, ee.Filter.eq('pudricion', pudricion))

    toconesCol = tocones.filter(eeFilter)
    derribeCol = derribe.filter(eeFilter)
    parcelaCol = parcela.filterBounds(toconesCol)
    pbufferCol = pBuffer.filterBounds(toconesCol)

    return {
        'tocones': toconesCol,
        'derribe': derribeCol,
        'parcela': parcelaCol,
        'buffers': pbufferCol,
    }
