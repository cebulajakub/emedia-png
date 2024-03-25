from filters import low_pass_filter,plot_edges
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image




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

    # Przekształć obraz do skali szarości
    img_gray = np.mean(img, axis=-1)

    # Normalizuj obraz do przedziału [0, 1]
    img_normalized = (img_gray - img_gray.min()) / (img_gray.max() - img_gray.min() + 1e-10)

    # Oblicz transformatę Fouriera
    spectrum = np.fft.fftshift(np.fft.fft2(img_normalized))

    low_pass = low_pass_filter(img_gray, cutoff_freq, spectrum)
    amplitude = np.abs(spectrum) + 1e-10
    phase = np.angle(spectrum)
    recovery = reconstruct_image(amplitude, phase)

    # Wyświetl obraz przefiltrowany
    plt.figure(figsize=(12, 12))

    plt.subplot(3, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Color Image')

    plt.subplot(3, 2, 2)
    plt.imshow(img_gray, cmap='gray')
    plt.title('Grayscale Image')

    plt.subplot(3, 2, 3)
    spectrum_log = np.abs(spectrum) + 1e-10
    plt.imshow(np.log(spectrum_log), cmap='gray')
    plt.title('Fourier Transform Spectrum')
    plt.colorbar()

    plt.subplot(3, 2, 4)
    edges = plot_edges(img_normalized)
    plt.imshow(edges, cmap='gray')
    plt.title('Edges')
    plt.colorbar()



    plt.subplot(3, 2, 5)
    plt.imshow(low_pass, cmap='gray')
    plt.title('Low pass Filtering')

    plt.subplot(3, 2, 6)
    plt.imshow(recovery,cmap='inferno')
    plt.title('Recovery')

    plt.show()
    
    #######################################################
    
def furier_trans_png(file_path):
    # Wczytaj obraz
    img = plt.imread(file_path)

    # Przekształć obraz do skali szarości
    img_gray = np.mean(img, axis=-1)

    # Normalizuj obraz do przedziału [0, 1]
    img_normalized = (img_gray - img_gray.min()) / (img_gray.max() - img_gray.min() + 1e-10)
    # = (img - img.min()) / (img.max() - img.min() + 1e-10)

    # Oblicz transformatę Fouriera
    spectrum = np.fft.fftshift(np.fft.fft2(img_normalized))

    # Wyświetl widmo
    plt.figure(figsize=(12, 12))

    plt.subplot(3, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Color Image')

    plt.subplot(3, 2, 2)
    plt.imshow(img_gray, cmap='gray')
    plt.title('Grayscale Image')

    plt.subplot(3, 2, 3)
    spectrum_log = np.abs(spectrum) + 1e-10
    plt.imshow(np.log(spectrum_log), cmap='gray')#gray
    plt.title('Fourier Transform Spectrum')
    plt.colorbar()

    plt.subplot(3, 2, 4)
    edges = plot_edges(img_normalized)
    plt.imshow(edges, cmap='gray')
    plt.title('Edges')
    plt.colorbar()

    plt.subplot(3, 2, 5)
    spectrum_phase = np.angle(spectrum)
    plt.imshow(spectrum_phase, cmap='gray')
    plt.title('Fourier Transform Spectrum (Phases)')
    plt.colorbar()



    plt.show()