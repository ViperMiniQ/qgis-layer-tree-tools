# -*- coding: utf-8 -*-
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QFont


README_FILEPATH = os.path.join(os.path.dirname(__file__), 'README.md')
CHANGELOG_FILEPATH = os.path.join(os.path.dirname(__file__), 'CHANGELOG.md')


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'help_dialog.ui'))


class MDRender(QtWidgets.QMainWindow, FORM_CLASS):
    def __init__(self, filepath: str, title: str = '', parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.setWindowTitle(title)

        self.font = QFont("Courier", 10)

        self.pushButtonIncreaseFontSize.clicked.connect(self.increase_font_size)
        self.pushButtonDecreaseFontSize.clicked.connect(self.decrease_font_size)

        with open(filepath, 'r') as file:
            readme_text = file.read()

        self.textEditMD.setMarkdown(readme_text)
        self.textEditMD.setFont(self.font)

    def increase_font_size(self):
        self.font.setPointSize(self.font.pointSize() + 1)
        self.textEditMD.setFont(self.font)

    def decrease_font_size(self):
        self.font.setPointSize(self.font.pointSize() - 1)
        self.textEditMD.setFont(self.font)


class HelpDialog(MDRender):
    def __init__(self, parent=None):
        super().__init__(README_FILEPATH, "Layer Tree Tools: Help", parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect


class ChangeLogDialog(MDRender):
    def __init__(self, parent=None):
        super().__init__(CHANGELOG_FILEPATH, "Layer Tree Tools: Change log", parent)
