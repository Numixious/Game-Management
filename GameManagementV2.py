import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView
from PyQt5.QtGui import QPixmap
from qt_material import apply_stylesheet
import sys
import os


class GameManagementSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Management System")
        self.setGeometry(100, 100, 1920, 1080)

        # Database
        self.db_path = "games.db"
        self.games = self.load_data_from_db()

        # Layout
        self.layout = QVBoxLayout()
