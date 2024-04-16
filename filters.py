from scipy import ndimage
import numpy as np
import cv2
from scipy.ndimage import convolve


def low_pass_filter(img_gray, cutoff_freq, spectrum):
    # maska
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2
    mask = np.zeros((rows, cols), np.uint8)
    mask[crow - cutoff_freq:crow + cutoff_freq, ccol - cutoff_freq:ccol + cutoff_freq] = 1

    # filtracja
    filtered_spectrum = spectrum * mask

    # odwrotna
    filtered_img = np.fft.ifft2(np.fft.ifftshift(filtered_spectrum))
    return np.abs(filtered_img)


def hight_pass_filter(img_gray, cutoff_freq, spectrum):
    # maska
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2
    mask = np.ones((rows, cols), np.uint8)

    mask[crow - cutoff_freq:crow + cutoff_freq, ccol - cutoff_freq:ccol + cutoff_freq] = 0

    # filtracja
    filtered_spectrum = spectrum * mask

    # odwrotna
    filtered_img = np.fft.ifft2(np.fft.ifftshift(filtered_spectrum))
    return np.abs(filtered_img)


###############################################################
def plot_edges(gray_img_normalized):
    sobel_x = np.array([[1, 0, -1],
                        [2, 0, -2],
                        [1, 0, -1]])

    sobel_y = np.array([[1, 2, 1],
                        [0, 0, 0],
                        [-1, -2, -1]])

    edges_x = ndimage.convolve(gray_img_normalized, sobel_x)
    edges_y = ndimage.convolve(gray_img_normalized, sobel_y)
    edges = np.sqrt(edges_x ** 2 + edges_y ** 2)

    return edges


def laplace_filter(image):

    laplace_kernel = np.array([[0, -1, 0],
                               [-1, 4, -1],
                               [0, -1, 0]])

    filtered_image = ndimage.laplace(image)
    #lap = cv2.Laplacian(image, cv2.CV_64F, ksize=3)
    # filtered_img = np.real(np.fft.ifft2(np.fft.ifftshift(filtered_image)))
   # cv2.imshow("Laplacian", lap)
    #cv2.waitKey(0)


    # return filtered_img
    return filtered_image
    # return laplace_kernel
    #return lap


def quantize_image(image, levels):

    image_8bit = np.uint8(image)


    interval = 256 / levels
    quantized_image = np.floor_divide(image_8bit, interval)


    quantized_image = np.uint8(quantized_image * interval)

    return quantized_image
