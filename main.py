import sys

from PyQt6 import QtWidgets
from MVC.Controller import Controller
from MVC.Model import Model
from MVC.View import View

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    model = Model()
    view = View()
    main_form  = QtWidgets.QMainWindow()
    view.setupUi(main_form)
    controller = Controller(model, view)

    controller.show()
    sys.exit(app.exec())