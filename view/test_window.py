# view/test_window.py

import sys
import os
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QApplication, QRadioButton, 
    QButtonGroup, QFrame, QSpacerItem, QSizePolicy, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from model import Question 
from constants import MASTER_STYLESHEET

class TestWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.current_question: Question | None = None
        self.remaining_time = 60
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Simulador de Examen - En Progreso")
        self.setFixedSize(650, 700)
        self.setStyleSheet(MASTER_STYLESHEET)

        # --- Creación de Widgets ---
        self.question_number_label = QLabel("Pregunta 1/40")
        self.question_number_label.setObjectName("questionNumberLabel")
        
        self.timer_label = QLabel("Tiempo: 60")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignRight)

        self.question_text_label = QLabel("Cargando pregunta...")
        self.question_text_label.setObjectName("questionTextLabel")
        self.question_text_label.setWordWrap(True)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(540, 250) 
        self.image_label.hide() 

        self.options_frame = QFrame()
        self.options_frame.setObjectName("optionsFrame")
        self.options_layout = QVBoxLayout(self.options_frame)
        
        self.button_group = QButtonGroup(self)
        self.options_radio_buttons = []
        for i in range(4):
            radio = QRadioButton(f"Opción {i+1}")
            self.options_radio_buttons.append(radio)
            self.button_group.addButton(radio)
            self.options_layout.addWidget(radio)
            
        self.next_button = QPushButton("Siguiente Pregunta")
        self.next_button.setEnabled(False)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.button_group.buttonToggled.connect(self.on_option_selected)

        # --- Layout (Organización) ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 25)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.question_number_label)
        header_layout.addStretch()
        header_layout.addWidget(self.timer_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
        main_layout.addWidget(self.question_text_label)
        main_layout.addWidget(self.image_label, 0, Qt.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
        main_layout.addWidget(self.options_frame)
        main_layout.addStretch()
        main_layout.addWidget(self.next_button)
        
        self.setLayout(main_layout)

    def on_option_selected(self, button, checked):
        if checked:
            self.next_button.setEnabled(True)

    def update_timer(self):
        self.remaining_time -= 1
        self.timer_label.setText(f"Tiempo: {self.remaining_time}")
        if self.remaining_time <= 0:
            self.timer.stop()
            self.next_button.clicked.emit() 

    def start_timer(self):
        self.remaining_time = 60
        self.timer_label.setText(f"Tiempo: {self.remaining_time}")
        self.timer.start(1000)

    def stop_timer(self):
        self.timer.stop()

    def display_question(self, question: Question, number: int, total: int):
        self.current_question = question
        self.question_number_label.setText(f"Pregunta {number}/{total}")
        self.question_text_label.setText(question.text)

        if question.image_path:
            image_full_path = f"images/{question.image_path}"
            if os.path.exists(image_full_path):
                pixmap = QPixmap(image_full_path)
                self.image_label.setPixmap(pixmap)
                self.image_label.show()
            else:
                self.image_label.hide()
                self.image_label.clear()
        else:
            self.image_label.hide()
            self.image_label.clear()

        self.button_group.setExclusive(False)
        for radio in self.options_radio_buttons:
            radio.setChecked(False)
        self.button_group.setExclusive(True)

        shuffled_options = list(question.options)
        random.shuffle(shuffled_options)

        for i, radio_button in enumerate(self.options_radio_buttons):
            if i < len(shuffled_options):
                option = shuffled_options[i]
                radio_button.setText(option.text)
                self.button_group.setId(radio_button, option.id)
                radio_button.show()
            else:
                radio_button.hide() 

        self.start_timer()
        self.next_button.setEnabled(False)

    def get_selected_option_id(self) -> int | None:
        checked_id = self.button_group.checkedId()
        return checked_id if checked_id != -1 else None

    def get_time_taken(self) -> int:
        return 60 - self.remaining_time