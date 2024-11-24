import os
from PyQt5 import QtCore, QtWidgets, QtGui

class PlayListDialog(QtWidgets.QDialog):
    def __init__(self, data, title, parent=None):
        super().__init__(parent)  # Corrected call to super()
        self.data = data
        self.title = title

        self.setWindowTitle(f'{self.title}')
        self.setGeometry(500, 200, 500, 200)  # Corrected method name
        self.setMaximumSize(QtCore.QSize(500, 300))
        self.setMinimumSize(QtCore.QSize(500, 300))

        self.playlist_widget = QtWidgets.QListWidget(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.playlist_widget)

        if isinstance(data, list):
            for item in data:
                self.playlist_widget.addItem(os.path.basename(item))
        else:
            self.playlist_widget.addItem(data)

# Example usage:
# dialog = PlayListDialog(["Song 1", "Song 2"], "My Playlist")
# dialog.exec_()
