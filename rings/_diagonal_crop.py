# Created by fw at 4/15/20
# modify from https://github.com/jobevers/diagonal-crop

import collections
import numpy as np

__all__ = ["crop"]

_Point = collections.namedtuple("Point", ["x", "y"])


class Point(_Point):
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def recenter(self, old_center, new_center):
        return self + (new_center - old_center)

    def rotate(self, center, angle):
        # angle should be in radians
        x = (
            np.cos(angle) * (self.x - center.x)
            - np.sin(angle) * (self.y - center.y)
            + center.x
        )
        y = (
            np.sin(angle) * (self.x - center.x)
            + np.cos(angle) * (self.y - center.y)
            + center.y
        )
        return Point(x, y)


Bound = collections.namedtuple("Bound", ("left", "upper", "right", "lower"))


def get_center(im):
    return Point(*(d / 2 for d in im.size))


def get_bounds(points):
    xs, ys = zip(*points)
    # left, upper, right, lower using the usual image coordinate system
    # where top-left of the image is 0, 0
    return Bound(min(xs), min(ys), max(xs), max(ys))


def get_bounds_center(bounds):
    return Point(
        (bounds.right - bounds.left) / 2 + bounds.left,
        (bounds.lower - bounds.upper) / 2 + bounds.upper,
    )


def round_int(values):
    return tuple(int(round(v)) for v in values)


def get_rotated_rectangle_points(angle, base_point, height, width):
    # base_point is the upper left (ul)
    ur = Point(width * np.cos(angle), -width * np.sin(angle))
    lr = Point(ur.x + height * np.sin(angle), ur.y + height * np.cos(angle))
    ll = Point(height * np.cos(np.pi / 2 - angle), height * np.sin(np.pi / 2 - angle))
    return tuple(base_point + pt for pt in (Point(0, 0), ur, lr, ll))


def crop(im: np.array, base, angle, height, width):
    base = Point(*base)
    points = get_rotated_rectangle_points(angle, base, height, width)
    return crop_with_points(im, angle, points)


def crop_with_points(im, angle, points):
    bounds = get_bounds(points)
    im2 = im.crop(round_int(bounds))
    bound_center = get_bounds_center(bounds)
    crop_center = get_center(im2)
    # in the cropped image, this is where our points are
    crop_points = [pt.recenter(bound_center, crop_center) for pt in points]
    # this is where the rotated points would end up without expansion
    rotated_points = [pt.rotate(crop_center, angle) for pt in crop_points]
    # expand is necessary so that we don't lose any part of the picture
    im3 = im2.rotate(-angle * 180 / np.pi, expand=True)
    # but, since the image has been expanded, we need to recenter
    im3_center = get_center(im3)
    rotated_expanded_points = [
        pt.recenter(crop_center, im3_center) for pt in rotated_points
    ]
    im4 = im3.crop(round_int(get_bounds(rotated_expanded_points)))
    return im4
