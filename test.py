from PyQt6 import QtWidgets
import pyqtgraph.opengl as gl
import sys

class GLViewExample(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GLViewWidget Example with PyQt6')
        self.resize(800, 600)

        # Создаем GLViewWidget
        self.glview = gl.GLViewWidget()
        self.glview.opts['distance'] = 40  # дистанция камеры

        # Добавим координатные оси
        axis = gl.GLAxisItem()
        self.glview.addItem(axis)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.glview)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GLViewExample()
    window.show()
    sys.exit(app.exec())