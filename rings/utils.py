# Created by fw at 4/8/20
import cv2
from PIL import Image
import numpy as np
from ._diagonal_crop import *
from statsmodels.tsa.stattools import acf


def get_edges(img: np.array, scale=1,
              low_threshold=0.1, high_threshold=0.9,
              use_quantiles=False, sigma=1.0, kernel_size=(7, 7), ):
    img = cv2.resize(img, tuple([x // scale for x in img.shape[:2][::-1]]))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if use_quantiles:
        low_threshold = np.quantile(img, low_threshold)
        high_threshold = np.quantile(img, high_threshold)
    else:
        img_max = img.max()
        low_threshold = img_max * low_threshold
        high_threshold = img_max * high_threshold

    edges = cv2.Canny(cv2.GaussianBlur(img, kernel_size, sigma), low_threshold, high_threshold,
                      L2gradient=True, apertureSize=3, )
    return edges


def get_hough_transform(edges: np.array, scale=1, min_dist=1, acc_threshold=30):
    circles = cv2.HoughCircles(
        image=edges,
        method=cv2.HOUGH_GRADIENT,
        dp=scale,
        minDist=min_dist,
        param2=acc_threshold,
    )
    if len(circles) > 0:
        circles = circles[0]
        return circles
    else:
        raise Exception("Found no circles")
        # return None


def get_pith(circles: np.array):
    x, y, _ = circles.mean(0).astype(int)
    return x, y


def get_radius(circles: np.array, center=None, img_size=None, center_threshold=10):
    if center is None:
        center = get_pith(circles)

    if center_threshold is not None:
        if (img_size is not None) & 0 < center_threshold < 1:
            x = center[0] * center_threshold
            y = center[1] * center_threshold
            circles = circles[
                (abs(circles[:, 0] - center[0]) <= x)
                & (abs(circles[:, 1] - center[1]) <= y)
                ]
        else:
            circles = circles[
                (abs(circles[:, 0] - center[0]) <= center_threshold)
                & (abs(circles[:, 1] - center[1]) <= center_threshold)
                ]
    radius = circles.max(0)[1].astype(int)
    return radius


def crop_img(img: np.array, center, radius, angle, width=20):
    # in bgr format
    img = Image.fromarray(img)
    pil_center = (center[1], center[0])
    base = (pil_center[0] - width // 2, pil_center[1])
    img = crop(img, base, angle, width, radius)
    img = np.array(img)
    return img


# TODO  hardcore parameter configuration
def find_chainsaw_marks_direction(img: np.array):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]
    gray_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    edges = cv2.Canny(gray_img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angle = np.rad2deg(np.median(lines[:, 0, 1]))
    return angle


# hanning smooth function
def hanning_smooth(x, window_len):
    w = np.hanning(window_len)
    s = np.r_[x[window_len - 1: 0: -1], x, x[-2: -window_len - 1: -1]]
    y = np.convolve(w / w.sum(), s, mode="valid")
    return y


# compute the local maxium
def find_local_maximum(array: np.array):
    array = (np.diff(array, prepend=float("inf")) > 0) & (
            np.diff(array, append=float("inf")) < 0
    )
    array = np.where(array)[0]
    return array


def smooth_array(strip_img: np.array, window_len="auto", ksize=5):
    gray_img = cv2.cvtColor(strip_img, cv2.COLOR_BGR2HSV)[:, :, 2]
    gray_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # perform x sobel filter
    sobel_img = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=ksize)
    mean_sobel_array = sobel_img.mean(0)
    if window_len == "auto":
        window_len = acf(mean_sobel_array, nlags=len(mean_sobel_array), fft=False)
        window_len = find_local_maximum(window_len)
        if window_len is None:
            window_len = int(len(mean_sobel_array) // 50)
        else:
            window_len = window_len[0]
    hanning_smooth_array = hanning_smooth(mean_sobel_array, window_len=window_len)
    return hanning_smooth_array


def find_peaks(smoothed_array: np.array, quantile=0.1):
    local_maximum = find_local_maximum(smoothed_array)
    if len(local_maximum) > 0:
        quantile_height = np.quantile(smoothed_array[local_maximum], quantile)
        more_than_quantile = set(np.where(smoothed_array > quantile_height)[0])
        local_maximum = np.array(
            list(set(local_maximum).intersection(more_than_quantile))
        )
        local_maximum.sort()
        return local_maximum
    else:
        raise Exception("found on rings")
