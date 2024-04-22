import cv2
import matplotlib

from filters import low_pass_filter, plot_edges, hight_pass_filter, laplace_filter, quantize_image
import matplotlib.pyplot as plt
matplotlib.use('TkAgg') or matplotlib.use('Qt5Agg')

import numpy as np
from PIL import Image
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

import mpl_toolkits.mplot3d




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
    if len(img.shape) == 2:
        img_gray = img
        #img_normalized = (img_gray - img_gray.min()) / (img_gray.max() - img_gray.min() + 1e-10)
    else:
        # Przekształć obraz do skali szarości
        img_gray = np.mean(img, axis=-1)

    # Normalizuj obraz do przedziału [0, 1]
    #img_normalized = (img_gray - img_gray.min()) / (img_gray.max() - img_gray.min() + 1e-10)
    # Normalizuj obraz do przedziału [0, 255]
    img_normalized = (img_gray - img_gray.min()) * (255 / (img_gray.max() - img_gray.min()))

    # Oblicz transformatę Fouriera
    f = np.fft.fftshift(np.fft.fft2(img_normalized))


    ff = np.fft.fftshift(np.fft.fft2(img))
    if len(img.shape) == 2:
        img_res = np.fft.ifft2(np.fft.ifftshift(f))
    else:
        img_res = np.fft.ifft2(np.fft.ifftshift(ff))

    low_pass = low_pass_filter(img_normalized, cutoff_freq, f)

    hight_pass = hight_pass_filter(img_normalized, cutoff_freq, f)

    laplace = laplace_filter(img_normalized)

    kwant = quantize_image(img_normalized, 2)

    im = cv2.imread(file_path)

    vals = im.mean(axis=2).flatten()

    counts, bins = np.histogram(vals, range(257))



    amplitude = np.abs(f) + 1e-10

    phase = np.angle(f)
    hist, bins = np.histogram(img_gray.flatten(), bins=256, range=[0, 256])

    recovery = reconstruct_image(amplitude, phase)

    # Wyświetl obraz przefiltrowany
    plt.figure(figsize=(12, 12))

    plt.subplot(3, 3, 1)
    plt.imshow(img)
    plt.title('Color Image')

    plt.subplot(3, 3, 2)
    if len(img.shape) == 2:
        plt.imshow(np.abs(img_res), cmap='gray')
    else:
        print("tutut")
        plt.imshow(np.abs(img_res)/255)
    plt.title('Iff')

    plt.subplot(3, 3, 3)
    plt.imshow(recovery)
    plt.title('Phaze + Amplitude')

    plt.subplot(3, 3, 9)
    edges = plot_edges(img_normalized)
    plt.imshow(edges, cmap='gray')
    plt.title('Edges')
    plt.colorbar()

    #Black - 0 white - 250
    #https://stackoverflow.com/questions/22159160/python-calculate-histogram-of-image
    plt.subplot(3, 3, 5)
    plt.title('Histogram of Image Intensity')
    plt.xlabel('Intensity Value')
    plt.ylabel('Frequency')
    plt.bar(bins[:-1] - 0.5, counts, width=1, edgecolor='none')
    plt.xlim([-1, 256])



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



    plt.subplot(3, 3, 4)
    plt.imshow(kwant, cmap='gray')
    plt.title('Quant')




    #######################################################

    freq_x = np.fft.fftshift(np.fft.fftfreq(img.shape[1]))
    freq_y = np.fft.fftshift(np.fft.fftfreq(img.shape[0]))


    # Przygotuj widmo transformaty Fouriera
    spectrum_log = np.abs(f) + 1e-10
    spectrum_log_shifted = np.fft.fftshift(np.log(spectrum_log))
    X, Y = np.meshgrid(freq_x, freq_y)
    # Stwórz siatkę dwóch wykresów obok siebie
    plt.figure(figsize=(16, 6))

    # Pierwszy wykres: Częstotliwości w kierunku osi X
    plt.subplot(1, 2, 1)
    plt.plot(freq_x, spectrum_log_shifted[int(spectrum_log_shifted.shape[0] / 2)],
             label='Częstotliwości w kierunku osi X')
    plt.xlabel('Częstotliwość w kierunku osi X')
    plt.ylabel('Amplituda (log)')
    plt.title('Widmo Transformacji Fouriera (Częstotliwość w kierunku osi X)')
    plt.legend()
    plt.grid(True)

    # Drugi wykres: Częstotliwości w kierunku osi Y
    plt.subplot(1, 2, 2)
    plt.plot(freq_y, spectrum_log_shifted[:, int(spectrum_log_shifted.shape[1] / 2)],
             label='Częstotliwości w kierunku osi Y')
    plt.xlabel('Częstotliwość w kierunku osi Y')
    plt.ylabel('Amplituda (log)')
    plt.title('Widmo Transformacji Fouriera (Częstotliwość w kierunku osi Y)')
    plt.legend()
    plt.grid(True)



    # Tworzymy nową figurę z wykresami 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    # Tworzymy konturowy wykres 3D
    contour = ax.contour3D(X, Y, spectrum_log_shifted, 50, cmap='viridis', linewidths=0.5)

    # Dodajemy etykiety osi
    ax.set_xlabel('Przesunięta częstotliwość w kierunku osi X')
    ax.set_ylabel('Przesunięta częstotliwość w kierunku osi Y')
    ax.set_zlabel('Amplituda (log)')
    ax.set_title('Widmo Transformacji Fouriera')

    # Pokaż wykres
    #plt.colorbar(contour, ax=ax, label='Amplituda (log)')  # Dodajemy pasek kolorów
    #plt.show()

    plt.figure(figsize=(10, 8))
    spectrum_log = np.abs(f) + 1e-10
    spectrum_log_shifted = np.fft.fftshift(spectrum_log)  # Przesunięcie widma
    plt.imshow(np.log(spectrum_log_shifted), cmap='gray')  # Wyświetlenie przesuniętego widma
    plt.title('Fourier Transform Spectrum (Shifted)')
    plt.colorbar()
    #
    plt.show()
