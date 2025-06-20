from PyQt6 import QtWidgets

from UI.MainForm import Ui_MainWindow



class MainFormOptions(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainFormOptions()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())