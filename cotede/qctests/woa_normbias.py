# -*- coding: utf-8 -*-

"""


    Create a test to check if cfg['vars'] does exist in the climatology file,
      to avoid error like have t_mn in one and t_an in the other.

    An idea to improve the climatology test. Gridpoints estimated from few
      measurements should be less trustable. Here I'm using a threshold of at
      least 3 samples to be considered. Deep ocean is in general quite
      stable, so few measurements should be sufficient. One possibility is to
      estimate the standard error, which depends on the ammount of samples and
      estimated standard deviation. This would be the 'uncertainty on the
      estimated average climatology. Any measurement in that range would be
      considered statistically identical to the climatology. Above that
      difference, it would be normalized by the standard deviation. Therefore,
      stable areas would be less tolerant to variability, even with few samples.
"""

from datetime import timedelta

import numpy as np
from numpy import ma

from oceansdb import WOA

FLAG_GOOD = 1
FLAG_BAD = 3

def woa_normbias(data, v, cfg):
    """

        FIXME: Move this procedure into a class to conform with the new system
          and include a limit in minimum ammount of samples to trust it. For
          example, consider as masked all climatologic values estimated from
          less than 5 samples.
    """

    # 3 is the possible minimum to estimate the std, but I shold use higher.
    min_samples = 3
    woa = None

    if ('LATITUDE' in data.keys()) and ('LONGITUDE' in data.keys()):
        if 'datetime' in data.keys():
            d = data['datetime']
        elif ('datetime' in data.attributes):
            d0 = data.attributes['datetime']
            if ('timeS' in data.keys()):
                d = [d0 + timedelta(seconds=s) for s in data['timeS']]
            else:
                d = [data.attributes['datetime']]*len(data['LATITUDE']),

        #woa = woa_track_from_file(
        #        d,
        #        data['LATITUDE'],
        #        data['LONGITUDE'],
        #        cfg['file'],
        #        varnames=cfg['vars'])
        db = WOA()
        if v not in db.keys():
            vtype = v[:-1]
        else:
            vtype = v

        print("Sorry, I'm temporary not ready to handle tracks.")
        #woa = db[vtype].get_track(var=['mn', 'sd'],
        #        doy=d,
        #        depth=[0],
        #        lat=data['LATITUDE'],
        #        lon=data['LONGITUDE'])

    elif ('LATITUDE' in data.attributes.keys()) and \
            ('LONGITUDE' in data.attributes.keys()) and \
            ('PRES' in data.keys()):
                db = WOA()
                if v not in db.keys():
                    vtype = v[:-1]
                else:
                    vtype = v

                woa = db[vtype].extract(
                        var=['mn', 'sd', 'dd'],
                        doy=int(data.attributes['datetime'].strftime('%j')),
                        depth=data['PRES'],
                        lat=data.attributes['LATITUDE'],
                        lon=data.attributes['LONGITUDE'])

    flag = np.zeros(data[v].shape, dtype='i1')
    features = {}

    try:
        woa_bias = data[v] - woa['mn']
        woa_normbias = woa_bias/woa['sd']

        ind = np.nonzero((woa['dd'] >= min_samples) &
                (np.absolute(woa_normbias) <= cfg['sigma_threshold']))
        flag[ind] = 1   # cfg['flag_good']
        ind = np.nonzero((woa['dd'] >= min_samples) &
                (np.absolute(woa_normbias) > cfg['sigma_threshold']))
        flag[ind] = 3   # cfg['flag_bad']

        # Flag as 9 any masked input value
        flag[ma.getmaskarray(data[v])] = 9

        features = {'woa_bias': woa_bias, 'woa_normbias': woa_normbias,
                'woa_std': woa['sd'], 'woa_nsamples': woa['dd'],
                'woa_mean': woa['mn']}

    finally:
        # self.logger.warn("%s - WOA is not available at this site" %
        # self.name)
        return flag, features


class WOA_NormBias(object):
    def __init__(self, data, varname, cfg):
        self.data = data
        self.varname = varname
        self.cfg = cfg

        # Default is to do not use standard error to estimate the bias,
        #   because that is the traditional approach.
        if 'use_standard_error' not in self.cfg:
            self.cfg['use_standard_error'] = False

        self.set_features()

    def keys(self):
        return self.features.keys() + \
                ["flag_%s" % f for f in self.flags.keys()]

    def set_features(self):

        if ('LATITUDE' in self.data.keys()) and \
                ('LONGITUDE' in self.data.keys()):
                    assert False, "I'm not ready for that"

        elif ('LATITUDE' in self.data.attributes.keys()) and \
                ('LONGITUDE' in self.data.attributes.keys()):
                    lat = self.data.attributes['LATITUDE']
                    lon = self.data.attributes['LONGITUDE']

        if ('PRES' in self.data.keys()):
            pres = self.data['PRES']

        doy = int(self.data.attributes['datetime'].strftime('%j'))

        db = WOA()
        if self.varname not in db.keys():
            vtype = self.varname[:-1]
        else:
            vtype = self.varname

        woa = db[vtype].extract(
                var=['mn', 'sd', 'dd'],
                doy=doy,
                depth=pres,
                lat=lat,
                lon=lon)

        self.features = {
                'woa_mean': woa['mn'],
                'woa_std': woa['sd'],
                'woa_nsamples': woa['dd']}

        self.features['woa_bias'] = self.data[self.varname] - \
                self.features['woa_mean']

        # if use_standard_error = True, the comparison with the climatology
        #   considers the standard error, i.e. the bias will be only the
        #   ammount above the standard error range.
        if self.cfg['use_standard_error'] is True:
            standard_error = self.features['woa_std'] / \
                    self.features['woa_nsamples'] ** 0.5
            idx = np.absolute(self.features['woa_bias']) <= \
                    standard_error
            self.features['woa_bias'][idx] = 0
            idx = np.absolute(self.features['woa_bias']) > standard_error
            self.features['woa_bias'][idx] -= \
                    np.sign(self.features['woa_bias'][idx]) * \
                    standard_error[idx]

        self.features['woa_normbias'] = self.features['woa_bias'] / \
                self.features['woa_std']

    def test(self):

        # 3 is the possible minimum to estimate the std, but I shold use higher.
        try:
            min_samples = self.cfg['min_samples']
        except:
            min_samples = 3

        self.flags = {}

        try:
            flag_good = self.cfg['flag_good']
        except:
            flag_good = FLAG_GOOD
        try:
            flag_bad = self.cfg['flag_bad']
        except:
            flag_bad = FLAG_BAD

        threshold = self.cfg['threshold']
        assert (np.size(threshold) == 1) and \
                (threshold is not None)

        flag = np.zeros(self.data[self.varname].shape, dtype='i1')

        normbias_abs = np.absolute(self.features['woa_normbias'])
        ind = np.nonzero((self.features['woa_nsamples'] >= min_samples) &
                (normbias_abs <= threshold))
        flag[ind] = flag_good
        ind = np.nonzero((self.features['woa_nsamples'] >= min_samples) &
                (normbias_abs > threshold))
        flag[ind] = flag_bad

        # Flag as 9 any masked input value
        flag[ma.getmaskarray(self.data[self.varname])] = 9

        self.flags['woa_normbias'] = flag
