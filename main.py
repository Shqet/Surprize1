import sys

from PyQt6 import QtWidgets
from PyQt6 import QtGui

from MVC.Controller import Controller
from MVC.Model import Model
from MVC.View import View

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon("Resources/Pictures/surprize_icon.ico")
    app.setWindowIcon(icon)

    model = Model()
    view = View()
    main_form  = QtWidgets.QMainWindow()
    view.setupUi(main_form)
    view.setup_icon(icon)
    controller = Controller(model, view)

    controller.show()
    sys.exit(app.exec())