import sys
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QFrame, QApplication, QLineEdit, QSlider
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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
            "Zonas Oscuras": lambda: self.preview_contrast(0.5, 0),
            "Zonas Claras": lambda: self.preview_contrast(0.5, 1),
            "Extraer RGB (Rojo)": lambda: self.preview_rgb(0),
            "Extraer CMY (Cian)": lambda: self.preview_cmy(0),
            "Blanco y Negro": self.preview_grayscale,
            "Negativo": self.preview_negative
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
        self.zoom_slider.valueChanged.connect(self.preview_zoom)

        left_layout.addWidget(QLabel("Zoom (zona central):"))
        left_layout.addWidget(self.zoom_slider)
        left_layout.addStretch()

        self.left_panel.setLayout(left_layout)

        # ----- Histograma embebido -----
        self.hist_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.hist_axes = self.hist_canvas.figure.subplots()
        left_layout.addWidget(QLabel("Histograma RGB:"))
        left_layout.addWidget(self.hist_canvas)


        # ----- Panel derecho -----
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(350)
        self.right_panel.setFrameShape(QFrame.Shape.StyledPanel)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)

        restore_button = QPushButton("Restaurar imagen")
        restore_button.clicked.connect(self.reset_image)
        right_layout.addWidget(restore_button)

        # Botón aplicar cambios
        apply_button = QPushButton("Guardar cambios")
        apply_button.clicked.connect(self.apply_changes)
        right_layout.addWidget(apply_button)

        # Botón descartar cambios
        discard_button = QPushButton("Descartar cambios")
        discard_button.clicked.connect(self.discard_changes)
        right_layout.addWidget(discard_button)

        # ----- Slider de Brillo -----
        brightness_label = QLabel("Brillo")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.preview_brightness)
        right_layout.addWidget(brightness_label)
        right_layout.addWidget(self.brightness_slider)

        # ----- Slider de Contraste (Zonas Oscuras) -----
        contrast_label = QLabel("Contraste (Z. Oscuras)")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(1)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(10)
        self.contrast_slider.valueChanged.connect(lambda: self.preview_contrast_slider(0))
        right_layout.addWidget(contrast_label)
        right_layout.addWidget(self.contrast_slider)

        # ----- Slider de Rotación -----
        rotate_label = QLabel("Rotación (°)")
        self.rotate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotate_slider.setMinimum(-180)
        self.rotate_slider.setMaximum(180)
        self.rotate_slider.setValue(0)
        self.rotate_slider.valueChanged.connect(self.preview_rotation)
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

    def update_histogram(self, image_np):
        if image_np is not None:
            img = (image_np * 255).astype(np.uint8) if image_np.max() <= 1.0 else image_np
            R, G, B = img[..., 0], img[..., 1], img[..., 2]

            self.hist_axes.clear()
            self.hist_axes.hist(R.ravel(), bins=256, color='red', alpha=0.5, label='Rojo')
            self.hist_axes.hist(G.ravel(), bins=256, color='green', alpha=0.5, label='Verde')
            self.hist_axes.hist(B.ravel(), bins=256, color='blue', alpha=0.5, label='Azul')
            self.hist_axes.set_title("Histograma RGB")
            self.hist_axes.set_xlabel("Intensidad")
            self.hist_axes.set_ylabel("Frecuencia")
            self.hist_axes.legend()
            self.hist_canvas.draw()

    def show_image(self, img_np):
        if img_np is not None:
            img_uint8 = (img_np * 255).astype(np.uint8)
            h, w, ch = img_uint8.shape
            bytes_per_line = ch * w
            qimg = QImage(img_uint8.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
            self.update_histogram(img_np)


    def preview_contrast(self, value, mode):
        img = self.controller.preview_contrast(value, mode)
        self.show_image(img)

    def preview_rgb(self, channel):
        img = self.controller.preview_extract_rgb(channel)
        self.show_image(img)

    def preview_cmy(self, channel):
        img = self.controller.preview_extract_cmy(channel)
        self.show_image(img)

    def preview_grayscale(self):
        img = self.controller.preview_grayscale()
        self.show_image(img)

    def preview_negative(self):
        img = self.controller.get_processed_image()
        if img is not None:
            img = 1.0 - img
            self.show_image(img)

    def preview_zoom(self):
        value = self.zoom_slider.value()
        img = self.controller.preview_zoom_center(area_size=100, factor=value)
        self.show_image(img)

    def preview_brightness(self):
        value = self.brightness_slider.value() / 100
        img = self.controller.preview_brightness(value)
        self.show_image(img)

    def preview_contrast_slider(self, mode=0):
        value = self.contrast_slider.value() / 100
        img = self.controller.preview_contrast(value, mode)
        self.show_image(img)

    def preview_rotation(self):
        angle = self.rotate_slider.value()
        img = self.controller.preview_rotate_manual(angle)
        self.show_image(img)

    def apply_changes(self):
        self.controller.apply_preview()
        self.show_image(self.controller.get_processed_image())

    def discard_changes(self):
        self.controller.discard_preview()
        self.show_image(self.controller.get_processed_image())

    def reset_image(self):
        img = self.controller.reset_image()
        self.show_image(img)