import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, 
    QApplication, QSpacerItem, QSizePolicy, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from constants import MASTER_STYLESHEET

class MainMenuWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Simulador de Examen - Menú Principal")

        self.setMinimumSize(400, 600)
        self.setStyleSheet(MASTER_STYLESHEET)

        # --- Creación de Widgets ---
        self.title_label = QLabel("Menú Principal")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.welcome_label = QLabel("Bienvenido, [Usuario]")
        self.welcome_label.setObjectName("usernameLabel")
        self.welcome_label.setAlignment(Qt.AlignCenter)

        # --- Grupo de Exámenes ---
        self.exam_group = QGroupBox("Selecciona un modo")
        exam_layout = QVBoxLayout(self.exam_group)
        exam_layout.setSpacing(10)

        self.practice_button = QPushButton("Simulador de Práctica")
        self.practice_attempts_label = QLabel("Intentos restantes: 5/5")
        self.practice_attempts_label.setAlignment(Qt.AlignCenter)

        self.final_button = QPushButton("Examen Final de Ubicación")
        self.final_attempts_label = QLabel("Intentos restantes: 2/2")
        self.final_attempts_label.setAlignment(Qt.AlignCenter)
        
        exam_layout.addWidget(self.practice_button)
        exam_layout.addWidget(self.practice_attempts_label)
        exam_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        exam_layout.addWidget(self.final_button)
        exam_layout.addWidget(self.final_attempts_label)

        self.dashboard_button = QPushButton("Ver Mi Progreso (Dashboard)")

        # --- Otros Widgets ---
        self.logout_button = QPushButton("Cerrar Sesión")
        self.logout_button.setObjectName("logoutButton")
        
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)

        # --- Layout (Organización) ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(15)
        
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.welcome_label)
        main_layout.addWidget(self.exam_group)
        main_layout.addWidget(self.dashboard_button)
        main_layout.addStretch()
        main_layout.addWidget(self.error_label)
        main_layout.addWidget(self.logout_button)
        
        self.setLayout(main_layout)

    # --- Métodos para el Controlador ---
    def update_info(self, username: str, counts: dict):
        self.welcome_label.setText(f"Bienvenido, {username}")
        
        practice_rem = counts.get('practice_remaining', 0)
        self.practice_attempts_label.setText(f"Intentos restantes: {practice_rem}/5")
        self.practice_button.setEnabled(practice_rem > 0)

        final_rem = counts.get('final_remaining', 0)
        self.final_attempts_label.setText(f"Intentos restantes: {final_rem}/2")
        self.final_button.setEnabled(final_rem > 0)
        
        self.show_error("")

    def show_error(self, message: str):
        self.error_label.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenuWindow()
    test_counts = {'practice_remaining': 3, 'final_remaining': 0}
    window.update_info("UsuarioDePrueba", test_counts)
    window.show()
    sys.exit(app.exec_())