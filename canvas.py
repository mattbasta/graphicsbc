from math import cos, sin

from PIL import Image, ImageColor, ImageDraw


class Transform(object):
    def get(self, x, y):
        return x, y


class TranslateTransform(Transform):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def get(self, x, y):
        return x + self.x, y + self.y


class RotateTransform(Transform):
    def __init__(self, theta):
        self.theta = theta

    def get(self, x, y):
        theta = self.theta
        return (x * cos(theta) - y * sin(theta),
                y * cos(theta) + x * sin(theta))


class ScaleTransform(Transform):
    def __init__(self, x_scale, y_scale):
        self.x, self.y = x_scale, y_scale

    def get(self, x, y):
        return x * self.x, y * self.y


class Canvas(object):

    def __init__(self):
        self.image = Image.new("RGBA", (500, 500))
        self.transforms = []
        self.draw = ImageDraw.Draw(self.image)
        self.color = ImageColor.getcolor("rgb(0, 0, 0)", mode="RGB")

        self.last_point = 0, 0
        self.cursor = 0, 0

    def set_color(self, r, g, b, mode="rgb"):
        self.color = ImageColor.getcolor("%s(%d, %d, %d)" % (mode, r, g, b),
                                         mode=mode.upper())

    def set_cursor(self, x, y):
        self.cursor = x, y

    def get_cursor(self, coords=None):
        pos = coords or self.cursor
        for t in self.transforms:
            pos = t.get(*pos)
        return pos

    def clear_transforms(self):
        self.transforms = []

    def pop(self):
        self.transforms.pop()

    def translate(self, x, y):
        self.transforms.append(TranslateTransform(x, y))

    def rotate(self, theta):
        self.transforms.append(RotateTransform(theta))

    def scale(self, x_scale, y_scale):
        self.transforms.append(ScaleTransform(x_scale, y_scale))

    def dot(self):
        cursor = self.get_cursor()
        self.draw.point(cursor, color=self.color)
        self.last_point = cursor

    def line(self):
        cursor = self.get_cursor()
        self.draw.point([self.last_point, cursor],
                        color=self.color)
        self.last_point = cursor

