
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import zlib
from scipy import ndimage





def read_png_header(file_path):
    metadata = {}

    with open(file_path, 'rb') as file:

        png_signature = file.read(8)
        if png_signature != b'\x89PNG\r\n\x1a\n':  # specjalny ciaf bajtów na poczatku pliku PNG
            print("To nie jest plik PNG.")
            return

        while True:
            length_bytes = file.read(4)
            chunk_length = int.from_bytes(length_bytes, byteorder='big')  # sekwencja bajtów na inty

            chunk_type = file.read(4)

            if chunk_type == b'IHDR':
                data = file.read(chunk_length)

                width = int.from_bytes(data[0:4], byteorder='big')
                height = int.from_bytes(data[4:8], byteorder='big')
                bit_depht = data[8]
                color_type = data[9]
                Compressiom_method = data[10]
                Filter_method = data[11]
                Interlace_method = data[12]
                print(f"Szerokość: {width}, Wysokość: {height}, Bitdepht: {bit_depht}")
                print(f" color_type: {color_type}, Compressiom_method: {Compressiom_method}")
                print(f"Filter_method: {Filter_method}, Interlace_method: {Interlace_method}")
                break





def read_png_metadata(file_path):
    metadata = {}

    try:
        with open(file_path, 'rb') as file:

            file.read(8)

            while True:

                length_bytes = file.read(4)
                if not length_bytes:
                    break

                chunk_length = int.from_bytes(length_bytes, byteorder='big')


                chunk_type = file.read(4)
                if not chunk_type:
                    break


                chunk_data = file.read(chunk_length)


                crc = file.read(4)


                if chunk_type == b'tEXt':
                    keyword, value = chunk_data.split(b'\x00', 1)
                    metadata[keyword.decode()] = value.decode()
                elif chunk_type == b'zTXt':
                    # Decompress compressed data
                    keyword, comp_data = chunk_data.split(b'\x00', 1)
                    value = zlib.decompress(comp_data)
                    metadata[keyword.decode()] = value.decode()
                elif chunk_type == b'cHRM':
                    white_point_x = int.from_bytes(chunk_data[0:4], byteorder='big') / 100000
                    white_point_y = int.from_bytes(chunk_data[4:8], byteorder='big') / 100000
                    red_x = int.from_bytes(chunk_data[8:12], byteorder='big') / 100000
                    red_y = int.from_bytes(chunk_data[12:16], byteorder='big') / 100000
                    green_x = int.from_bytes(chunk_data[16:20], byteorder='big') / 100000
                    green_y = int.from_bytes(chunk_data[20:24], byteorder='big') / 100000
                    blue_x = int.from_bytes(chunk_data[24:28], byteorder='big') / 100000
                    blue_y = int.from_bytes(chunk_data[28:32], byteorder='big') / 100000

                    chromaticity_data = {
                        'white_point': (white_point_x, white_point_y),
                        'red': (red_x, red_y),
                        'green': (green_x, green_y),
                        'blue': (blue_x, blue_y)
                    }

                    metadata['cHRM'] = chromaticity_data
                elif chunk_type == b'bKGD':
                    if len(chunk_data) == 1:  # Gray level background
                        gray_level = int.from_bytes(chunk_data, byteorder='big')
                        metadata['bKGD'] = {'gray_level': gray_level}
                    elif len(chunk_data) == 6:  # RGB background
                        red = int.from_bytes(chunk_data[0:2], byteorder='big')
                        green = int.from_bytes(chunk_data[2:4], byteorder='big')
                        blue = int.from_bytes(chunk_data[4:6], byteorder='big')
                        metadata['bKGD'] = {'red': red, 'green': green, 'blue': blue}
                elif chunk_type == b'pHYs':
                    pixels_per_unit_x = int.from_bytes(chunk_data[0:4], byteorder='big')
                    pixels_per_unit_y = int.from_bytes(chunk_data[4:8], byteorder='big')
                    unit_specifier = int.from_bytes(chunk_data[8:9], byteorder='big')
                    metadata['pHYs'] = {'pixels_per_unit_x': pixels_per_unit_x, 'pixels_per_unit_y': pixels_per_unit_y, 'unit_specifier': unit_specifier}
                elif chunk_type == b'sRGB':
                    rendering_intent = int.from_bytes(chunk_data, byteorder='big')
                    metadata['sRGB'] = rendering_intent
                elif chunk_type == b'PLTE':
                    palette = int.from_bytes(chunk_data, byteorder='big')
                    metadata['PLTE'] = palette
                elif chunk_type == b'gAMA':
                    gamma_value = int.from_bytes(chunk_data, byteorder='big') / 100000
                    metadata['gAMA'] = gamma_value
                elif chunk_type == b'tIME':
                    year = int.from_bytes(chunk_data[0:2], byteorder='big')
                    month = int.from_bytes(chunk_data[2:3], byteorder='big')
                    day = int.from_bytes(chunk_data[3:4], byteorder='big')
                    hour = int.from_bytes(chunk_data[4:5], byteorder='big')
                    minute = int.from_bytes(chunk_data[5:6], byteorder='big')
                    second = int.from_bytes(chunk_data[6:7], byteorder='big')
                    metadata['tIME'] = {'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute, 'second': second}
                elif chunk_type == b'tRNS':
                    if b'PLTE' in metadata:
                        palette_size = len(metadata[b'PLTE'])
                        if palette_size > 0:
                            if palette_size == 2:  # Grayscale with alpha
                                alpha = int.from_bytes(chunk_data, byteorder='big')
                                metadata['tRNS'] = {'gray_alpha': alpha}
                            elif palette_size == 6:  # RGB with alpha
                                red_alpha = int.from_bytes(chunk_data[0:2], byteorder='big')
                                green_alpha = int.from_bytes(chunk_data[2:4], byteorder='big')
                                blue_alpha = int.from_bytes(chunk_data[4:6], byteorder='big')
                                metadata['tRNS'] = {'red_alpha': red_alpha, 'green_alpha': green_alpha, 'blue_alpha': blue_alpha}
                elif chunk_type == b'sBIT':
                    if b'PLTE' in metadata:
                        palette_size = len(metadata[b'PLTE'])
                        if palette_size > 0:
                            if palette_size == 1:  # Grayscale
                                gray_bits = int.from_bytes(chunk_data, byteorder='big')
                                metadata['sBIT'] = {'gray_bits': gray_bits}
                            elif palette_size == 3:  # RGB
                                red_bits = int.from_bytes(chunk_data[0:1], byteorder='big')
                                green_bits = int.from_bytes(chunk_data[1:2], byteorder='big')
                                blue_bits = int.from_bytes(chunk_data[2:3], byteorder='big')
                                metadata['sBIT'] = {'red_bits': red_bits, 'green_bits': green_bits, 'blue_bits': blue_bits}
                elif chunk_type == b'hIST':
                    histogram = [int.from_bytes(chunk_data[i:i+2], byteorder='big') for i in range(0, len(chunk_data), 2)]
                    metadata['hIST'] = histogram
                elif chunk_type == b'sPLT':
                    palette_name, sample_depth, entries = chunk_data.split(b'\x00', 2)
                    palette_name = palette_name.decode()
                    sample_depth = int.from_bytes(sample_depth, byteorder='big')
                    entries = [entries[i:i+sample_depth+1] for i in range(0, len(entries), sample_depth+1)]
                    palette = [(entry[0:sample_depth].decode(), int.from_bytes(entry[sample_depth:], byteorder='big')) for entry in entries]
                    metadata['sPLT'] = {'palette_name': palette_name, 'sample_depth': sample_depth, 'palette': palette}

    except Exception as e:
        print("Błąd podczas odczytywania metadanych PNG:", e)

    return metadata

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

def show_png(file_path):
    im = Image.open(file_path)
    im.show()


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
    plt.figure(figsize=(12, 6))

    plt.subplot(131)
    plt.imshow(img, cmap='gray')
    plt.title('Color Image')

    plt.subplot(132)
    plt.imshow(img_gray, cmap='gray')
    plt.title('Grayscale Image')

    plt.subplot(133)
    spectrum_log = np.abs(spectrum) + 1e-10
    plt.imshow(np.log(spectrum_log), cmap='gray')#gray
    plt.title('Fourier Transform Spectrum')
    plt.colorbar()

    plt.show()





if __name__ == "__main__":
    file_path = r"C:\Users\Jakub\Desktop\EMEDIA\png\moon.png"  # Ścieżka do pliku PNG
   # file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\Sigma.png"
    #file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\poli.png"
    read_png_header(file_path)
   # show_png(file_path)
    #furier_trans_png(file_path)
    #equals(file_path)
    metadata = read_png_metadata(file_path)
    if metadata:
        print("Metadane PNG:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    else:
        print("Nie udało się wczytać metadanych PNG.")

