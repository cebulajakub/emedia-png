import zlib

from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL.Image import Image

from metadata import read_png_metadata, create_minimal_png_copy, read_png_header
from fourier import furier_trans_pngg

if __name__ == "__main__":
    file_path = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\a.png" # Ścieżka do pliku PNG
    file_path_xml = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\metadane.xml"
    file_path_copy = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\copy.png"
    #file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\drag.png"
    #file_path_xml = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\metadane.xml"
    #file_path_copy = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\copy.png"

    input_file_path = file_path
    output_file_path = file_path_copy
    create_minimal_png_copy(input_file_path, output_file_path)

    # get_decompressed_idat_data(file_path)

    # furier_trans_pngg(file_path, 50)

    metadata, idat = read_png_metadata(file_path, file_path_xml)
    if metadata:
        print("Metadane PNG:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    elif idat:
        print(idat)
        print(f"IDATA LENGHT:{len(idat)}")

    metadatacpy, idat_data = read_png_metadata(file_path_copy, file_path_xml)
    if metadatacpy:
        print("Metadane PNG:")
        for key, value in metadatacpy.items():
            print(f"{key}: {value}")
    elif idat_data:
        print("IDATA")
        print(f"IDATA LENGHT:{len(idat_data)}")
