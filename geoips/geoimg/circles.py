# coding=utf-8

"""
circles.py
Created by Stephan Hügel on 2014-05-22
Copyright Stephan Hügel
Convenience functions for calculating and drawing circles on a projected map,
based on great-circle distances
Almost all code from:
http://www.geophysique.be/2011/02/20/matplotlib-basemap-tutorial-09-drawing-circles/
License: MIT
"""
__author__ = 'urschrei@gmail.com'


# Installed Libraries
import numpy as np



class CourseException(Exception):
    """ Simple error class """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



def _gccalc(lon, lat, azimuth, maxdist=None):
    """
    Original javascript on http://williams.best.vwh.net/gccalc.htm
    Translated into python by Thomas Lecocq
    This function is a black box, because trigonometry is difficult
    
    """
    glat1 = lat * np.pi / 180.
    glon1 = lon * np.pi / 180.
    s = maxdist / 1.852243
    faz = azimuth * np.pi / 180.
 
    EPS = 0.00000000005
    if ((np.abs(np.cos(glat1)) < EPS) and not (np.abs(np.sin(faz)) < EPS)):
        raise CourseException("Only North-South courses are meaningful")

    a = 6378.137 / 1.852243
    f = 1 / 298.257223563
    r = 1 - f
    tu = r * np.tan(glat1)
    sf = np.sin(faz)
    cf = np.cos(faz)
    if (cf == 0):
        b = 0.
    else:
        b = 2. * np.arctan2 (tu, cf)

    cu = 1. / np.sqrt(1 + tu * tu)
    su = tu * cu
    sa = cu * sf
    c2a = 1 - sa * sa
    x = 1. + np.sqrt(1. + c2a * (1. / (r * r) - 1.))
    x = (x - 2.) / x
    c = 1. - x
    c = (x * x / 4. + 1.) / c
    d = (0.375 * x * x - 1.) * x
    tu = s / (r * a * c)
    y = tu
    c = y + 1
    while (np.abs (y - c) > EPS):
        sy = np.sin(y)
        cy = np.cos(y)
        cz = np.cos(b + y)
        e = 2. * cz * cz - 1.
        c = y
        x = e * cy
        y = e + e - 1.
        y = (((sy * sy * 4. - 3.) * y * cz * d / 6. + x) *
            d / 4. - cz) * sy * d + tu

    b = cu * cy * cf - su * sy
    c = r * np.sqrt(sa * sa + b * b)
    d = su * cy + cu * sy * cf
    glat2 = (np.arctan2(d, c) + np.pi) % (2*np.pi) - np.pi
    c = cu * cy - su * sy * cf
    x = np.arctan2(sy * sf, c)
    c = ((-3. * c2a + 4.) * f + 4.) * c2a * f / 16.
    d = ((e * cy * c + cz) * sy * c + y) * sa
    glon2 = ((glon1 + x - (1. - c) * d * f + np.pi) % (2*np.pi)) - np.pi

    baz = (np.arctan2(sa, b) + np.pi) % (2 * np.pi)

    glon2 *= 180./np.pi
    glat2 *= 180./np.pi
    baz *= 180./np.pi
    return (glon2, glat2, baz)


def circle(m, centerlon, centerlat, radius, *args, **kwargs):
    """
    Return lon, lat tuples of a "circle" which matches the chosen Basemap projection
    Takes the following arguments:
    m = basemap instance
    centerlon = originating lon
    centrelat = originating lat
    radius = radius
    """
    glon1 = centerlon
    glat1 = centerlat
    X = []
    Y = []
    for azimuth in range(0, 360):
        glon2, glat2, baz = _gccalc(glon1, glat1, azimuth, radius)
        X.append(glon2)
        Y.append(glat2)
    X.append(X[0])
    Y.append(Y[0])

    proj_x, proj_y = m(X,Y)
    return zip(proj_x, proj_y)
