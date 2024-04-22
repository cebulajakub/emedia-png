
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from metadata import read_png_metadata, create_minimal_png_copy, read_png_header
from fourier import furier_trans_pngg

if __name__ == "__main__":
    file_path = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\itxt.png" # Ścieżka do pliku PNG
    file_path_xml = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\metadae.xml"
    #file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\vwboot.png"
   #file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\ball.png"
    #file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\gull.png"
    #file_path_copy = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\copy.png"
    file_path_copy = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\copy.png"
    input_file_path = file_path
    output_file_path = file_path_copy
    create_minimal_png_copy(input_file_path, output_file_path)
    read_png_header(file_path_copy)
    #show_png(file_path)
   # furier_trans_png(file_path)
    furier_trans_pngg(file_path, 50)
    #equals(file_path)
    metadata = read_png_metadata(file_path,file_path_xml)
    if metadata:
        print("Metadane PNG:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    else:
        print("Nie udało się wczytać metadanych PNG.")




