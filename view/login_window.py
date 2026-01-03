# view/login_window.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from constants import MASTER_STYLESHEET

class LoginWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Simulador de Examen - Inicio de Sesión")
        self.setMinimumSize(400, 600)
        self.setStyleSheet(MASTER_STYLESHEET)

        # --- Creación de Widgets ---
        self.title_label = QLabel("Bienvenido")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.username_label = QLabel("Usuario:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario")

        self.password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Iniciar Sesión")
        self.register_button = QPushButton("Registrarse")

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)

        # --- Layout (Organización) ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.password_label)
        main_layout.addWidget(self.password_input)
        main_layout.addStretch(1)
        main_layout.addWidget(self.error_label)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    # --- Métodos para el Controlador ---
    def get_credentials(self) -> tuple[str, str]:
        return self.username_input.text(), self.password_input.text()

    def show_error(self, message: str):
        self.error_label.setText(message)

    def show_success_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())