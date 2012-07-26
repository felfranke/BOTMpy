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

__docformat__ = 'restructuredtext'

##---IMPORTS

from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
except ImportError:
    build_ext = None
import numpy

##--HELPERS

def find_version():
    """read version from spikepy.__init__"""

    try:
        f = open('./spikepy/__init__.py', 'r')
        try:
            for line in f:
                if line.startswith('__version__'):
                    rval = line.split()[-1][1:-1]
                    break
        finally:
            f.close()
    except:
        rval = '0'
    return rval

##---DEFINITIONS

DESC_TITLE = 'SpikePy : online spike sorting with linear fitlers'
DESC_LONG = ''.join([DESC_TITLE, '\n\n', open('README', 'r').read()])

##---USE_CYTHON

ext_mod_list = []
if build_ext is not None:
    ext_mod_list.append(
        Extension(
            'spikepy.common.mcfilter.mcfilter_cy',
            ['spikepy/common/mcfilter/mcfilter_cy.pyx'],
            include_dirs=[numpy.get_include()]))

##---MAIN

if __name__ == "__main__":
    setup(
        #main
        name="SpikePy",
        version=find_version(),
        packages=['spikepy', 'spikepy.common', 'spikepy.common.datafile',
                  'spikepy.common.mcfilter', 'spikepy.nodes'],
        requires=['scipy', 'mdp', 'tables', 'scikits.learn'],

        # metadata
        author="Philipp Meier",
        author_email="pmeier82@googlemail.com",
        maintainer="Philipp Meier",
        maintainer_email="pmeier82@googlemail.com",
        description=DESC_TITLE,
        long_description=DESC_LONG,
        license="MIT License",
        url='http://ni.tu-berlin.de',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics'],

        # cython
        cmdclass={'build_ext': build_ext},
        ext_modules=ext_mod_list)
