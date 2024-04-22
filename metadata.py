import io
import zlib
import gzip
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
                break

##########################################################################333

def read_png_metadata(file_path, sciezka_xml=None):
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

                if chunk_type == b'iTXt':

                        keyword, value = chunk_data.split(b'\x00', 1)
                        keyword_decoded = keyword.decode('latin-1')  # Dekodowanie klucza jako Latin-1
                        compression_flag = value[0]  # Pierwszy bajt to flaga kompresji
                        print(f"Compression_flag: {value}")
                        if compression_flag == 0:
                            # Dane nie są skompresowane
                            print("aaaaa")
                            value_decoded = value.decode('latin-1')

                        elif compression_flag == 1:
                            try:

                                decompressed_value = zlib.decompress(value)
                                value_decoded = decompressed_value.decode('latin-1')
                            except zlib.error as e:
                                print("Błąd podczas dekompresji danych:", e)




                        # Sprawdź, czy dane zawierają klucz "translated keyword"
                        if b'\x00' in value:
                            print("bbb")
                            translated_keyword, data = value.split(b'\x00', 1)
                            translated_keyword_decoded = translated_keyword.decode(
                                'latin-1')  # Dekodowanie klucza jako Latin-1
                        else:

                            translated_keyword_decoded = None

                        metadata[keyword_decoded] = value_decoded

                        # Utwórz plik XML z danymi iTXt
                        if sciezka_xml:
                            korzen = ET.Element("metadane")
                            if translated_keyword_decoded:
                                # Jeśli klucz "translated keyword" istnieje, dodaj go do XML
                                element_translated = ET.SubElement(korzen, "translated_keyword")
                                element_translated.text = translated_keyword_decoded
                            element = ET.SubElement(korzen, keyword_decoded)
                            element.text = value_decoded
                            drzewo = ET.ElementTree(korzen)
                            drzewo.write(sciezka_xml)


                elif chunk_type == b'tEXt':
                    keyword, value = chunk_data.split(b'\x00', 1)
                    metadata[keyword.decode()] = value.decode('Latin-1')
                elif chunk_type == b'zTXt':
                    # Rozdziel klucz i dane skompresowane
                    keyword, comp_data = chunk_data.split(b'\x00', 1)

                    # Sprawdź, czy dane są skompresowane
                    compression = comp_data.split(b'\x00', 1)
                    if compression[0] == b'\x00':
                        # Dane nie są skompresowane
                        value = compression[1]  # Pomijamy bajt określający metodę kompresji
                        metadata[keyword.decode()] = value.decode('latin-1')
                    else:
                        # Dane są skompresowane, użyj odpowiedniej metody dekompresji
                        try:
                            value = zlib.decompress(compression[1])
                            metadata[keyword.decode()] = value.decode('latin-1')
                        except zlib.error as e:
                            print("Błąd podczas dekompresji danych:", e)
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


