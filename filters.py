from scipy import ndimage
import numpy as np


def low_pass_filter(img_gray,cutoff_freq,spectrum):
    #maska
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2
    mask = np.zeros((rows, cols), np.uint8)
    mask[crow - cutoff_freq:crow + cutoff_freq, ccol - cutoff_freq:ccol + cutoff_freq] = 1

    #filtracja
    filtered_spectrum = spectrum * mask

    # odwrotna
    filtered_img = np.fft.ifft2(np.fft.ifftshift(filtered_spectrum)).real
    return filtered_img

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
    edges = np.sqrt(edges_x**2 + edges_y**2)

    return edges