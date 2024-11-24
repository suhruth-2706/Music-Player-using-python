from main import ModernMusicPlayer
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)     
app.setStyle('fusion')
window = ModernMusicPlayer()
sys.exit(app.exec())