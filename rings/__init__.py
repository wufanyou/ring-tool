# Created by fw at 4/8/20

from .utils import *
import cv2

__all__ = ["RingDetector", "LogParameters"]


class LogParameters:
    def __init__(self, dict):
        # process pith is given
        self.x = None
        self.y = None
        self.angle = None
        self.radius = None

        self.has_pith = False
        self.has_angle = False
        self.has_radius = False

        if ("pithx" in dict) & ("pithy" in dict):
            try:
                self.x = float(dict["pithx"])
                self.y = float(dict["pithy"])
                self.has_pith = True
            except:
                self.has_pith = False

        if "angle" in dict:
            try:
                self.angle = float(dict["mark_angle"])
                self.has_angle = True
            except:
                self.has_angle = False

        if "radius" in dict:
            try:
                self.radius = float(dict["radius"])
                self.has_radius = True
            except:
                self.has_radius = False

        self.has_all = self.has_pith & self.has_angle & self.has_angle

    def __repr__(self):
        return f"x:{self.x}\ny:{self.y}\nangle:{self.angle}\nradius:{self.radius}\nall:{self.has_all}"


class RingDetector:
    def __init__(self, use_cache=True):
        self.image = None
        self.filename = None
        self.parameters = None
        self.is_strip = None

    # update input image given parameters
    def update(self, filename, parameters: dict, is_strip=False):

        self.parameters = LogParameters(parameters)
        self.image = cv2.imread(filename)
        self.is_strip = is_strip
        if not is_strip and not self.parameters.has_all:
            self.process_strip_parameter()

    # TODO  hardcore parameter configuration
    def process_strip_parameter(self):
        RESIZE_RATIO_FORM_EDGE_IMGS = 10
        CENTER_THRESHOLD = 20
        if ~self.parameters.has_all:
            edge_img = cv2.resize(
                self.image,
                tuple(
                    [
                        RESIZE_RATIO_FORM_EDGE_IMGS // 10
                        for x in self.image.shape[:2][::-1]
                    ]
                ),
            )
            edges = get_edges(edge_img)
            circles = get_hough_transform(edges)
            if self.parameters.has_pith:
                center = (self.parameters.x, self.parameters.y)
            else:
                center = get_pith(circles)
                center = tuple([RESIZE_RATIO_FORM_EDGE_IMGS * i for i in center])

            radius = get_radius(
                circles,
                center=center,
                img_size=edge_img.shape,
                center_threshold=CENTER_THRESHOLD,
            )
            radius = radius * RESIZE_RATIO_FORM_EDGE_IMGS
            if self.parameters.has_angle:
                angle = self.parameters.angle
            else:
                angle = find_chainsaw_marks_direction(self.image)
        else:
            center = (self.parameters.x, self.parameters.y)
            radius = self.parameters.radius
            angle = self.parameters.angle

        # update parameter for log image
        self.parameters.x = center[0]
        self.parameters.y = center[1]
        self.parameters.radius = radius
        self.parameters.angle = angle

    # crop image if necessary
    def crop_image(self, width):
        return crop_img(
            self.image,
            (self.parameters.x, self.parameters.y),
            self.parameters.radius,
            self.parameters.angle,
            width=width,
        )

    # TODO hardcore parameter configuration
    def __call__(self, width=20, ksize=31, window_len="auto", quantile=0.3):
        strip_img = self.image if self.is_strip else self.crop_image(width)
        strip_img = strip_img.swapaxes(0, 1) if strip_img.shape[0] > strip_img.shape[1] else strip_img
        array = smooth_array(strip_img, window_len=window_len, ksize=ksize)
        array = (array - np.min(array)) / (np.max(array) - np.min(array))
        peaks = find_peaks(array, quantile=quantile)
        diff = np.diff(peaks,prepend=0)
        return diff
