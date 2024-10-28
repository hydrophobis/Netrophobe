from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt5.QtGui import QFont

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        
        layout = QVBoxLayout()

        # Example: Add a font size setting
        self.font_size_input = QLineEdit(self)
        self.font_size_input.setPlaceholderText("Enter font size")
        layout.addWidget(QLabel("Font Size:"))
        layout.addWidget(self.font_size_input)

        # Add a button to save settings
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        # Save settings logic (e.g., update font size)
        font_size = int(self.font_size_input.text())
        font = QFont("Arial", font_size)
        QApplication.setFont(font)
        self.accept()  # Close the dialog