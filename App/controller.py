from .image_processor import ImageProcessor

class ImageController:
    def __init__(self):
        self.processor = ImageProcessor()

    def load_image(self, path):
        """Carga una imagen desde un archivo y la pasa al procesador."""
        return self.processor.read_image(path)

    def reset_image(self):
        """Restaura la imagen original sin modificaciones."""
        self.processor.reset()
        return self.processor.get_image()

    def get_processed_image(self):
        """Retorna la imagen actualmente modificada."""
        return self.processor.get_image()

    def adjust_brightness(self, value):
        """Ajusta el brillo general."""
        return self.processor.adjust_brightness(value)

    def adjust_channel(self, channel, value):
        """Ajusta un canal específico (0: R, 1: G, 2: B)."""
        return self.processor.adjust_channel_brightness(channel, value)

    def adjust_contrast(self, value, mode=0):
        """Aplica contraste por zonas oscuras o claras."""
        return self.processor.adjust_contrast(value, mode)

    def rotate(self, angle):
        """Rota usando PIL."""
        return self.processor.rotate(angle)

    def rotate_manual(self, angle):
        """Rota usando coordenadas (más costoso)."""
        return self.processor.rotate_manual(angle)

    def grayscale(self):
        """Convierte a escala de grises por promedio."""
        return self.processor.to_grayscale_average()

    def binarize(self, threshold=0.5):
        """Aplica binarización a blanco y negro."""
        return self.processor.binarize(threshold)

    def crop(self, x1, x2, y1, y2):
        """Recorta una región específica."""
        return self.processor.crop(x1, x2, y1, y2)

    def zoom_center(self, area_size=100, factor=5):
        """Zoom sobre el centro de la imagen."""
        return self.processor.zoom_center(area_size, factor)

    def fuse_with(self, other_image, alpha=0.5):
        """Funde la imagen cargada con otra."""
        return self.processor.fuse_images(other_image, alpha)

    def show_histogram(self):
        """Muestra el histograma RGB."""
        self.processor.show_histogram()

    def extract_rgb(self, channel):
        """Extrae un canal RGB (0: R, 1: G, 2: B)."""
        return self.processor.extract_rgb_channel(channel)

    def extract_cmy(self, channel):
        """Extrae un canal CMY (0: C, 1: M, 2: Y)."""
        return self.processor.extract_cmy_channel(channel)
