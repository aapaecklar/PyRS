#!/usr/bin/python
# In order to test the core methods for peak fitting and thus strain/stress calculation
import os
from pyrs.core import pyrscore
import sys
import pyrs.core

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PyQt4.QtGui import QApplication

# default testing directory is ..../PyRS/
print (os.getcwd())
# therefore it is not too hard to locate testing data
test_data = 'tests/testdata/BD_Data_Log.hdf5'
print ('Data file {0} exists? : {1}'.format(test_data, os.path.exists(test_data)))


def create_test_data(rs_core, src_data_set, target_data_set):
    """
    fit peaks and output to h5 data sets as the input of strain/stress
    :param rs_core
    :param src_data_set: 
    :param target_data_set: 
    :return: 
    """
    for direction in ['e11', 'e22', 'e33']:
        # load
        src_h5_file = src_data_set[direction]
        data_key, message = rs_core.load_rs_raw(src_h5_file)
        print ('Load {}: {}'.format(src_h5_file, message))
        # fit
        rs_core.fit_peaks(data_key, None, 'Gaussian', 'Linear', [80, 90])
        # save
        target_h5_file = target_data_set[direction]
        rs_core.save_peak_fit_result(data_key, src_h5_file, target_h5_file)
    # END-FOR

    return


def test_strain_calculation():
    """
    main testing body to test the workflow to calculate strain
    :return:
    """
    # initialize core
    rs_core = pyrscore.PyRsCore()

    # import data file: detector ID and file name
    test_data_set = {'e11': 'tests/testdata/LD_Data_Log.hdf5',
                     'e22': 'tests/testdata/BD_Data_Log.hdf5',
                     'e33': 'tests/testdata/ND_Data_Log.hdf5'}

    # create testing files, aka, testing peak fitting module (core)
    target_data_set = {'e11': 'tests/temp/LD_Data_Log.hdf5',
                       'e22': 'tests/temp/BD_Data_Log.hdf5',
                       'e33': 'tests/temp/ND_Data_Log.hdf5'}
    create_test_data(rs_core, test_data_set, target_data_set)

    # start a session
    rs_core.new_strain_stress_session('test strain/stress module', is_plane_strain=False,
                                      is_plane_stress=False)

    # load data
    rs_core.strain_stress_calculator.load_raw_file(file_name=target_data_set['e11'], direction='e11')
    rs_core.strain_stress_calculator.load_raw_file(file_name=target_data_set['e22'], direction='e22')
    rs_core.strain_stress_calculator.load_raw_file(file_name=target_data_set['e33'], direction='e33')

    # check and align measurement points around
    try:
        rs_core.strain_stress_calculator.align_measuring_points(pos_x='vx', pos_y='vy', pos_z='vz')
    except RuntimeError as run_err:
        print ('Measuring points are not aligned: {}'.format(run_err))

    # peak fitting for detector - ALL
    for direction in ['e11', 'e22', 'e33']:
        assert rs_core.strain_stress_calculator.are_peaks_fitted(direction=direction),\
            'Peaks must be fitted as a pre-requisite'

    rs_core.calculate_strain(data_key)

    # export
    rs_core.export_to_paraview(data_key, 'strain', '/tmp/stain_para.dat')

    return


if __name__ == '__main__':
    """ main
    """
    test_strain_calculation()
