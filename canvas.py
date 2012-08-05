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

    def update(self, x, y):
        self.x += x
        self.y += y


class RotateTransform(Transform):
    def __init__(self, theta):
        self.theta = theta

    def get(self, x, y):
        theta = self.theta
        return (x * cos(theta) - y * sin(theta),
                y * cos(theta) + x * sin(theta))

    def update(self, theta):
        self.theta += theta


class ScaleTransform(Transform):
    def __init__(self, x_scale, y_scale):
        self.x, self.y = x_scale, y_scale

    def get(self, x, y):
        return x * self.x, y * self.y

    def update(self, x, y):
        self.x += x
        self.y += y


class Canvas(object):

    def __init__(self):
        self.image = Image.new("RGBA", (500, 500))
        self.transforms = []
        self.draw = ImageDraw.Draw(self.image)
        self.color = ImageColor.getcolor("rgb(0, 0, 0)", mode="RGB")

        self.last_point = 0, 0
        self.cursor = 0, 0

    def set_color(self, r, g, b, a=255, mode="rgb"):
        rgba = r, g, b
        rgba = map(str, rgba)
        self.color = ImageColor.getcolor("%s(%s)" % (mode, ", ".join(rgba)),
                                         mode=mode.upper())
        #print "Color:", self.color

    def set_cursor(self, x, y):
        self.cursor = x, y
        #print "Moved cursor to", self.cursor

    def get_cursor(self, coords=None):
        pos = 0, 0
        for t in self.transforms:
            pos = t.get(*pos)
        cur_pos = coords or self.cursor
        return pos[0] + cur_pos[0], pos[1] + cur_pos[0]

    def clear_transforms(self):
        self.transforms = []

    def pop(self):
        self.transforms.pop()

    def translate(self, x, y):
        if self.transforms and isinstance(self.transforms[-1],
                                          TranslateTransform):
            self.transforms[-1].update(x, y)
            return
        self.transforms.append(TranslateTransform(x, y))

    def rotate(self, theta):
        if self.transforms and isinstance(self.transforms[-1], RotateTransform):
            self.transforms[-1].update(theta)
            return
        self.transforms.append(RotateTransform(theta))

    def scale(self, x_scale, y_scale):
        if self.transforms and isinstance(self.transforms[-1], ScaleTransform):
            self.transforms[-1].update(x_scale, y_scale)
            return
        self.transforms.append(ScaleTransform(x_scale, y_scale))

    def dot(self):
        cursor = self.get_cursor()
        self.draw.point(cursor, fill=self.color)
        self.last_point = cursor

    def line(self):
        cursor = self.get_cursor()
        self.draw.line([self.last_point, cursor],
                       fill=self.color)
        self.last_point = cursor

    def save(self, path):
        self.image.save(path)

