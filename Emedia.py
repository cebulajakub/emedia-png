
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error
import matplotlib.image as mpimg
import exifread
import zlib


# image = Image.open(r"C:\Users\PRO\Downloads\spermik.png")
# image = Image.open(r"C:\Users\PRO\Downloads\drag.png")
# image = Image.open(r"C:\Users\PRO\Downloads\spermik.png")

imagename = r"C:\Users\PRO\Downloads\spermik.png"


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



            elif chunk_type == b'sRGB':
                data = file.read(chunk_length)
                rendering_intent = data[0]
                print(f"Rendering intent: {rendering_intent}")

            elif chunk_type == b'IEND':
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





                if chunk_type == b'tEXt':
                    keyword, value = chunk_data.split(b'\x00', 1)
                    metadata[keyword.decode()] = value.decode()
                elif chunk_type == b'zTXt':
                    # Rozpakuj skompresowane dane
                    keyword, comp_data = chunk_data.split(b'\x00', 1)
                    value = zlib.decompress(comp_data)
                    metadata[keyword.decode()] = value.decode()

    except Exception as e:
        print("Błąd podczas odczytywania metadanych PNG:", e)

    return metadata



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
    file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\spermik.png"  # Ścieżka do pliku PNG
   # file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\Sigma.png"
    #file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\poli.png"
   # read_png_header(file_path)
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

