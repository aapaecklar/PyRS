# Reduction engine including slicing
import os
import random
from pyrs.utilities import checkdatatypes
from pyrs.core import workspaces
from pyrs.utilities import calibration_file_io
from pyrs.core import mask_util
from pyrs.core import reduce_hb2b_mtd
from pyrs.core import reduce_hb2b_pyrs
from pyrs.utilities import rs_project_file
from pyrs.core import instrument_geometry
from mantid.simpleapi import CreateWorkspace, LoadSpiceXML2DDet, Transpose, LoadEventNexus, ConvertToMatrixWorkspace

# TODO - FIXME - Issue #72 : Clean up


class HB2BReductionManager(object):
    """
    A data reduction manager of HB2B

    1. It can work with both PyHB2BReduction and MantidHB2BReduction seamlessly
    2. It can always compare the results between 2 reduction engines
    3. It shall provide an API to calibration optimization
    """
    def __init__(self):
        """ initialization
        """
        # # calibration manager
        # self._calibration_manager = calibration_file_io.CalibrationManager()
        # self._geometry_calibration = calibration_file_io.ResidualStressInstrumentCalibration()

        # workspace name or array vector
        self._curr_workspace = None
        self._curr_session_name = None
        self._session_dict = dict()  # ID = workspace, counts vector

        # Reduction engine
        self._last_reduction_engine = None

        # IDF
        self._mantid_idf = None

        # TODO - FUTURE - Whether a reduction engine can be re-used or stored???

        # (default) number of bins
        self._num_bins = 2500

        # masks
        self._loaded_mask_files = list()
        self._loaded_mask_dict = dict()

        # Outputs
        self._output_directory = None

        return

    @staticmethod
    def _generate_ws_name(file_name, is_nexus):
        ws_name = os.path.basename(file_name).split('.')[0]
        if is_nexus:
            # flag to show that there is no need to load instrument again
            ws_name = '{}__nexus'.format(ws_name)

        return ws_name

    def get_last_reduction_engine(self):
        """
        Get the reduction engine recently used
        :return:
        """
        return self._last_reduction_engine

    # TODO - TONIGHT 0 - Need to register reduced data with sub-run
    def get_reduced_diffraction_data(self, session_name, sub_run=None, mask_id=None):
        """ Get the reduce data
        :param session_name:
        :param sub_run:
        :param mask_id:
        :return:
        """
        workspace = self._session_dict[session_name]

        data_set = workspace.get_reduced_diffraction_data(sub_run, mask_id)

        return data_set

    def get_sub_runs(self, session_name):
        # TODO - TONIGHT - Doc and check
        return

    def get_sub_run_detector_counts(self, session_name, sub_run):
        # TODO - TONIGHT - Doc and check
        return

    def get_sub_run_2theta(self, exp_handler, sub_run):
        # TODO - TONIGHT - Doc and check
        return

    def get_sub_run_workspace(self, session_name):
        # TODO - TONIGHT - Doc and check
        # TODO - GOAL: Replace: get counts() and get 2theta()
        return

    def init_session(self, session_name):
        """
        Initialize a new session of reduction and thus to store data according to session name
        :return:
        """
        # Check inputs
        checkdatatypes.check_string_variable('Reduction session name', session_name)
        if session_name == '' or session_name in self._session_dict:
            raise RuntimeError('Session name {} is either empty or previously used (not unique)'.format(session_name))

        self._curr_workspace = workspaces.HidraWorkspace()
        self._curr_session_name = session_name
        self._session_dict[session_name] = self._curr_workspace

        return

    def load_hidra_project(self, project_file_name, load_calibrated_instrument):
        """
        load hidra project file
        :param project_file_name:
        :return:
        """
        # check inputs
        checkdatatypes.check_file_name(project_file_name, True, False, False, 'Project file to load')

        # Check
        if self._curr_workspace is None:
            raise RuntimeError('Call init_session to create a ReductionWorkspace')

        # PyRS HDF5
        project_h5_file = rs_project_file.HydraProjectFile(project_file_name,
                                                           mode=rs_project_file.HydraProjectFileMode.READWRITE)

        # Load
        self._curr_workspace.load_hidra_project(project_h5_file,
                                                load_raw_counts=True,
                                                load_reduced_diffraction=False)

        # Close
        project_h5_file.close()

        return

    def load_instrument_file(self, instrument_file_name):
        """
        Load instrument (setup) file to current "workspace"
        :param instrument_file_name:
        :return:
        """
        # Check
        if self._curr_workspace is None:
            raise RuntimeError('Call init_session to create a ReductionWorkspace')

        instrument = calibration_file_io.import_instrument_setup(instrument_file_name)
        self._curr_workspace.set_instrument(instrument)

        return

    def load_mask_file(self, mask_file_name):
        """ Load mask file to 1D array and auxiliary information
        :param mask_file_name:
        :return:
        """
        mask_vec, two_theta, note = mask_util.load_pyrs_mask(mask_file_name)

        # register the masks
        self._loaded_mask_files.append(mask_file_name)

        mask_id = os.path.basename(mask_file_name).split('.')[0] + '_{}'.format(hash(mask_file_name) % 100)
        self._loaded_mask_dict[mask_id] = mask_vec, two_theta, mask_file_name

        return two_theta, note, mask_id

    def get_loaded_mask_files(self):
        """
        Get the list of file names (full path) that have been loaded
        :return:
        """
        return self._loaded_mask_files[:]

    def get_mask_ids(self):
        """
        get IDs for loaded masks
        :return:
        """
        return sorted(self._loaded_mask_dict.keys())

    def get_mask_vector(self, mask_id):
        # TODO - Doc and check
        print ('L317 Mask dict: {}'.format(self._loaded_mask_dict.keys()))
        return self._loaded_mask_dict[mask_id][0]

    def set_geometry_calibration(self, geometry_calibration):
        """
        Load calibration file
        :param geometry_calibration:
        :return:
        """
        # TODO FIXME - NEXT - ???????
        checkdatatypes.check_type('Geometry calibration', geometry_calibration,
                                  calibration_file_io.ResidualStressInstrumentCalibration)
        self._geometry_calibration = geometry_calibration

        return

    def reduce_diffraction_data(self, session_name, apply_calibrated_geometry, bin_size_2theta, use_pyrs_engine, mask):
        """ Reduce ALL sub runs in a workspace from detector counts to diffraction data
        :param session_name:
        :param apply_calibrated_geometry: 3 options (1) user-provided AnglerCameraDetectorShift
                                          (2) True (use the one in workspace) (3) False (no calibration)
        :param bin_size_2theta:
        :param use_pyrs_engine:
        :param mask:  mask ID or mask vector
        :return:
        """
        # Get workspace
        if session_name is None:  # default as current session/workspace
            workspace = self._curr_workspace
        else:
            workspace = self._session_dict[session_name]

        # Process mask: No mask, Mask ID and mask vector
        if mask is None:
            mask_vec = None
            mask_id = None
        elif isinstance(mask, str):
            # mask ID
            mask_vec = self.get_mask_vector(mask)
            mask_id = mask
        else:
            checkdatatypes.check_numpy_arrays('Mask', [mask], dimension=1, check_same_shape=False)
            mask_vec = mask
            mask_id = 'Mask_{0:04}'.format(random.randint(1000))
        # END-IF-ELSE

        # Apply (or not) instrument geometry calibration shift
        if isinstance(apply_calibrated_geometry, instrument_geometry.AnglerCameraDetectorShift):
            det_pos_shift = apply_calibrated_geometry
        elif apply_calibrated_geometry:
            det_pos_shift = workspace.get_detector_shift()
        else:
            det_pos_shift = None
        # END-IF-ELSE
        print ('[DB...BAT] Det Position Shift: {}'.format(det_pos_shift))

        # TODO - TONIGHT NOW #72 - How to embed mask information???
        for sub_run in workspace.get_subruns():
            self.reduce_sub_run_diffraction(workspace, sub_run, det_pos_shift,
                                            use_mantid_engine=not use_pyrs_engine,
                                            mask_vec_id=(mask_id, mask_vec),
                                            resolution_2theta=bin_size_2theta)
        # END-FOR

        return

    # NOTE: Refer to compare_reduction_engines_tst
    def reduce_sub_run_diffraction(self, workspace, sub_run, geometry_calibration, use_mantid_engine,
                                   mask_vec_id,
                                   min_2theta=None, max_2theta=None, resolution_2theta=None):
        """
        Reduce import data (workspace or vector) to 2-theta ~ I
        Note: engine may not be reused because 2theta value may change among sub runs
        :param workspace:
        :param sub_run: integer for sub run number in workspace to reduce
        :param use_mantid_engine: Flag to use Mantid engine
        :param mask_vec_id: 2-tuple (String as ID, None or vector for Mask)
        :param geometry_calibration: instrument_geometry.AnglerCameraDetectorShift instance
        :param min_2theta: None or user specified
        :param max_2theta: None or user specified
        :param resolution_2theta: None or user specified
        :return:
        """
        # Get the raw data
        raw_count_vec = workspace.get_raw_data(sub_run)

        # process two theta
        two_theta = workspace.get_2theta(sub_run)
        print ('[INFO] User specified 2theta = {} is converted to Mantid 2theta = {}'
               ''.format(two_theta, -two_theta))
        two_theta = -two_theta

        # Set up reduction engine and also
        if use_mantid_engine:
            # Mantid reduction engine
            reduction_engine = reduce_hb2b_mtd.MantidHB2BReduction(self._mantid_idf)
            data_ws_name = reduction_engine.set_experimental_data(two_theta, raw_count_vec)
            reduction_engine.build_instrument(geometry_calibration)
        else:
            # PyRS reduction engine
            reduction_engine = reduce_hb2b_pyrs.PyHB2BReduction(workspace.get_instrument_setup())
            reduction_engine.set_experimental_data(two_theta, raw_count_vec)
            reduction_engine.build_instrument(geometry_calibration)

            # TODO FIXME - NEXT - START OF DEBUG OUTPUT -------->
            # Debug output: self._pixel_matrix
            # check corners
            # test 5 spots (corner and center): (0, 0), (0, 1023), (1023, 0), (1023, 1023), (512, 512)
            pixel_1d_array = reduction_engine.get_pixel_positions(False)
            pixel_number = 2048
            pixel_locations = [(0, 0),
                               (0, pixel_number - 1),
                               (pixel_number - 1, 0),
                               (pixel_number - 1, pixel_number - 1),
                               (pixel_number / 2, pixel_number / 2)]
            for index_i, index_j in pixel_locations:
                index1d = index_i + pixel_number * index_j
                pos_python = pixel_1d_array[index1d]
                print ('Pixel {}:  position = {}'.format(index1d, pos_python))
                for i in range(3):
                    print ('dir {}:  {:10f}'
                           ''.format(i, float(pos_python[i])))
                # END-FOR
            # END-FOR
            # TODO FIXME - NEXT - END OF DEBUG OUTPUT <------------
        # END-IF

        # Mask
        mask_id, mask_vec = mask_vec_id
        if mask_vec is not None:
            reduction_engine.set_mask(mask_vec)

        # Reduce
        # TODO - TONIGHT NOW #72 - Make this method call happy!
        num_bins = 500
        two_theta_range = (10, 60)
        two_theta_step = 50./500.
        data_set = reduction_engine.reduce_to_2theta_histogram(two_theta_range, two_theta_step,
                                                               apply_mask=True,
                                                               is_point_data=True,
                                                               normalize_pixel_bin=True,
                                                               use_mantid_histogram=False)

        bin_edges = data_set[0]
        hist = data_set[1]

        print ('[DB...BAT] vec X shape = {}, vec Y shape = {}'.format(bin_edges.shape, hist.shape))

        # record
        workspace.set_reduced_diffraction_data(sub_run, mask_id, bin_edges, hist)
        self._last_reduction_engine = reduction_engine

        return

    def save_reduced_diffraction(self, session_name, output_name):
        """
        Save the reduced diffraction data to file
        :param session_name:
        :param output_name:
        :return:
        """
        checkdatatypes.check_file_name(output_name, False, True, False, 'Output reduced file')

        workspace = self._session_dict[session_name]

        # Open
        if os.path.exists(output_name):
            io_mode = rs_project_file.HydraProjectFileMode.READWRITE
        else:
            io_mode = rs_project_file.HydraProjectFileMode.OVERWRITE
        project_file = rs_project_file.HydraProjectFile(output_name, io_mode)

        # Save
        workspace.save_reduced_diffraction_data(project_file)

        # Close
        project_file.save_hydra_project()

        return

    def set_mantid_idf(self, idf_name):
        """
        set the IDF file to reduction engine
        :param idf_name:
        :return:
        """
        checkdatatypes.check_file_name(idf_name, True, False, False, 'Mantid IDF file')
        if not idf_name.lower().endswith('.xml'):
            raise RuntimeError('Mantid IDF {} must end with .xml'.format(idf_name))

        self._mantid_idf = idf_name

        return

    def set_output_dir(self, output_dir):
        """
        set the directory for output data
        :param output_dir:
        :return:
        """
        # TODO - FIXME - check whether the output dir exist;

        self._output_directory = output_dir

        return

# END-CLASS-DEF