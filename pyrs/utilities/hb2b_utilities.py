# A module contains a set of static methods to provide instrument geometry and data archiving knowledge of HB2B
from . import checkdatatypes
from .convertdatatypes import to_int
import os


def get_hb2b_raw_data(ipts_number: int, run_number: int) -> str:
    """
    get the archived HB2B raw data
    :param ipts_number:
    :param run_number:
    :return:
    """
    # check inputs
    ipts_number = to_int('IPTS number', ipts_number, min_value=1)
    run_number = to_int('Run number', run_number, min_value=1)

    raw_exp_file_name = '/HFIR/HB2B/IPTS-{0}/datafiles/{1}.h5'.format(ipts_number, run_number)

    checkdatatypes.check_file_name(raw_exp_file_name, check_exist=True, check_writable=False, is_dir=False)

    return raw_exp_file_name


def get_hydra_project_file(ipts_number: int, run_number: int) -> str:
    """
    get the archived HB2B raw data
    :param ipts_number: IPTS number (int)
    :param run_number: Run number (int)
    :return:
    """
    # check inputs
    ipts_number = to_int('IPTS number', ipts_number, min_value=1)
    run_number = to_int('Run number', run_number, min_value=1)

    hydra_file_name = '/HFIR/HB2B/IPTS-{0}/shared/reduced_files/HB2B_{1}.hdf'.format(ipts_number, run_number)

    try:
        checkdatatypes.check_file_name(hydra_file_name, check_exist=True, check_writable=False, is_dir=False)
    except RuntimeError as run_error:
        print('[ERROR] Unable to find Hidra project file {} due to {}'.format(hydra_file_name, run_error))
        return ''

    return hydra_file_name


def is_calibration_dir(cal_sub_dir_name):
    """
    check whether the directory name is an allowed calibration directory name for HB2B
    :param cal_sub_dir_name:
    :return:
    """
    checkdatatypes.check_file_name(cal_sub_dir_name, check_exist=True, check_writable=False,
                                   is_dir=True, description='Directory for calibration files')

    dir_base_name = os.path.basename(cal_sub_dir_name)

    print('[TO BE IMPLEMENTED SOON] Not sure how to examine {} is a valid calibration dir.'.format(dir_base_name))

    # dir_base_name in hb2b_setup

    return False
