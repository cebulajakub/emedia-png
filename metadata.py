import io
import zlib
import gzip
import png
import xml.etree.ElementTree as ET

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
                metadata['width'] = width
                metadata['height'] = height
                metadata['bit_depth'] = bit_depht
                metadata['color_type'] = color_type
                metadata['compression_method'] = Compressiom_method
                metadata['filter_method'] = Filter_method
                metadata['interlace_method'] = Interlace_method

                return metadata

##########################################################################333

def deinterlace(width, height, data):
    # Przeplot Adam7 ma 7 przeplotów, więc tworzymy odpowiednie listy dla każdego z nich
    pass1_data = bytearray()
    pass2_data = bytearray()
    pass3_data = bytearray()
    pass4_data = bytearray()
    pass5_data = bytearray()
    pass6_data = bytearray()
    pass7_data = bytearray()

    # Przeprowadzamy deinterlace
    for y in range(height):
        for x in range(width):
            if y % 8 == 0:
                pass1_data.append(data[y * width + x])
            elif y % 8 == 4:
                pass5_data.append(data[y * width + x])
            elif y % 8 == 2:
                if x % 2 == 0:
                    pass2_data.append(data[y * width + x])
                else:
                    pass6_data.append(data[y * width + x])
            elif y % 8 == 6:
                if x % 2 == 0:
                    pass3_data.append(data[y * width + x])
                else:
                    pass7_data.append(data[y * width + x])
            elif y % 8 == 1 or y % 8 == 3 or y % 8 == 5 or y % 8 == 7:
                if x % 4 == 0:
                    pass4_data.append(data[y * width + x])
                elif x % 4 == 1:
                    pass3_data.append(data[y * width + x])
                elif x % 4 == 2:
                    pass2_data.append(data[y * width + x])
                elif x % 4 == 3:
                    pass1_data.append(data[y * width + x])

    # Łączymy dane z każdego przeplotu w jedną ciągłą tablicę bajtów
    deinterlaced_data = pass1_data + pass2_data + pass3_data + pass4_data + pass5_data + pass6_data + pass7_data

    return deinterlaced_data


################################################

def read_png_metadata(file_path, sciezka_xml=None):
    metadata = {}
    idat_data = b''
    IHDR = read_png_header(file_path)

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
                    metadata = read_iTXT_chunk(chunk_data, metadata, sciezka_xml)
                elif chunk_type == b'tEXt':
                    metadata = read_tEXt_chunk(chunk_data, metadata)
                elif chunk_type == b'zTXt':
                    metadata = read_zTXt_chunk(chunk_data, metadata)
                elif chunk_type == b'IDAT':
                    idat_data += chunk_data
                elif chunk_type == b'cHRM':
                    metadata = read_cHRM_chunk(chunk_data, metadata)
                elif chunk_type == b'bKGD':
                    metadata = read_bKGD_chunk(chunk_data, metadata)
                elif chunk_type == b'pHYs':
                    metadata = read_pHYs_chunk(chunk_data, metadata)
                elif chunk_type == b'sRGB':
                    metadata = read_sRGB_chunk(chunk_data, metadata)
                elif chunk_type == b'PLTE':
                    metadata = read_PLTE_chunk(chunk_data, metadata)
                elif chunk_type == b'gAMA':
                    metadata = read_gAMA_chunk(chunk_data, metadata)
                elif chunk_type == b'tIME':
                    metadata = read_tIME_chunk(chunk_data, metadata)
                elif chunk_type == b'tRNS':
                    metadata = read_tRNS_chunk(chunk_data, metadata)
                elif chunk_type == b'sBIT':
                    metadata = read_sBIT_chunk(chunk_data, metadata)
                elif chunk_type == b'hIST':
                    metadata = read_hIST_chunk(chunk_data, metadata)
                elif chunk_type == b'sPLT':
                    metadata = read_sPLT_chunk(chunk_data, metadata)

    except Exception as e:
        print("Błąd podczas odczytywania metadanych PNG:", e)

    try:
        idat = zlib.decompress(idat_data)
        print(len(idat))
    except Exception as e:
        print("Błąd podczas dekompresji danych IDAT:", e)
        idat = b''  # Ustawienie pustych danych IDAT w przypadku błędu

    return metadata, idat


def read_iTXT_chunk(chunk_data, metadata, sciezka_xml):
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

    if sciezka_xml:
        korzen = ET.Element("metadane")
        element = ET.SubElement(korzen, keyword)
        element.text = text
        drzewo = ET.ElementTree(korzen)
        drzewo.write(sciezka_xml)

    return metadata


def read_tEXt_chunk(chunk_data, metadata):
    keyword, value = chunk_data.split(b'\x00', 1)
    metadata[keyword.decode()] = value.decode()
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
    if len(chunk_data) == 1:
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
    metadata['pHYs'] = {'pixels_per_unit_x': pixels_per_unit_x, 'pixels_per_unit_y': pixels_per_unit_y, 'unit_specifier': unit_specifier}
    return metadata


def read_sRGB_chunk(chunk_data, metadata):
    rendering_intent = int.from_bytes(chunk_data, byteorder='big')
    metadata['sRGB'] = rendering_intent
    return metadata


def read_PLTE_chunk(chunk_data, metadata):
    palette = int.from_bytes(chunk_data, byteorder='big')
    metadata['PLTE'] = palette
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
    if b'PLTE' in metadata:
        palette_size = len(metadata[b'PLTE'])
        if palette_size > 0:
            if palette_size == 2:
                alpha = int.from_bytes(chunk_data, byteorder='big')
                metadata['tRNS'] = {'gray_alpha': alpha}
            elif palette_size == 6:
                red_alpha = int.from_bytes(chunk_data[0:2], byteorder='big')
                green_alpha = int.from_bytes(chunk_data[2:4], byteorder='big')
                blue_alpha = int.from_bytes(chunk_data[4:6], byteorder='big')
                metadata['tRNS'] = {'red_alpha': red_alpha, 'green_alpha': green_alpha, 'blue_alpha': blue_alpha}
    return metadata


def read_sBIT_chunk(chunk_data, metadata):
    if b'PLTE' in metadata:
        palette_size = len(metadata[b'PLTE'])
        if palette_size > 0:
            if palette_size == 1:
                gray_bits = int.from_bytes(chunk_data, byteorder='big')
                metadata['sBIT'] = {'gray_bits': gray_bits}
            elif palette_size == 3:
                red_bits = int.from_bytes(chunk_data[0:1], byteorder='big')
                green_bits = int.from_bytes(chunk_data[1:2], byteorder='big')
                blue_bits = int.from_bytes(chunk_data[2:3], byteorder='big')
                metadata['sBIT'] = {'red_bits': red_bits, 'green_bits': green_bits, 'blue_bits': blue_bits}
    return metadata


def read_hIST_chunk(chunk_data, metadata):
    histogram = [int.from_bytes(chunk_data[i:i+2], byteorder='big') for i in range(0, len(chunk_data), 2)]
    metadata['hIST'] = histogram
    return metadata


def read_sPLT_chunk(chunk_data, metadata):
    palette_name, sample_depth, entries = chunk_data.split(b'\x00', 2)
    palette_name = palette_name.decode()
    sample_depth = int.from_bytes(sample_depth, byteorder='big')
    entries = [entries[i:i+sample_depth+1] for i in range(0, len(entries), sample_depth+1)]
    palette = [(entry[0:sample_depth].decode(), int.from_bytes(entry[sample_depth:], byteorder='big')) for entry in entries]
    metadata['sPLT'] = {'palette_name': palette_name, 'sample_depth': sample_depth, 'palette': palette}
    return metadata


def create_minimal_png_copy(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
            # Kopiuj nagłówek
            output_file.write(input_file.read(8))

            while True:
                # Odczytaj długość następnego chunka
                length_bytes = input_file.read(4)
                if not length_bytes:  # Koniec pliku
                    break
                chunk_length = int.from_bytes(length_bytes, byteorder='big')

                # Odczytaj typ chunka
                chunk_type = input_file.read(4)
                if not chunk_type:  # Koniec pliku
                    break

                # Odczytaj dane chunka
                chunk_data = input_file.read(chunk_length)

                # Odczytaj CRC
                crc = input_file.read(4)

                # Jeśli chunk jest jednym z wymaganych, skopiuj go
                if chunk_type in [b'IHDR', b'IDAT', b'IEND', b'PLTE']:
                    output_file.write(length_bytes)
                    output_file.write(chunk_type)
                    output_file.write(chunk_data)
                    output_file.write(crc)

    except Exception as e:
        print("Błąd podczas tworzenia minimalnej kopii pliku PNG:", e)


