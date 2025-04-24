from .image_processor import ImageProcessor

class ImageController:
    def __init__(self):
        self.processor = ImageProcessor()
        self.original_image = None
        self.current_image = None
        self.preview_image = None

    def load_image(self, path):
        self.original_image = self.processor.read_image(path)
        self.current_image = self.original_image.copy()
        self.preview_image = self.current_image.copy()
        return self.current_image

    def reset_image(self):
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.preview_image = self.current_image.copy()
        return self.preview_image

    def apply_preview(self):
        if self.preview_image is not None:
            self.current_image = self.preview_image.copy()

    def discard_preview(self):
        if self.current_image is not None:
            self.preview_image = self.current_image.copy()

    def get_processed_image(self):
        return self.preview_image

    def preview_brightness(self, value):
        if self.current_image is not None:
            self.preview_image = self.processor.adjust_brightness(self.current_image.copy(), value)
        return self.preview_image

    def preview_channel(self, channel, value):
        if self.current_image is not None:
            self.preview_image = self.processor.adjust_channel_brightness(self.current_image.copy(), channel, value)
        return self.preview_image

    def preview_contrast(self, value, mode=0):
        if self.current_image is not None:
            self.preview_image = self.processor.adjust_contrast(self.current_image.copy(), value, mode)
        return self.preview_image

    def preview_rotate(self, angle):
        if self.current_image is not None:
            self.preview_image = self.processor.rotate(self.current_image.copy(), angle)
        return self.preview_image

    def preview_rotate_manual(self, angle):
        if self.current_image is not None:
            self.preview_image = self.processor.rotate_manual(self.current_image.copy(), angle)
        return self.preview_image

    def preview_grayscale(self):
        if self.current_image is not None:
            self.preview_image = self.processor.to_grayscale_average(self.current_image.copy())
        return self.preview_image

    def preview_binarize(self, threshold=0.5):
        if self.current_image is not None:
            self.preview_image = self.processor.binarize(self.current_image.copy(), threshold)
        return self.preview_image

    def preview_crop(self, x1, x2, y1, y2):
        if self.current_image is not None:
            self.preview_image = self.processor.crop(self.current_image.copy(), x1, x2, y1, y2)
        return self.preview_image

    def preview_zoom_center(self, area_size=100, factor=5):
        if self.current_image is not None:
            self.preview_image = self.processor.zoom_center(self.current_image.copy(), area_size, factor)
        return self.preview_image

    def preview_fuse_with(self, other_image, alpha=0.5):
        if self.current_image is not None:
            self.preview_image = self.processor.fuse_images(self.current_image.copy(), other_image, alpha)
        return self.preview_image

    def show_histogram(self):
        if self.preview_image is not None:
            self.processor.show_histogram(self.preview_image)

    def preview_extract_rgb(self, channel):
        if self.current_image is not None:
            self.preview_image = self.processor.extract_rgb_channel(self.current_image.copy(), channel)
        return self.preview_image

    def preview_extract_cmy(self, channel):
        if self.current_image is not None:
            self.preview_image = self.processor.extract_cmy_channel(self.current_image.copy(), channel)
        return self.preview_image
