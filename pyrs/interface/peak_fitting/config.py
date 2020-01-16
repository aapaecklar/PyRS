from collections import OrderedDict

raw_dict = OrderedDict([('Sub-runs', 'subrun'),
                        ('sx', 'sx'), ('sy', 'sy'), ('sz', 'sz'),
                        ('vx', 'vx'), ('vy', 'vy'), ('vz', 'vz'),
                        ('phi', 'phi'), ('chi', 'chi'), ('omega', 'omega')])

fit_dict = OrderedDict([('Peak Height', 'PeakHeight'),
                        ('Full Width Half Max', 'FWHM'),
                        ('intensity', 'intensity'),
                        ('PeakCenter', 'PeakCenter'),
                        ('d-spacing', 'd-spacing'),
                        ('strain', 'strain')])

full_dict = OrderedDict([('Sub-runs', 'subrun'),
                         ('sx', 'sx'), ('sy', 'sy'), ('sz', 'sz'),
                         ('vx', 'vx'), ('vy', 'vy'), ('vz', 'vz'),
                         ('phi', 'phi'), ('chi', 'chi'), ('omega', 'omega'),
                         ('Peak Height', 'PeakHeight'),
                         ('Full Width Half Max', 'FWHM'), ('intensity', 'intensity'),
                         ('PeakCenter', 'PeakCenter'),
                         ('d-spacing', 'd-spacing'),
                         ('strain', 'strain')])

LIST_AXIS_TO_PLOT = {'raw': raw_dict,
                     'fit': fit_dict,
                     'full': full_dict,
                     }
DEFAUT_AXIS = {'1d': {'xaxis': 'Sub-runs',
                      'yaxis': 'sx'},
               '2d': {'xaxis': 'Sub-runs',
                      'yaxis': 'sx',
                      'zaxis': 'sy'}}

RAW_LIST_COLORS = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
