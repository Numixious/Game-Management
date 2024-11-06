import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView
from PyQt5.QtGui import QPixmap
from qt_material import apply_stylesheet
import sys


class GameManagementSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Management System")
        self.setGeometry(100, 100, 800, 600)

        # Initialize database and load data
        self.db_path = "games.db"
        self.init_db()
        self.games = self.load_data_from_db()

        # Layouts
        self.layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search by game name...")
        self.search_bar.textChanged.connect(self.search_games)
        self.layout.addWidget(self.search_bar)

        # Input Fields
        self.input_fields_layout = QHBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Game Name")
        self.input_fields_layout.addWidget(self.name_input)

        self.release_date_input = QLineEdit(self)
        self.release_date_input.setPlaceholderText("Release Date (YYYY-MM-DD)")
        self.input_fields_layout.addWidget(self.release_date_input)

        self.metacritic_score_input = QLineEdit(self)
        self.metacritic_score_input.setPlaceholderText("Metacritic Score")
        self.input_fields_layout.addWidget(self.metacritic_score_input)

        self.category_input = QComboBox(self)
        self.category_input.addItems(["Action", "Horror", "Sci-Fi"])
        self.input_fields_layout.addWidget(self.category_input)

        self.image_button = QPushButton("Select Image", self)
        self.image_button.clicked.connect(self.select_image)
        self.input_fields_layout.addWidget(self.image_button)

        self.image_label = QLabel("No Image Selected", self)
        self.input_fields_layout.addWidget(self.image_label)

        self.layout.addLayout(self.input_fields_layout)

        # Buttons
        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Game", self)
        self.add_button.clicked.connect(self.add_game)
        self.buttons_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected Game", self)
        self.remove_button.clicked.connect(self.remove_game)
        self.buttons_layout.addWidget(self.remove_button)

        self.layout.addLayout(self.buttons_layout)

        # Table to Display Games
        # 5 columns to include image column
        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(
            ["Image", "Name", "Release Date", "Metacritic Score", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)  # Stretch columns to fit
        self.layout.addWidget(self.table)

        # Set cells to be editable
        self.table.itemChanged.connect(self.edit_game_in_db)

        self.setLayout(self.layout)
        self.selected_image_path = None  # Store selected image path

        # Load data into the table
        self.populate_table()

    def init_db(self):
        """Initialize the SQLite database."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS games (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            release_date TEXT,
                            metacritic_score INTEGER,
                            category TEXT,
                            image_path TEXT)''')
        connection.commit()
        connection.close()

    def load_data_from_db(self):
        """Load games from the database into a list."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, name, release_date, metacritic_score, category, image_path FROM games")
        games = cursor.fetchall()
        connection.close()
        return games

    def populate_table(self, games=None):
        """Populate the table with data from the database."""
        self.table.setRowCount(0)  # Clear the table first
        games = games if games else self.games  # Use filtered games if provided
        for game in games:
            game_id, name, release_date, metacritic_score, category, image_path = game
            self.add_game_to_table(
                game_id, name, release_date, metacritic_score, category, image_path)

    def add_game_to_table(self, game_id, name, release_date, metacritic_score, category, image_path):
        """Add a single game entry to the table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Add image as a QLabel in the first column
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        # Scale image to fit cell
        image_label.setPixmap(pixmap.scaled(100, 100))
        self.table.setCellWidget(row, 0, image_label)

        # Add other data in columns
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(release_date))
        self.table.setItem(row, 3, QTableWidgetItem(str(metacritic_score)))
        self.table.setItem(row, 4, QTableWidgetItem(category))

        # Store game ID as item data to keep track of each row
        self.table.item(row, 1).setData(1000, game_id)

    def select_image(self):
        """Select an image for the game."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Game Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_name:
            self.selected_image_path = file_name
            pixmap = QPixmap(file_name).scaled(
                100, 100)  # Scale image for preview
            self.image_label.setPixmap(pixmap)

    def add_game(self):
        """Add a new game to the table and database."""
        name = self.name_input.text()
        release_date = self.release_date_input.text()
        metacritic_score = self.metacritic_score_input.text()
        category = self.category_input.currentText()

        if name and release_date and metacritic_score.isnumeric() and self.selected_image_path:
            metacritic_score = int(metacritic_score)
            game_id = self.add_game_to_db(
                name, release_date, metacritic_score, category, self.selected_image_path)
            self.add_game_to_table(
                game_id, name, release_date, metacritic_score, category, self.selected_image_path)

            # Reset input fields
            self.name_input.clear()
            self.release_date_input.clear()
            self.metacritic_score_input.clear()
            self.image_label.clear()
            self.image_label.setText("No Image Selected")
            self.selected_image_path = None
        else:
            QMessageBox.warning(
                self, "Input Error", "Please fill all fields correctly and select an image.")

    def add_game_to_db(self, name, release_date, metacritic_score, category, image_path):
        """Add a new game entry to the database."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO games (name, release_date, metacritic_score, category, image_path) VALUES (?, ?, ?, ?, ?)",
                       (name, release_date, metacritic_score, category, image_path))
        connection.commit()
        game_id = cursor.lastrowid
        connection.close()
        return game_id

    def remove_game(self):
        """Remove the selected game from the table and database."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            game_id = self.table.item(selected_row, 1).data(1000)
            self.delete_game_from_db(game_id)
            self.table.removeRow(selected_row)
        else:
            QMessageBox.warning(self, "Selection Error",
                                "Please select a game to remove.")

    def delete_game_from_db(self, game_id):
        """Remove a game entry from the database by ID."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        connection.commit()
        connection.close()

    def edit_game_in_db(self, item):
        """Update the database when a cell is edited."""
        row = item.row()
        game_id = self.table.item(row, 1).data(1000)
        column = item.column()

        # Get updated value based on the column
        if column == 1:  # Name
            field, value = "name", item.text()
        elif column == 2:  # Release Date
            field, value = "release_date", item.text()
        elif column == 3:  # Metacritic Score
            field, value = "metacritic_score", int(item.text())
        elif column == 4:  # Category
            field, value = "category", item.text()
        else:
            return  # Skip if it's not an editable field

            # Update database
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE games SET {field} = ? WHERE id = ?", (value, game_id))
        connection.commit()
        connection.close()

    def search_games(self):
        """Filter games in the table based on the search bar input."""
        search_text = self.search_bar.text().lower()
        filtered_games = [
            game for game in self.games if search_text in game[1].lower()]
        self.populate_table(filtered_games)

    def closeEvent(self, event):
        """Override close event to confirm exit."""
        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")  # Apply Material theme
    window = GameManagementSystem()
    window.show()
    sys.exit(app.exec_())
