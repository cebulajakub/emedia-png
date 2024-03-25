
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from metadata import read_png_metadata
from  fourier import furier_trans_pngg



if __name__ == "__main__":
    file_path = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\spermik.png"  # Ścieżka do pliku PNG
    #file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\spermik.png"
    #file_path = r"C:\Users\PRO\Desktop\Programy-Projekty\Python\pngs\poli.png"
    #read_png_header(file_path)
    #show_png(file_path)
    #furier_trans_png(file_path)
    furier_trans_pngg(file_path, 20)
    #equals(file_path)
    metadata = read_png_metadata(file_path)
    if metadata:
        print("Metadane PNG:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    else:
        print("Nie udało się wczytać metadanych PNG.")

