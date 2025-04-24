import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class ImageProcessor:

    @staticmethod
    def read_image(file_path):
        img = plt.imread(file_path).astype(np.float32)
        return img / 255.0 if img.max() > 1.0 else img

    @staticmethod
    def adjust_brightness(image, brightness):
        return np.clip(image + brightness, 0, 1)

    @staticmethod
    def adjust_channel_brightness(image, channel, value):
        adjusted = image.copy()
        adjusted[:, :, channel] = np.clip(adjusted[:, :, channel] + value, 0, 1)
        return adjusted

    @staticmethod
    def adjust_contrast(image, value, mode=0):
        if mode == 0:
            return np.clip(value * np.log10(1 + image), 0, 1)
        elif mode == 1:
            return np.clip(value * np.exp(image - 1), 0, 1)
        return image

    @staticmethod
    def rotate(image, angle):
        pil_img = Image.fromarray((image * 255).astype(np.uint8))
        rotated = pil_img.rotate(angle, expand=True)
        return np.array(rotated) / 255.0

    @staticmethod
    def rotate_manual(image, angle_degrees):
        gray = np.mean(image, axis=2) if image.ndim == 3 else image
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
        return np.stack([rotated]*3, axis=-1)

    @staticmethod
    def to_grayscale_average(image):
        gray = np.mean(image[:, :, :3], axis=2)
        return np.stack([gray]*3, axis=-1)

    @staticmethod
    def binarize(image, threshold=0.5):
        gray = np.mean(image, axis=2)
        binary = (gray >= threshold).astype(np.float32)
        return np.stack([binary]*3, axis=-1)

    @staticmethod
    def crop(image, x_start, x_end, y_start, y_end):
        return image[y_start:y_end, x_start:x_end]

    @staticmethod
    def zoom_center(image, area_size=100, factor=5):
        h, w = image.shape[:2]
        sr, er = h//2 - area_size//2, h//2 + area_size//2
        sc, ec = w//2 - area_size//2, w//2 + area_size//2
        region = image[sr:er, sc:ec]
        return np.clip(np.kron(region, np.ones((factor, factor, 1))), 0, 1)

    @staticmethod
    def fuse_images(image1, image2, factor):
        image2_resized = np.resize(image2, image1.shape)
        return np.clip(image1 * factor + image2_resized * (1 - factor), 0, 1)

    @staticmethod
    def show_histogram(image):
        img = (image * 255).astype(np.uint8) if image.max() <= 1.0 else image
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

    @staticmethod
    def extract_rgb_channel(image, channel):
        img = np.zeros_like(image)
        img[:, :, channel] = image[:, :, channel]
        return img

    @staticmethod
    def extract_cmy_channel(image, channel):
        cmy = 1.0 - image
        for i in range(3):
            if i != channel:
                cmy[:, :, i] = 1.0
        return cmy
