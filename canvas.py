from math import cos, sin


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
        self.transforms = []

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

