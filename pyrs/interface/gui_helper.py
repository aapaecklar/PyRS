# a collection of helper methdos for GUI
import os
import platform
from pyrs.utilities import checkdatatypes
try:
    from PyQt5.QtWidgets import QDialog, QLineEdit, QFileDialog, QMessageBox
    is_qt4 = False
except ImportError:
    from PyQt4.QtGui import QDialog, QLineEdit, QFileDialog, QMessageBox
    from PyQt4 import QtCore
    is_qt4 = True


def browse_file(parent, caption, default_dir, file_filter, file_list=False, save_file=False):
    """ browse a file or files
    :param parent:
    :param caption:
    :param default_dir:
    :param file_filter:
    :param file_list:
    :param save_file:
    :return: if file_list is False: return string (file name); otherwise, return a list;
             if user cancels the operation, then return None
    """
    # check inputs
    assert isinstance(parent, object), 'Parent {} must be of some object.'.format(parent)
    checkdatatypes.check_string_variable('File browsing title/caption', caption)
    checkdatatypes.check_file_name(default_dir, check_exist=False, is_dir=True)
    checkdatatypes.check_bool_variable('Flag for browse a list of files to load', file_list)
    checkdatatypes.check_bool_variable('Flag to select loading or saving file', save_file)
    if file_filter is None:
        file_filter = 'All Files (*.*)'
    else:
        checkdatatypes.check_string_variable('File filter', file_filter)
        file_filter = '{};;All Files (*.*)'.format(file_filter)

    if save_file:
        # browse file name to save to
        if platform.system() == 'Darwin':
            # TODO - 20180721 - Find out the behavior on Mac!
            file_filter = ''
        save_set = QFileDialog.getSaveFileName(parent, caption=caption, directory=default_dir,
                                               filter=file_filter)
        if isinstance(save_set, tuple):
            # returned include both file name and filter
            file_name = str(save_set[0])
        else:
            file_name = str(save_set)

    elif file_list:
        # browse file names to load
        open_set = QFileDialog.getOpenFileNames(parent, caption, default_dir, file_filter)

        if isinstance(open_set, tuple):
            # PyQt5
            file_name_list = open_set[0]
        else:
            file_name_list = open_set

        if len(file_name_list) == 0:
            # use cancel
            return None
        else:
            return file_name_list

    else:
        # browse single file name
        open_set = QFileDialog.getOpenFileName(parent, caption, default_dir, file_filter)

        if isinstance(open_set, tuple):
            # PyQt5
            file_name = open_set[0]
        else:
            file_name = open_set

    # END-IF-ELSE

    # check result for single file whether user cancels operation
    if len(file_name) == 0:
        return None

    return file_name


def parse_float(float_str):
    """
    parse flaots from a string or a LineEdit
    :param float_str:
    :return:
    """
    if isinstance(float_str, QLineEdit):
        float_str = str(float_str.text())
    elif is_qt4 and isinstance(float_str, QtCore.QString):
        # There is no QString in PyQt5
        float_str = str(float_str)
    else:
        checkdatatypes.check_string_variable('Integer string', float_str)

    try:
        float_value = float(float_str)
    except ValueError as value_error:
        raise RuntimeError('Unable to parse {0} to integer due to {1}'.format(float_str, value_error))

    return float_value


def parse_integer(int_str):
    """
    parse integer from a string or a LineEdit
    :param int_str:
    :return:
    """
    if isinstance(int_str, QLineEdit):
        int_str = str(int_str.text())
    elif is_qt4 and isinstance(int_str, QtCore.QString):
        # There is no QString in PyQt5
        int_str = str(int_str)
    else:
        checkdatatypes.check_string_variable('Integer string', int_str)

    try:
        int_value = int(int_str)
    except ValueError as value_error:
        raise RuntimeError('Unable to parse {0} to integer due to {1}'.format(int_str, value_error))

    return int_value


def parse_integers(int_list_string):
    """ parse a list of integers.  Note that the start is inclusive and the end is exclusive
    example 1:4, 6:12, 8:12
    :param int_list_string:
    :return: list of int or range tuples
    """
    checkdatatypes.check_string_variable('Integer list (string)', int_list_string)

    # remove unnecessary spaces
    int_list_string = int_list_string.replace(' ', '')

    # split by ,
    int_range_list = int_list_string.split(',')

    # parse to integers
    int_list = list()
    try:
        for int_range in int_range_list:
            if int_range.isdigit():
                # is an integer
                int_list.append(int(int_range))
            elif int_range.count(':') == 1:
                # integer range:
                int_str_list = int_range.split(':')
                start_int = int(int_str_list[0])
                end_int = int(int_str_list[1])
                int_list.extend(range(start_int, end_int))
            else:
                raise ValueError('{0} is not recognized'.format(int_range))
    except ValueError as val_err:
        raise RuntimeError('Unable to parse integer list {0} due to {1}'.format(int_list_string, val_err))

    # remove additional integers
    int_list = list(set(int_list))

    int_list.sort()

    return int_list


def get_boolean_from_dialog(window_title, message):
    """
    pop out a dialog showing a message to user.  User will choose OK or Cancel
    :param window_title
    :param message:
    :return:
    """
    def msgbtn(i):
        # debugging output
        print "Button pressed is:", i.text()

    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Information)
    message_box.setText(message)
    if window_title is not None:
        message_box.setWindowTitle(window_title)
    message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    message_box.buttonClicked.connect(msgbtn)

    # get the message executed
    return_value = message_box.exec_()

    # identify output
    if return_value == 4194304:
        return_value = True
    elif return_value == 1024:
        return_value = False
    else:
        raise RuntimeError('Return value {} of type {} is not recognized.'
                           ''.format(return_value, type(return_value)))

    return return_value


def parse_tuples(tuple_str, data_type, size=None):
    """

    :param tuple_str:
    :param data_type:
    :param size:
    :return:
    """
    # TODO - 20180906 - Refine!
    items = tuple_str.strip().split(',')

    if size is not None:
        assert len(items) == size, '{} vs {}'.format(items, size)

    ret_list = list()
    for item in items:
        item = item.strip()
        item = data_type(item)
        ret_list.append(item)

    return ret_list


def pop_message(parent, message, detailed_message=None, message_type='error'):
    """ pop up a message with specified message type such as error, warning, info...
    :param parent:
    :param message:
    :param detailed_message: detailed message optionally shown to user
    :param message_type: str as ['error', 'warning', 'info'] but NOT case sensitive
    :return:
    """
    message_type = message_type.lower()
    if message_type not in ['error', 'warning', 'info']:
        raise TypeError('Message type {0} is not supported.'.format(message_type))

    # check types
    checkdatatypes.check_string_variable('(Main) message to show', message)
    if detailed_message is not None:
        checkdatatypes.check_string_variable('(Detailed) message to show', detailed_message)

    # create a QMessageBox
    msg_box = QMessageBox()

    # set information type
    if message_type == 'info':
        msg_box.setIcon(QMessageBox.Information)
    elif message_type == 'error':
        msg_box.setIcon(QMessageBox.Critical)
    elif message_type == 'warning':
        msg_box.setIcon(QMessageBox.Warning)

    # set text
    msg_box.setText(message)
    if detailed_message is not None:
        msg_box.setDetailedText(detailed_message)  # another button
    msg_box.setWindowTitle('PyRS Message')

    # box
    msg_box.setStandardButtons(QMessageBox.Ok)

    ret_val = msg_box.exec_()

    return
