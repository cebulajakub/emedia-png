import cv2

from filters import low_pass_filter, plot_edges, hight_pass_filter, laplace_filter, quantize_image
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


#file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\vwboot.png"

def show_png(file_path):
    im = Image.open(file_path)
    im.show()


###########################33
def reconstruct_image(magnitude, phase):
    # zespolona
    spectrum_complex = magnitude * np.exp(1j * phase)

    # Odwrócenie
    inverse_spectrum = np.fft.ifft2(np.fft.ifftshift(spectrum_complex)).real

    # Przeskalowanie  pikseli [0, 255]
    inverse_spectrum *= 255

    return inverse_spectrum.astype(np.uint8)

#################################333

def furier_trans_pngg(file_path, cutoff_freq):
    # Wczytaj obraz
    img = plt.imread(file_path)
    imgcv = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    # Przekształć obraz do skali szarości
    if len(img.shape) == 2:
        img_gray = img

    else:
        # Przekształć obraz do skali szarości
        img_gray = np.mean(img, axis=-1)

    # Normalizuj obraz do przedziału [0, 1]
    #img_normalized = (img_gray - img_gray.min()) / (img_gray.max() - img_gray.min() + 1e-10)
    # Normalizuj obraz do przedziału [0, 255]
    img_normalized = (img_gray - img_gray.min()) * (255 / (img_gray.max() - img_gray.min()))

    # Oblicz transformatę Fouriera
    f = np.fft.fftshift(np.fft.fft2(img_normalized))

    low_pass = low_pass_filter(img_normalized, cutoff_freq, f)

    hight_pass = hight_pass_filter(img_normalized, cutoff_freq, f)

    laplace = laplace_filter(img_normalized)

    kwant = quantize_image(img_normalized, 2)




    amplitude = np.abs(f) + 1e-10

    phase = np.angle(f)
    hist, bins = np.histogram(img_gray.flatten(), bins=256, range=[0, 256])

    recovery = reconstruct_image(amplitude, phase)

    # Wyświetl obraz przefiltrowany
    plt.figure(figsize=(12, 12))

    plt.subplot(3, 3, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Color Image')

    plt.subplot(3, 3, 2)
    plt.imshow(img_gray, cmap='gray')
    plt.title('Grayscale Image')

    plt.subplot(3, 3, 3)
    plt.imshow(recovery)
    plt.title('Phaze + Amplitude')

    plt.subplot(3, 3, 4)
    edges = plot_edges(img_normalized)
    plt.imshow(edges, cmap='gray')
    plt.title('Edges')
    plt.colorbar()

    plt.subplot(3, 3, 5)
    plt.bar(bins[:-1], hist, width=np.diff(bins), color='blue', alpha=0.7)
    plt.title('Color Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')


    plt.subplot(3, 3, 6)
    spectrum_log = np.abs(f) + 1e-10
    plt.imshow(np.log(spectrum_log), cmap='gray')
    plt.title('Fourier Transform Spectrum')
    plt.colorbar()



    plt.subplot(3, 3, 7)
    plt.imshow(low_pass, cmap='gray')
    plt.title('Low pass Filtering')


    plt.subplot(3, 3, 8)
    plt.imshow(hight_pass, cmap='gray')
    plt.title('Hight pass Filtering')

    #plt.subplot(3, 3, 9)
    #plt.imshow(laplace, cmap='gray')
    #plt.title('Laplacian Filtering')

    plt.subplot(3, 3, 9)
    plt.imshow(kwant, cmap='gray')
    plt.title('Quant')


    plt.show()

    #######################################################
    
