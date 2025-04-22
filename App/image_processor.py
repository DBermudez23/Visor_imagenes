import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.modified_image = None

    def read_image(self, file_path):
        """Lee la imagen desde disco y normaliza su escala a [0, 1]."""
        img = plt.imread(file_path).astype(np.float32)
        if img.max() > 1.0:
            img = img / 255.0
        self.original_image = img
        self.modified_image = img.copy()
        return self.modified_image

    def reset(self):
        """Restaura la imagen modificada a la original."""
        if self.original_image is not None:
            self.modified_image = self.original_image.copy()

    def get_image(self):
        """Devuelve una copia de la imagen modificada actual."""
        return self.modified_image.copy() if self.modified_image is not None else None

    def adjust_brightness(self, brightness):
        if self.modified_image is not None:
            self.modified_image = np.clip(self.modified_image + brightness, 0, 1)
        return self.modified_image

    def adjust_channel_brightness(self, channel, value):
        if self.modified_image is not None:
            adjusted = self.modified_image.copy()
            adjusted[:, :, channel] = np.clip(adjusted[:, :, channel] + value, 0, 1)
            self.modified_image = adjusted
        return self.modified_image

    def adjust_contrast(self, value, mode=0):
        if self.modified_image is not None:
            if mode == 0:
                self.modified_image = np.clip(value * np.log10(1 + self.modified_image), 0, 1)
            elif mode == 1:
                self.modified_image = np.clip(value * np.exp(self.modified_image - 1), 0, 1)
        return self.modified_image

    def rotate(self, angle):
        """Rota usando PIL para evitar dependencia de scipy."""
        if self.modified_image is not None:
            pil_img = Image.fromarray((self.modified_image * 255).astype(np.uint8))
            rotated = pil_img.rotate(angle, expand=True)
            self.modified_image = np.array(rotated) / 255.0
        return self.modified_image

    def rotate_manual(self, angle_degrees):
        if self.modified_image is None:
            return None
        gray = np.mean(self.modified_image, axis=2) if self.modified_image.ndim == 3 else self.modified_image
        ang = np.radians(angle_degrees)
        m, n = gray.shape
        cos_ang, sin_ang = np.cos(ang), np.sin(ang)
        c = int(round(m * sin_ang + n * cos_ang))
        d = int(round(m * cos_ang + n * sin_ang))
        rotated = np.zeros((c, d))
        for i in range(c):
            for j in range(d):
                ii = int((i - c / 2) * cos_ang + (j - d / 2) * sin_ang + m / 2)
                jj = int(-(i - c / 2) * sin_ang + (j - d / 2) * cos_ang + n / 2)
                if 0 <= ii < m and 0 <= jj < n:
                    rotated[i, j] = gray[ii, jj]
        self.modified_image = np.stack([rotated]*3, axis=-1)
        return self.modified_image

    def to_grayscale_average(self):
        if self.modified_image is not None:
            gray = np.mean(self.modified_image[:, :, :3], axis=2)
            self.modified_image = np.stack([gray]*3, axis=-1)
        return self.modified_image

    def binarize(self, threshold=0.5):
        if self.modified_image is not None:
            gray = np.mean(self.modified_image, axis=2)
            binary = (gray >= threshold).astype(np.float32)
            self.modified_image = np.stack([binary]*3, axis=-1)
        return self.modified_image

    def crop(self, x_start, x_end, y_start, y_end):
        if self.modified_image is not None:
            self.modified_image = self.modified_image[y_start:y_end, x_start:x_end]
        return self.modified_image

    def zoom_center(self, area_size=100, factor=5):
        if self.modified_image is None:
            return None
        h, w = self.modified_image.shape[:2]
        sr, er = h//2 - area_size//2, h//2 + area_size//2
        sc, ec = w//2 - area_size//2, w//2 + area_size//2
        region = self.modified_image[sr:er, sc:ec]
        zoomed = np.kron(region, np.ones((factor, factor, 1)))
        self.modified_image = np.clip(zoomed, 0, 1)
        return self.modified_image

    def fuse_images(self, image2, factor):
        if self.modified_image is None:
            return None
        image2_resized = np.resize(image2, self.modified_image.shape)
        self.modified_image = np.clip(self.modified_image * factor + image2_resized * (1 - factor), 0, 1)
        return self.modified_image

    def show_histogram(self):
        if self.modified_image is None:
            return
        img = (self.modified_image * 255).astype(np.uint8) if self.modified_image.max() <= 1.0 else self.modified_image
        R, G, B = img[..., 0], img[..., 1], img[..., 2]
        plt.figure(figsize=(10, 6))
        for i, (channel, color, name) in enumerate(zip([R, G, B], ['red', 'green', 'blue'], ['Rojo', 'Verde', 'Azul'])):
            plt.subplot(3, 1, i+1)
            plt.hist(channel.ravel(), bins=256, color=color, alpha=0.7)
            plt.title(f'Histograma del canal {name}')
            plt.xlabel('Intensidad')
            plt.ylabel('Frecuencia')
        plt.tight_layout()
        plt.show()

    def extract_rgb_channel(self, channel):
        if self.modified_image is None:
            return None
        img = np.zeros_like(self.modified_image)
        img[:, :, channel] = self.modified_image[:, :, channel]
        self.modified_image = img
        return self.modified_image

    def extract_cmy_channel(self, channel):
        if self.modified_image is None:
            return None
        cmy = 1.0 - self.modified_image
        for i in range(3):
            if i != channel:
                cmy[:, :, i] = 1.0
        self.modified_image = cmy
        return self.modified_image
