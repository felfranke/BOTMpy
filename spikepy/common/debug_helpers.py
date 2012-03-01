# -*- coding: utf-8 -*-
#_____________________________________________________________________________
#
# Copyright (C) 2011 by Philipp Meier, Felix Franke and
# Berlin Institute of Technology
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#_____________________________________________________________________________
#
# Affiliation:
#   Bernstein Center for Computational Neuroscience (BCCN) Berlin
#     and
#   Neural Information Processing Group
#   School for Electrical Engineering and Computer Science
#   Berlin Institute of Technology
#   FR 2-1, Franklinstrasse 28/29, 10587 Berlin, Germany
#   Tel: +49-30-314 26756
#_____________________________________________________________________________
#
# Acknowledgements:
#   This work was supported by Deutsche Forschungs Gemeinschaft (DFG) with
#   grant GRK 1589/1
#     and
#   Bundesministerium für Bildung und Forschung (BMBF) with grants 01GQ0743
#   and 01GQ0410.
#_____________________________________________________________________________
#

"""helper functions for debug output"""
__docformat__ = 'restructuredtext'
__all__ = ['STD_INFO', 'STD_ERROR', 'set_std_info', 'd_info', 'd_err',
           'd_var']

##---IMPORTS

import sys

##---CONSTANTS

global STD_INFO
STD_INFO = sys.stdout
global STD_ERROR
STD_ERROR = sys.stderr

##---FUNCTIONS

def set_std_info(stream):
    """relocate standard info stream"""

    if not hasattr(stream, 'write'):
        raise TypeError('need to implement the file/Stream interface!')
    STD_INFO = stream


def d_info(*args):
    """debug output to info stream"""

    _write_to_stream(STD_INFO, args[0] % args[1:])


def d_err(*args):
    """debug output to error stream"""

    _write_to_stream(STD_ERROR, args[0] % args[1:])


def d_var(*args):
    """debug output of :var: in format "<name> : value" to info stream"""

    if len(args) > 0:
        for item in args:
            try:
                _write_to_stream(STD_INFO, '%s : %s\n' % (
                    item.__class__.__name__, item))
            except:
                _write_to_stream(STD_INFO, ':: unknown item ::\n')


def _write_to_stream(s, text):
    s.write(text)

##---MAIN

if __name__ == '__main__':
    pass
