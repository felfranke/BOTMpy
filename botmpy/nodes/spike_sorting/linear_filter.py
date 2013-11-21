# -*- coding: utf-8 -*-
#_____________________________________________________________________________
#
# Copyright (c) 2012-2013, Berlin Institute of Technology
# All rights reserved.
#
# Developed by:	Philipp Meier <pmeier82@gmail.com>
#
#               Neural Information Processing Group (NI)
#               School for Electrical Engineering and Computer Science
#               Berlin Institute of Technology
#               MAR 5-6, Marchstr. 23, 10587 Berlin, Germany
#               http://www.ni.tu-berlin.de/
#
# Repository:   https://github.com/pmeier82/BOTMpy
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
# Changelog:
#   * <iso-date> <identity> :: <description>
#_____________________________________________________________________________
#

"""linear filters in the time domain"""
__docformat__ = "restructuredtext"
__all__ = ["FilterError", "LinearFilterNode", "MatchedFilterNode"]

## IMPORTS

import scipy as sp
from collections import deque
from ...common import mcvec_from_conc, mcvec_to_conc, TimeSeriesCovE, MxRingBuffer, snr_maha
from ...mcfilter import mcfilter_hist
from ..base_node import Node

## CLASSES

class FilterError(Exception):
    pass


class LinearFilterNode(Node):
    """linear filter in the time domain

    This node applies a linear filter to the data and returns the filtered
    data. The derivation of the filter (f) from the pattern (xi) is
    specified in the implementing subclass via the 'filter_calculation'
    classmethod. The template will be averaged from a ringbuffer of
    observations. The covariance matrix is supplied from an external
    covariance estimator.

    This implementation uses `mcfilter.mcfilter_hist` method and only filters
    causal part of the input and stored the remainder in a history buffer.
    """

    ## special

    def __init__(self, tf, nc, ce, chan_set=None, rb_cap=None, dtype=None):
        """
        :param int tf: template length in samples
        :param int nc: template channel count
        :param TimeSeriesCovE ce: covariance estimator instance
        :param tuple chan_set: tuple of int designating the subset of channels this
            filter operates on. Defaults to tuple(range(nc))
        :param int rb_cap: capacity of the xi buffer
        :param dtype dtype: determines the internal dtype
        """

        # checks
        if tf <= 0:
            raise ValueError("tf <= 0")
        if nc <= 0:
            raise ValueError("nc <= 0")
        if chan_set is None:
            chan_set = tuple(range(nc))

        # super
        super(LinearFilterNode, self).__init__(output_dim=1, dtype=dtype)

        # members
        self._xi_buf = MxRingBuffer(
            capacity=rb_cap or 350, dimension=(tf, nc),
            dtype=self.dtype)
        self._ce = None
        self._f = None
        self._hist = sp.zeros((tf - 1, nc), dtype=self.dtype)
        self._chan_set = tuple(sorted(chan_set))
        self.ce = ce
        self.active = True

    def __str__(self):
        return "%s(tf=%s,nc=%s,cs=%s)" % (self.__class__.__name__, self.tf, self.nc, str(self._chan_set))

    ## properties - not settable

    def get_xi(self):
        return self._xi_buf.mean()

    xi = property(get_xi, doc="template (multi-channeled)")

    def get_xi_conc(self):
        return mcvec_to_conc(self._xi_buf.mean())

    xi_conc = property(get_xi_conc, doc="template (concatenated)")

    def get_tf(self):
        return self._xi_buf.dimension[0]

    tf = property(get_tf, doc="temporal extend [sample]")

    def get_nc(self):
        return self._xi_buf.dimension[1]

    nc = property(get_nc, doc="number of channels")

    def get_f(self):
        return self._f

    f = property(get_f, doc="filter (multi-channeled)")

    def get_f_conc(self):
        return mcvec_to_conc(self._f)

    f_conc = property(get_f_conc, doc="filter (concatenated)")

    ## properties settable

    def get_ce(self):
        return self._ce

    def set_ce(self, value):
        if not isinstance(value, TimeSeriesCovE):
            raise TypeError("ce is not of type TimeSeriesCovE")
        if value.get_tf_max() < self.tf:
            raise ValueError("tf_max of ce < than filter tf")
        if value.get_nc() < self.nc:
            raise ValueError("nc of cov_est < than filter nc")
        if value.is_initialised is False:
            raise ValueError("ce not initialised!")
        self._ce = value
        if len(self._xi_buf) > 0:
            self.calc_filter()

    ce = property(get_ce, set_ce, doc="covariance estimator")

    def get_snr(self):
        return snr_maha(
            sp.array([mcvec_to_conc(self.xi)]),
            self._ce.get_icmx(tf=self.tf, chan_set=self._chan_set))[0]

    snr = property(get_snr, doc="signal to noise ratio (mahalanobis distance)")

    ## Node interface

    def _execute(self, x):
        """apply the filter to data"""

        # DOC: sp.ascontiguousarray is here to assert continuous memory for
        #      the array. This is important for ctypes/cython implementations.
        x_in = sp.ascontiguousarray(x, dtype=self.dtype)[:, self._chan_set]
        rval, self._hist = mcfilter_hist(x_in, self._f, self._hist)
        return rval

    def is_invertible(self):
        return False

    def is_trainable(self):
        return False

    def _get_supported_dtypes(self):
        return ["float32", "float64"]

    ## filter interface

    def append_xi_buf(self, wf, recalc=False):
        """append waveforms to the xi_buffer

        :param ndarray wf: wavefom data [self.tf, self.nc]
        :param bool recalc: if True, call self.calc_filter after appending
        """

        self._xi_buf.append(wf)
        if recalc is True:
            self.calc_filter()

    def extend_xi_buf(self, wfs, recalc=False):
        """append an iterable of waveforms to the xi_buffer

        :type wfs: iterable of ndarray
        :param wfs: wavefom data [n][self.tf, self.nc]
        :type recalc: bool
        :param recalc: if True, call self.calc_filter after extending
        """

        self._xi_buf.extend(wfs)
        if recalc is True:
            self.calc_filter()

    def fill_xi_buf(self, wf, recalc=False):
        """fill all of the xi_buffer with wf

        :Parameters:
            wf : ndarrsay
                ndarray of shape (self.tf, self.nc)
            recalc : bool
                if True, call self.calc_filter after appending
        """

        self._xi_buf.fill(wf)
        if recalc is True:
            self.calc_filter()

    def reset_history(self):
        """sets the history to all zeros"""

        self._hist[:] = 0.0

    ## filter calculation

    def calc_filter(self):
        """calculate the filter with currently set parameters"""

        self._f = self.filter_calculation(self.xi, self._ce, self._chan_set)

    @classmethod
    def filter_calculation(cls, xi, ce, cs, *args, **kwargs):
        """ABSTRACT METHOD FOR FILTER CALCULATION

        Implement this in a meaningful way in any subclass. The method should
        return the filter given the multi-channeled template `xi`, the
        covariance estimator `ce` and the channel set `cs` plus any number
        of optional arguments and keywords. The filter usually has the same
        shape as the pattern `xi`.
        """

        raise NotImplementedError


class MatchedFilterNode(LinearFilterNode):
    """matched filters in the time domain optimise the signal to noise ratio
    (SNR) of the pattern with respect to a covariance matrix describing the
    noise background. Approximate deconvolution.

    If `normalise` is set to true the output is normalised s.t. the response
    of the pattern `xi` to the filter `f` is a peak of unit amplitude.

    """

    normalise = False

    @classmethod
    def filter_calculation(cls, xi, ce, cs, *args, **kwargs):
        tf, nc = xi.shape
        icmx = ce.get_icmx(tf=tf, chan_set=cs)
        f = sp.dot(mcvec_to_conc(xi), icmx)
        if cls.normalise is True:
            f /= sp.dot(mcvec_to_conc(xi), f)
        return sp.ascontiguousarray(mcvec_from_conc(f, nc=nc), dtype=sp.float32)


class RateEstimator(object):
    """moving average rate estimation for streaming spike trains"""

    ## special

    def __init__(self, *args, **kwargs):
        self._spike_count = deque()
        self._sample_count = deque()
        self._n_sample_max = int(kwargs.get("n_sample_max", 2500000))
        self._sample_rate = float(kwargs.get("sample_rate", 32000.0))
        self._full = False

    ## properties

    def get_sample_size(self):
        return sum(self._sample_count)

    sample_size = property(get_sample_size)

    ## methods

    def estimate(self):
        try:
            return self._sample_rate * sum(self._spike_count) / float(self.sample_size)
        except ZeroDivisionError:
            return 0.0

    def observation(self, nobs, tlen):
        self._spike_count.append(nobs)
        self._sample_count.append(tlen)

        while sum(self._sample_count) > self._n_sample_max:
            self._full = True
            self._spike_count.popleft()
            self._sample_count.popleft()

    def reset(self):
        self._spike_count.clear()
        self._sample_count.clear()
        self._full = False

    def is_full(self):
        return self._full

    full = property(is_full)


class REMF(MatchedFilterNode):
    """matched filter with rate estimation"""

    def __init__(self, *args, **kwargs):
        srate = kwargs.pop("sample_rate", 32000.0)
        nsample = kwargs.pop("n_sample_max", sp.inf)
        super(REMF, self).__init__(*args, **kwargs)
        self.rate = RateEstimator(srate, nsample)

## MAIN

if __name__ == "__main__":
    pass

## EOF