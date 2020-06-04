from pyrs.interface.manual_reduction import manualreductionwindow
from qtpy import QtCore
import os
import pytest

wait = 100


def test_manual_reduction(qtbot, tmpdir):
    window = manualreductionwindow.ManualReductionWindow(None)
    qtbot.addWidget(window)
    window.show()
    qtbot.wait(wait)

    assert window.isVisible()

    # set data
    qtbot.keyClicks(window.ui.lineEdit_runNumber, "data/HB2B_938.nxs.h5")
    qtbot.wait(wait)

    # set mask
    qtbot.mouseClick(window.ui.checkBox_defaultMaskFile, QtCore.Qt.LeftButton)
    qtbot.wait(wait)
    for _ in range(100):
        qtbot.keyClick(window.ui.lineEdit_maskFile, QtCore.Qt.Key_Backspace)
    qtbot.wait(wait)
    qtbot.keyClicks(window.ui.lineEdit_maskFile, "data/HB2B_Mask_12-18-19.xml")
    qtbot.wait(wait)

    # set calibration
    qtbot.mouseClick(window.ui.checkBox_defaultCalibrationFile, QtCore.Qt.LeftButton)
    qtbot.wait(wait)
    for _ in range(100):
        qtbot.keyClick(window.ui.lineEdit_calibrationFile, QtCore.Qt.Key_Backspace)
    qtbot.wait(wait)
    qtbot.keyClicks(window.ui.lineEdit_calibrationFile, "data/HB2B_CAL_Si333.json")
    qtbot.wait(wait)

    # set vanadium
    qtbot.keyClicks(window.ui.lineEdit_vanRunNumber, "data/HB2B_1118.nxs.h5")
    qtbot.wait(wait)

    # set output directory
    qtbot.keyClicks(window.ui.lineEdit_outputDirectory, str(tmpdir))
    qtbot.wait(wait)

    # push button to run manual reduction
    qtbot.mouseClick(window.ui.pushButton_splitConvertSaveProject, QtCore.Qt.LeftButton)
    qtbot.wait(wait)

    assert window.ui.progressBar.value() == 100

    # check that the output file was made
    # should actaully check the contents, not just that it exist
    assert os.path.isfile(tmpdir.join("HB2B_938.h5"))

    # plot the detector view
    qtbot.mouseClick(window.ui.pushButton_plotDetView,  QtCore.Qt.LeftButton)
    qtbot.wait(wait)

    # change to Reduced Data view, I don't know how to do that with clicking
    window.ui.tabWidget_View.setCurrentIndex(1)
    qtbot.wait(wait)
    # plot the reduction data
    qtbot.mouseClick(window.ui.pushButton_plotDetView,  QtCore.Qt.LeftButton)
    qtbot.wait(wait)

    # get the data from the plot canvas and check the data limits and label
    line = window.ui.graphicsView_1DPlot.canvas().get_axis(0, 0, True).lines[0]
    assert line.get_label() == 'sub-run: 1, 2theta = 90.00050354003906'
    assert line.get_xdata().min() == pytest.approx(81.88955539289697)
    assert line.get_xdata().max() == pytest.approx(98.07327399000138)
    # first data point is a nan so exclude it
    assert line.get_ydata()[1::].min() == pytest.approx(46.154437570576924)
    assert line.get_ydata()[1::].max() == pytest.approx(473.8784126395234)