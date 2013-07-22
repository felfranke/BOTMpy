# -*- coding: utf-8 -*-
#_____________________________________________________________________________
#
# Copyright (c) 2012 Berlin Institute of Technology
# All rights reserved.
#
# Developed by:	Philipp Meier <pmeier82@gmail.com>
#               Neural Information Processing Group (NI)
#               School for Electrical Engineering and Computer Science
#               Berlin Institute of Technology
#               MAR 5-6, Marchstr. 23, 10587 Berlin, Germany
#               http://www.ni.tu-berlin.de/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal with the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the documentation
#   and/or other materials provided with the distribution.
# * Neither the names of Neural Information Processing Group (NI), Berlin
#   Institute of Technology, nor the names of its contributors may be used to
#   endorse or promote products derived from this Software without specific
#   prior written permission.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# WITH THE SOFTWARE.
#_____________________________________________________________________________
#
# Acknowledgements:
#   Philipp Meier <pmeier82@gmail.com>
#_____________________________________________________________________________
#

"""scaling of multi channeled input data to assert normal background"""
__docformat__ = 'restructuredtext'
__all__ = ['mad_scaling']

##--- IMPORTS

import scipy as sp
from .util import *

##---FUNCTIONS

def mad_scaling(X, center=None, constant=None, axis=0):
    """scale multi channeled input s.t. the background is standard normal

    :param sp.ndarray X: multi channeled input data [sample, channel]
    :param ndarray center: will be used to calculate the residual in X,
    if None use the median of X

        Default=None
    :param float constant: constant to use for the scale value,
    if None use the constant corresponding to a normal distribution

        Default=None
    """

    # init
    X = sp.asarray(X)
    ns, nc = X.shape
    center = sp.ones(nc) * (center or sp.median(X, axis=axis))
    if constant is None:
        constant = 1. / sp.stats.norm.ppf(0.75)

    # transform
    Xresidual = sp.fabs(X - center)
    scale = constant * sp.median(Xresidual, axis=axis)
    return X / scale, scale

##---MAIN

if __name__ == '__main__':
    pass
