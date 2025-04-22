import sys
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QFrame, QApplication, QLineEdit, QSlider
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import numpy as np
from App.controller import ImageController

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visor de Imágenes")
        self.setGeometry(100, 100, 1400, 600)

        self.controller = ImageController()
        self.image_path = ""

        self.init_ui()

    def init_ui(self):
        # ----- Header -----
        self.header = QFrame()
        self.header.setFixedHeight(80)
        self.header.setFrameShape(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Visor de Imágenes")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Ruta de la imagen...")
        self.path_input.setReadOnly(True)

        self.browse_button = QPushButton("Explorar")
        self.browse_button.clicked.connect(self.browse_image)

        self.load_button = QPushButton("Cargar")
        self.load_button.clicked.connect(self.load_from_path)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.path_input)
        header_layout.addWidget(self.browse_button)
        header_layout.addWidget(self.load_button)
        self.header.setLayout(header_layout)

        # ----- Panel izquierdo -----
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(350)
        self.left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        buttons = {
            "Zonas Oscuras": lambda: self.apply_contrast(0.5, 0),
            "Zonas Claras": lambda: self.apply_contrast(0.5, 1),
            "Extraer RGB (Rojo)": lambda: self.apply_rgb(0),
            "Extraer CMY (Cian)": lambda: self.apply_cmy(0),
            "Blanco y Negro": self.apply_grayscale,
            "Negativo": self.apply_negative
        }

        for label, action in buttons.items():
            btn = QPushButton(label)
            btn.clicked.connect(action)
            left_layout.addWidget(btn)

        # ----- Zoom slider -----
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.setValue(5)
        self.zoom_slider.setTickInterval(1)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.apply_zoom)

        left_layout.addWidget(QLabel("Zoom (zona central):"))
        left_layout.addWidget(self.zoom_slider)
        left_layout.addStretch()

        self.left_panel.setLayout(left_layout)

        # ----- Panel derecho -----
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(350)
        self.right_panel.setFrameShape(QFrame.Shape.StyledPanel)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)

        # ----- Slider de Brillo -----
        brightness_label = QLabel("Brillo")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.apply_brightness)
        right_layout.addWidget(brightness_label)
        right_layout.addWidget(self.brightness_slider)

        # ----- Slider de Contraste (Zonas Oscuras) -----
        contrast_label = QLabel("Contraste (Z. Oscuras)")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(1)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(10)
        self.contrast_slider.valueChanged.connect(lambda: self.apply_contrast_slider(0))
        right_layout.addWidget(contrast_label)
        right_layout.addWidget(self.contrast_slider)

        # ----- Slider de Rotación -----
        rotate_label = QLabel("Rotación (°)")
        self.rotate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotate_slider.setMinimum(-180)
        self.rotate_slider.setMaximum(180)
        self.rotate_slider.setValue(0)
        self.rotate_slider.valueChanged.connect(self.apply_rotation)
        right_layout.addWidget(rotate_label)
        right_layout.addWidget(self.rotate_slider)

        right_layout.addStretch()
        self.right_panel.setLayout(right_layout)


        # ----- Área central (imagen) -----
        self.image_label = QLabel("Aquí se mostrará la imagen")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setMinimumSize(400, 400)

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.image_label)

        # ----- Layout horizontal (izq - centro - der) -----
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.left_panel)
        middle_layout.addLayout(center_layout)
        middle_layout.addWidget(self.right_panel)

        # ----- Layout principal -----
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header)
        main_layout.addLayout(middle_layout)

        self.setLayout(main_layout)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.path_input.setText(file_path)

    def load_from_path(self):
        path = self.path_input.text()
        if path:
            img = self.controller.load_image(path)
            self.show_image(img)

    def show_image(self, img_np):
        if img_np is not None:
            img_uint8 = (img_np * 255).astype(np.uint8)
            h, w, ch = img_uint8.shape
            bytes_per_line = ch * w
            qimg = QImage(img_uint8.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

    def apply_contrast(self, value, mode):
        img = self.controller.adjust_contrast(value, mode)
        self.show_image(img)

    def apply_rgb(self, channel):
        img = self.controller.extract_rgb(channel)
        self.show_image(img)

    def apply_cmy(self, channel):
        img = self.controller.extract_cmy(channel)
        self.show_image(img)

    def apply_grayscale(self):
        img = self.controller.grayscale()
        self.show_image(img)

    def apply_negative(self):
        img = self.controller.get_processed_image()
        if img is not None:
            img = 1.0 - img
            self.show_image(img)

    def apply_zoom(self):
        value = self.zoom_slider.value()
        img = self.controller.zoom_center(area_size=100, factor=value)
        self.show_image(img)
        
    def apply_brightness(self):
        value = self.brightness_slider.value() / 100  # escala [-1.0, 1.0]
        img = self.controller.adjust_brightness(value)
        self.show_image(img)

    def apply_contrast_slider(self, mode=0):
        value = self.contrast_slider.value() / 100  # escala [0, 1]
        img = self.controller.adjust_contrast(value, mode)
        self.show_image(img)

    def apply_rotation(self):
        angle = self.rotate_slider.value()
        img = self.controller.rotate_manual(angle)
        self.show_image(img)
