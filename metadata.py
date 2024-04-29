import io
import struct
import zlib
import gzip

import numpy as np
import png
import re
import binascii
import xml.etree.ElementTree as ET
from PIL import Image
import matplotlib.pyplot as plt
import exifread





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
                IHDR_info = {
                    'width': width,
                    'height': height,
                    'bit_depth': bit_depht,
                    'color_type': color_type,
                    'Compressiom': Compressiom_method,
                    'Filter_method': Filter_method,
                    'Interlace_method': Interlace_method

                }
                #print(bit_depht)
                #print("2^BITDEPTH = ", 2 ** bit_depht)
                metadata['IHDR'] = IHDR_info

                return metadata


################################################


def read_png_metadata(file_path):
    metadata = {}
    idat_data = b''
    metadata = read_png_header(file_path)

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

                if chunk_type == b'iTXt':
                    metadata = read_iTXT_chunk(chunk_data, metadata)
                elif chunk_type == b'tEXt':
                    metadata = read_tEXt_chunk(chunk_data, metadata)
                elif chunk_type == b'zTXt':
                    metadata = read_zTXt_chunk(chunk_data, metadata)
                elif chunk_type == b'IDAT':
                    idat_data += chunk_data
                # print(chunk_data)
                elif chunk_type == b'cHRM':
                    metadata = read_cHRM_chunk(chunk_data, metadata)
                elif chunk_type == b'bKGD':
                    metadata = read_bKGD_chunk(chunk_data, metadata)
                elif chunk_type == b'pHYs':
                    metadata = read_pHYs_chunk(chunk_data, metadata)
                elif chunk_type == b'sRGB':
                    metadata = read_sRGB_chunk(chunk_data, metadata)
                elif chunk_type == b'PLTE':
                   # print(chunk_length)
                    #print("czytam plte")
                    metadata = read_PLTE_chunk(chunk_data, metadata)

                elif chunk_type == b'gAMA':
                    metadata = read_gAMA_chunk(chunk_data, metadata)
                elif chunk_type == b'tIME':
                    metadata = read_tIME_chunk(chunk_data, metadata)
                elif chunk_type == b'tRNS':
                    #print("tRNS")
                    metadata = read_tRNS_chunk(chunk_data, metadata)
                elif chunk_type == b'sBIT':
                    metadata = read_sBIT_chunk(chunk_data, metadata)
                elif chunk_type == b'sPLT':
                    metadata = read_sPLT_chunk(chunk_data, metadata)
                elif chunk_type == b'eXIf':
                    metadata = read_exif(chunk_data, metadata)
                if chunk_type == b'IEND':
                    metadata['IEND'] = crc


    except Exception as e:
        print("Błąd podczas odczytywania metadanych PNG:", e)
    # print(idat_data)

    #idat_data = zlib.decompress(idat_data)

    metadata = read_IDAT_chunk(idat_data, metadata)

    return metadata, idat_data


def apply_palette(Recon, metadata):
    """Replace indexed pixels in parsed IDAT with corresponding palette RGB values"""
    print('Applying palette')

    # Sprawdź, czy istnieje paleta PLTE w metadanych
    if 'PLTE' not in metadata:
        print("PLTE chunk not found.")
        return

    # Pobierz paletę RGB z metadanych
    palette = metadata['PLTE']['palette']

    # Sprawdź, czy dane IDAT zostały wcześniej przetworzone
    if Recon is None:
        print("No data to apply palette.")
        return

    # Aplikuj paletę do danych IDAT (Recon)
    applied_palette_data = bytearray()
    for pixel in Recon:
        try:
            pixel_index = int(pixel)
            if 0 <= pixel_index < len(palette):
                applied_palette_data.extend(palette[pixel_index])
            else:

                print("Invalid palette index:", pixel_index)
                # Wybierz domyślną wartość w przypadku nieprawidłowego indeksu
                applied_palette_data.extend(bytes([0, 0, 0]))  # Możesz wybrać inną domyślną wartość
        except ValueError:
            print("Invalid pixel value:", pixel)

            continue


    return applied_palette_data


# https://pyokagan.name/blog/2019-10-14-png/
def read_IDAT_chunk(idat_data, metadata):



    # Odczytujemy metadane obrazu
    width = metadata['IHDR']['width']
    height = metadata['IHDR']['height']
    color_type = metadata['IHDR']['color_type']
    bit_depth = metadata['IHDR']['bit_depth']


    # Obliczamy bytes_per_pixel
    bytes_per_pixel = calculate_bytes_per_pixel(metadata)

    stride = width * bytes_per_pixel
   # print("WIDTH:", width, " height :", height, " color_type :", color_type, " bit_depth :", bit_depth, " stride :", stride)

    # Dekompresujemy dane IDAT
    #print("BEFORE ZLIB:", idat_data)
    decompressed_idat_data = zlib.decompress(idat_data)
    #print("AFTER ZLIB : ",decompressed_idat_data)
    #print("COMPRESSING:", zlib.compress(decompressed_idat_data))
    #print("HIHI :")
    # Odtwarzamy piksele
    Recon = []
    i = 0
    for r in range(height):  # dla każdej linii skanowania
        filter_type = decompressed_idat_data[i]  # pierwszy bajt linii skanowania to typ filtra
        # print(filter_type)

        i += 1
        for c in range(stride):  # dla każdego bajtu w linii skanowania
            Filt_x = decompressed_idat_data[i]

            i += 1
            if filter_type == 0:  # None
                Recon_x = Filt_x
            elif filter_type == 1:  # Sub
                Recon_x = Filt_x + Recon_a(r, c, Recon, stride, bytes_per_pixel)
            elif filter_type == 2:  # Up
                Recon_x = Filt_x + Recon_b(r, c, Recon, stride)
            elif filter_type == 3:  # Average
                Recon_x = Filt_x + (Recon_a(r, c, Recon, stride, bytes_per_pixel) + Recon_b(r, c, Recon, stride)) // 2
            elif filter_type == 4:  # Paeth
                Recon_x = Filt_x + PaethPredictor(Recon_a(r, c, Recon, stride, bytes_per_pixel),
                                                  Recon_b(r, c, Recon, stride),
                                                  Recon_c(r, c, Recon, stride, bytes_per_pixel))
            else:
                print('unknown filter type: ' + str(filter_type))
                metadata['IDAT'] = len(idat_data)

                # Zwracamy metadane
                return metadata
            Recon.append(Recon_x & 0xff)  # przycinanie do bajtu

    image_array = np.array(Recon).reshape((height, width, bytes_per_pixel))
    print(image_array)
   # print(len(Recon))
    test = apply_palette(Recon, metadata)
    #print(len(test))
    test = np.array(test).reshape((height, width, 3))
    #print(test)
    # Wyświetlamy obraz
    plt.imshow(test)

    plt.show()

    # Zapisujemy dane IDAT w metadanych
    metadata['IDAT'] = len(idat_data)

    # Zwracamy metadane
    #return metadata
    return metadata


def calculate_bytes_per_pixel(metadata):
    color_type = metadata['IHDR']['color_type']
    bit_depth = metadata['IHDR']['bit_depth']

    color_type_bytes_per_pixel = {
        0: bit_depth // 8,  # Greyscale
        2: 3 * (bit_depth // 8),  # Truecolour (RGB)
        3: 1,  # Indexed-colour
        4: 2 * (bit_depth // 8),  # Greyscale with alpha
        6: 4 * (bit_depth // 8)  # Truecolour with alpha (RGBA)
    }
    if color_type in color_type_bytes_per_pixel:
        return color_type_bytes_per_pixel[color_type]
    else:

        raise Exception('unknown color_type: ' + str(color_type))


def Recon_a(r, c, Recon, stride, bytes_per_pixel):
    return Recon[r * stride + c - bytes_per_pixel] if c >= bytes_per_pixel else 0


def Recon_b(r, c, Recon, stride):
    return Recon[(r - 1) * stride + c] if r > 0 else 0


def Recon_c(r, c, Recon, stride, bytes_per_pixel):
    return Recon[(r - 1) * stride + c - bytes_per_pixel] if r > 0 and c >= bytes_per_pixel else 0


def PaethPredictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        Pr = a
    elif pb <= pc:
        Pr = b
    else:
        Pr = c
    return Pr


def translate_tag(tag):
    tags = {
        256: 'ImageWidth',
        257: 'ImageHeight',
        258: 'BitsPerSample',
        259: 'Compression',
        262: 'PhotometricInterpretation',
        273: 'StripOffsets',
        277: 'SamplesPerPixel',
        278: 'RowsPerStrip',
        279: 'StripByteCounts',
        282: 'XResolution',
        283: 'YResolution',
        284: 'PlanarConfiguration',
        296: 'ResolutionUnit',
        513: 'JPEGInterchangeFormat',
        514: 'ThumbnailLength',
        515: 'JPEGRestartInterval',
        531: 'YCbCrPositioning',
        34665: 'ExifOffset',
        36864: 'ExifVersion',
        36867: 'DateTimeOriginal',
        37121: 'ComponentsConfiguration',
        40960: 'FlashpixVersion',
        40961: 'ColorSpace'

    }
    return tags.get(tag, f'Unknown Tag ({tag})')


def data_to_value(type, value_data, byte_order, isIFD):
    if type == 1:  # BYTE
        return int.from_bytes(value_data, byteorder=byte_order)
    elif type == 2:  # ASCII
        return value_data.decode('utf-8').rstrip('\x00')
    elif type == 3:  # SHORT
        if isIFD:
            return int.from_bytes(value_data[:2], byteorder=byte_order)

        else:
            return value_data[:2]
    elif type == 4:  # LONG
        return int.from_bytes(value_data, byteorder=byte_order)
    elif type == 5:  # RATIONAL
        numerator = int.from_bytes(value_data[:4], byteorder=byte_order)
        denominator = int.from_bytes(value_data[4:], byteorder=byte_order)
        return (numerator, denominator)
    elif type == 7:  # UNDEFINED
        return value_data
    else:
        return None


def bpc(type):
    if type == 1:  # BYTE
        return 1
    elif type == 2:  # ASCII
        return 1
    elif type == 3:  # SHORT
        return 2
    elif type == 4:  # LONG
        return 4
    elif type == 5:  # RATIONAL
        return 8
    elif type == 7:  # UNDEFINED
        return 1
    else:
        return 0  # Unknown


# https://www.media.mit.edu/pia/Research/deepview/exif.html
def read_exif(chunk_data, metadata):
    # Odczytaj informację o kolejności bajtów
    if chunk_data[:2] == b'II':
        byte_order = 'little'
    elif chunk_data[:2] == b'MM':
        byte_order = 'big'
    else:
        return None

    # przesunięcie do IFD0
    offset_ifd0 = int.from_bytes(chunk_data[4:6], byte_order)
    if offset_ifd0 == 0:
        offset_ifd0 = 8

    # liczbę wpisów  IFD0
    number_entries_ifd0 = int.from_bytes(chunk_data[offset_ifd0:offset_ifd0 + 2], byte_order)
    offset_ifd0 += 2

    ifd0_list = []
    exif_offset = None
    for i in range(number_entries_ifd0):
        # Odczytaj tag, typ danych, liczbę składników i rozmiar
        tag = int.from_bytes(chunk_data[offset_ifd0 + 12 * i:offset_ifd0 + 12 * i + 2], byte_order)
        type = int.from_bytes(chunk_data[offset_ifd0 + 12 * i + 2:offset_ifd0 + 12 * i + 4], byte_order)
        comp_count = int.from_bytes(chunk_data[offset_ifd0 + 12 * i + 4:offset_ifd0 + 12 * i + 8], byte_order)
        size = bpc(type) * comp_count

        if size <= 4:
            value_data = chunk_data[offset_ifd0 + 12 * i + 8:offset_ifd0 + 12 * i + 12]
        else:
            data_offset = int.from_bytes(chunk_data[offset_ifd0 + 12 * i + 8:offset_ifd0 + 12 * i + 12], byte_order)
            value_data = chunk_data[data_offset:data_offset + size]

        #  czy to jest tag Exif Offset
        if tag == 0x8769:
            exif_offset = int.from_bytes(value_data, byte_order)

        ifd0_list.append((translate_tag(tag), data_to_value(type, value_data, byte_order, True)))

    metadata['ifd0'] = ifd0_list

    if exif_offset is not None:
        exif_ifd_metadata = read_exif_ifd(chunk_data, exif_offset, byte_order)
        metadata['exif_subifd'] = exif_ifd_metadata

    return metadata


def read_exif_ifd(chunk_data, exif_offset, byte_order):
    number_entries_exif_ifd = int.from_bytes(chunk_data[exif_offset:exif_offset + 2], byte_order)
    exif_offset += 2

    exif_ifd_list = []
    for i in range(number_entries_exif_ifd):

        tag = int.from_bytes(chunk_data[exif_offset + 12 * i:exif_offset + 12 * i + 2], byte_order)
        type = int.from_bytes(chunk_data[exif_offset + 12 * i + 2:exif_offset + 12 * i + 4], byte_order)
        comp_count = int.from_bytes(chunk_data[exif_offset + 12 * i + 4:exif_offset + 12 * i + 8], byte_order)
        size = bpc(type) * comp_count

        if size <= 4:
            value_data = chunk_data[exif_offset + 12 * i + 8:exif_offset + 12 * i + 12]
        else:
            data_offset = int.from_bytes(chunk_data[exif_offset + 12 * i + 8:exif_offset + 12 * i + 12], byte_order)
            value_data = chunk_data[data_offset:data_offset + size]

        exif_ifd_list.append((translate_tag(tag), data_to_value(type, value_data, byte_order, False)))

    return exif_ifd_list


def read_eXIf_chunk(chunk_data, metadata):
    try:
        chunk_file = io.BytesIO(chunk_data)
        exif_tags = exifread.process_file(chunk_file, details=False)
        for tag in exif_tags:
            metadata[tag] = str(exif_tags[tag])

    except Exception as e:
        print("Błąd podczas przetwarzania danych EXIF:", e)

    return metadata


def read_iTXT_chunk(chunk_data, metadata):
    iTxt_info = {}
    try:
        keyword, rest = chunk_data.split(b'\x00', 1)
        compression_flag, rest = rest.split(b'\x00', 1)
        language_tag, rest = rest.split(b'\x00', 1)
        translated_keyword, text_data = rest.split(b'\x00', 1)

        keyword = keyword.decode()
        compression_flag = int.from_bytes(compression_flag, byteorder='big')
        language_tag = language_tag.decode()
        translated_keyword = translated_keyword.decode()

        if compression_flag == 1:
            try:
                text_data = zlib.decompress(text_data)
            except zlib.error as e:
                print("Błąd podczas dekompresji danych algorytmem zlib:", e)
                return metadata

        text = text_data.decode()

        metadata[keyword] = text
        # Przetwarzanie tagów XML:com.adobe.xmp
        # pattern = r'<(exif:|tiff:)(.*?)>(.*?)<\/\1.*?>'
        pattern = r'<(exif|tiff):([^>]+)>(.*?)<\/\1:.*?>'
        # pattern = r'<(?:exif|tiff):([^>]+)>\s*<rdf:Seq>\s*<rdf:li>(.*?)<\/rdf:li>\s*<\/rdf:Seq>'
        matches = re.findall(pattern, text, re.DOTALL)
        # matches = re.findall(pattern, text)

        for match in matches:
            print(match[2])
            if "<rdf:Seq>" in match[2] and "<rdf:li>" in match[2]:
                extracted_value = re.search(r'<rdf:li>(.*?)<\/rdf:li>', match[2]).group(1)
                print(f"Wartość wyodrębniona: {extracted_value}")
                tag_type, tag_name, tag_value = match[0], match[1], extracted_value
                metadata[f"{tag_name}"] = tag_value.strip()
            else:
                tag_type, tag_name, tag_value = match
                # Dodajemy metadane do słownika metadata
                metadata[f"{tag_name}"] = tag_value.strip()

    except ValueError as e:
        print("Błąd podczas parsowania danych iTXt:", e)

    return metadata


def read_tEXt_chunk(chunk_data, metadata):
    try:
        keyword, value = chunk_data.split(b'\x00', 1)
        metadata[keyword.decode()] = value.decode()
        metadata['tEXt'] = {keyword.decode(): value.decode()}
    except ValueError as e:
        print("Error parsing tEXt chunk data:", e)
    return metadata


def read_zTXt_chunk(chunk_data, metadata):
    keyword, comp_data = chunk_data.split(b'\x00', 1)

    compression = comp_data.split(b'\x00', 1)
    if compression[0] == b'\x00':
        value = compression[1]
        metadata[keyword.decode()] = value.decode('latin-1')
    else:
        try:
            value = zlib.decompress(compression[1])
            metadata[keyword.decode()] = value.decode('latin-1')
        except zlib.error as e:
            print("Błąd podczas dekompresji danych:", e)

    return metadata


#
def read_cHRM_chunk(chunk_data, metadata):
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
    return metadata


def read_bKGD_chunk(chunk_data, metadata):
    # print(chunk_data)
    if len(chunk_data) == 1:
        Palette = int.from_bytes(chunk_data, byteorder='big')
        metadata['bKGD'] = {'Palette index': Palette}
    elif len(chunk_data) == 2:
        gray_level = int.from_bytes(chunk_data, byteorder='big')
        metadata['bKGD'] = {'gray_level': gray_level}
    elif len(chunk_data) == 6:
        red = int.from_bytes(chunk_data[0:2], byteorder='big')
        green = int.from_bytes(chunk_data[2:4], byteorder='big')
        blue = int.from_bytes(chunk_data[4:6], byteorder='big')
        metadata['bKGD'] = {'red': red, 'green': green, 'blue': blue}

    return metadata


def read_pHYs_chunk(chunk_data, metadata):
    pixels_per_unit_x = int.from_bytes(chunk_data[0:4], byteorder='big')
    pixels_per_unit_y = int.from_bytes(chunk_data[4:8], byteorder='big')
    unit_specifier = int.from_bytes(chunk_data[8:9], byteorder='big')
    metadata['pHYs'] = {'pixels_per_unit_x': pixels_per_unit_x, 'pixels_per_unit_y': pixels_per_unit_y,
                        'unit_specifier': unit_specifier}
    return metadata


def read_sRGB_chunk(chunk_data, metadata):
    rendering_intent = int.from_bytes(chunk_data, byteorder='big')
    metadata['sRGB'] = rendering_intent
    return metadata


def read_gAMA_chunk(chunk_data, metadata):
    gamma_value = int.from_bytes(chunk_data, byteorder='big') / 100000
    metadata['gAMA'] = gamma_value
    return metadata


def read_tIME_chunk(chunk_data, metadata):
    year = int.from_bytes(chunk_data[0:2], byteorder='big')
    month = int.from_bytes(chunk_data[2:3], byteorder='big')
    day = int.from_bytes(chunk_data[3:4], byteorder='big')
    hour = int.from_bytes(chunk_data[4:5], byteorder='big')
    minute = int.from_bytes(chunk_data[5:6], byteorder='big')
    second = int.from_bytes(chunk_data[6:7], byteorder='big')
    metadata['tIME'] = {'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute, 'second': second}
    return metadata


def read_tRNS_chunk(chunk_data, metadata):
    color_type = metadata['IHDR']['color_type']
    if color_type == 3:

        if 'PLTE' in metadata:

            palette_size = len(metadata['PLTE']['palette'])
            if palette_size > 0:
                alpha_values = [int.from_bytes(chunk_data[i:i+1], byteorder='big') for i in range(palette_size)]
                metadata['tRNS'] = {'alpha_values': alpha_values}
    elif color_type == 0:
        alpha = int.from_bytes(chunk_data, byteorder='big')
        metadata['tRNS'] = {'gray_alpha': alpha}
    elif color_type == 2:
        red_alpha = int.from_bytes(chunk_data[0:2], byteorder='big')
        green_alpha = int.from_bytes(chunk_data[2:4], byteorder='big')
        blue_alpha = int.from_bytes(chunk_data[4:6], byteorder='big')
        metadata['tRNS'] = {'red_alpha': red_alpha, 'green_alpha': green_alpha, 'blue_alpha': blue_alpha}
    return metadata


def read_PLTE_chunk(chunk_data, metadata):
    palette = [chunk_data[i:i+3] for i in range(0, len(chunk_data), 3)]
    PLTE_info = {
        'palette': palette,
        'PLTE_size': len(palette)
    }
    metadata['PLTE'] = PLTE_info
    return metadata



def read_sBIT_chunk(chunk_data, metadata):
    color_type = metadata['IHDR']['color_type']
    sample_depth = metadata['IHDR']['bit_depth']

    if color_type == 0:
        gray_bits = int.from_bytes(chunk_data, byteorder='big')
        metadata['sBIT'] = {'white_bits': gray_bits}
    elif color_type == 2 or color_type == 3:
        red_bits = int.from_bytes(chunk_data[0:1], byteorder='big')
        green_bits = int.from_bytes(chunk_data[1:2], byteorder='big')
        blue_bits = int.from_bytes(chunk_data[2:3], byteorder='big')
        metadata['sBIT'] = {'red_bits': red_bits, 'green_bits': green_bits, 'blue_bits': blue_bits}
    elif color_type == 4:
        gray_bits = int.from_bytes(chunk_data[0:1], byteorder='big')
        alpha_bits = int.from_bytes(chunk_data[1:2], byteorder='big')
        metadata['sBIT'] = {'white_bits': gray_bits, 'alpha_bits': alpha_bits}
    elif color_type == 6:
        red_bits = int.from_bytes(chunk_data[0:1], byteorder='big')
        green_bits = int.from_bytes(chunk_data[1:2], byteorder='big')
        blue_bits = int.from_bytes(chunk_data[2:3], byteorder='big')
        alpha_bits = int.from_bytes(chunk_data[3:4], byteorder='big')
        metadata['sBIT'] = {'red_bits': red_bits, 'green_bits': green_bits, 'blue_bits': blue_bits,
                            'alpha_bits': alpha_bits}

    return metadata



def read_sPLT_chunk(chunk_data, metadata):
    # Podziel chunk_data na nazwę palety, głębokość próbki i wpisy
    palette_name, rest = chunk_data.split(b'\x00', 1)
    sample_depth, entries = rest[:1], rest[1:]

    # Dekoduj nazwę palety
    palette_name = palette_name.decode('latin-1')
    sample_depth = int.from_bytes(sample_depth, byteorder='big')

    palette = []
    entry_length = sample_depth * 5 + 2
    for i in range(0, len(entries), entry_length):
        entry = entries[i:i + entry_length]
        red = int.from_bytes(entry[:sample_depth], byteorder='big')
        green = int.from_bytes(entry[sample_depth:sample_depth * 2], byteorder='big')
        blue = int.from_bytes(entry[sample_depth * 2:sample_depth * 3], byteorder='big')
        alpha = int.from_bytes(entry[sample_depth * 3:sample_depth * 4], byteorder='big')
        frequency = int.from_bytes(entry[sample_depth * 4:sample_depth * 5 + 2], byteorder='big')
        palette.append((red, green, blue, alpha, frequency))

    if 'sPLT' not in metadata:
        metadata['sPLT'] = []
    metadata['sPLT'].append({'palette_name': palette_name, 'sample_depth': sample_depth, 'palette': palette})
    return metadata


def create_minimal_png_copy(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
            # nagłówek
            output_file.write(input_file.read(8))

            combined_idat_data = b''

            while True:
                #  długość następnego chunka
                length_bytes = input_file.read(4)
                if not length_bytes:  # Koniec pliku
                    break
                chunk_length = int.from_bytes(length_bytes, byteorder='big')

                #  typ chunka
                chunk_type = input_file.read(4)
                if not chunk_type:  # koniec pliku
                    break

                #  dane chunka
                chunk_data = input_file.read(chunk_length)

                #  CRC
                crc = input_file.read(4)

                #  chunk IDAT-> dodaj  do  danych IDAT
                if chunk_type == b'IDAT' and chunk_length != 0:
                    combined_idat_data += chunk_data
                else:
                    #  nie chunk IDAT zapisz w dane IDAT
                    if combined_idat_data:
                        # Połącz wszystkie chunki IDAT w jeden
                        combined_idat_chunk = len(combined_idat_data).to_bytes(4,
                                                                               byteorder='big') + b'IDAT' + combined_idat_data + zlib.crc32(
                            b'IDAT' + combined_idat_data).to_bytes(4, byteorder='big')
                        # Zapisz połączony chunk IDAT do pliku wyjściowego
                        output_file.write(combined_idat_chunk)
                        # Wyczyść zmienne zawierające połączone dane IDAT
                        combined_idat_data = b''

                    # Zapisz aktualny chunk (jeśli to jeden z wymaganych) do pliku wyjściowego
                    if chunk_type in [b'IHDR', b'IEND', b'PLTE'] or (chunk_type == b'IDAT' and chunk_length != 0):
                        output_file.write(length_bytes)
                        output_file.write(chunk_type)
                        output_file.write(chunk_data)
                        output_file.write(crc)




    except Exception as e:
        print("Błąd podczas kopiowania pliku PNG:", e)
