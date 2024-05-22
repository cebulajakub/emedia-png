import os
import random
from collections import deque

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import math
import zlib

from PIL import Image
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB
from matplotlib import pyplot as plt
import png

from metadata import read_png_metadata, read_IDAT_chunk, calculate_bytes_per_pixel


class KeyGen:
    def __init__(self, keysize):
        self.keysize = keysize
        self.prime = keysize // 2
        self.p = 0
        self.q = 0
        self.phi = 0
        self.n = 0
        self.e = 0
        self.d = 0
        self.public_key = (self.e, self.n)
        self.private_key = (self.d, self.n)

    # https://inventwithpython.com/rabinMiller.py
    def rabinMiller(self, num):
        # Returns True if num is a prime number.
        # print("Miller")
        s = num - 1
        t = 0
        while s % 2 == 0:
            # keep halving s while it is even (and use t
            # to count how many times we halve s)
            s = s // 2
            t += 1

        for trials in range(5):  # try to falsify num's primality 5 times
            a = random.randrange(2, num - 1)
            v = pow(a, s, num)
            if v != 1:  # this test does not apply if v is 1.
                i = 0
                while v != (num - 1):
                    if i == t - 1:
                        return False
                    else:
                        i = i + 1
                        v = (v ** 2) % num
        return True

    def isPrime(self, num):
        # Return True if num is a prime number. This function does a quicker
        # prime number check before calling rabinMiller().

        if num < 2:
            return False  # 0, 1, and negative numbers are not prime

        # About 1/3 of the time we can quickly determine if num is not prime
        # by dividing by the first few dozen prime numbers. This is quicker
        # than rabinMiller(), but unlike rabinMiller() is not guaranteed to
        # prove that a number is prime.
        lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
                     101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197,
                     199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
                     317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439,
                     443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571,
                     577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
                     701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829,
                     839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977,
                     983, 991, 997]

        if num in lowPrimes:
            # print("Correct")
            return True

        # See if any of the low prime numbers can divide num
        for prime in lowPrimes:
            if num % prime == 0:
                # print("false")
                return False

        # If all else fails, call rabinMiller() to determine if num is a prime.
        return self.rabinMiller(num)

    def generate_prime(self):
        prime_gen = random.randrange((2 ** (self.prime - 1)), (2 ** self.prime))
        # print(f"prime_gen: {prime_gen} ")

        while not self.isPrime(prime_gen):
            prime_gen = random.randrange((2 ** (self.prime - 1)), (2 ** self.prime))

        return prime_gen

    # https://www.geeksforgeeks.org/python-program-for-basic-and-extended-euclidean-algorithms-2/
    def gcd(self, e, phi):
        if phi == 0:
            return e
        else:
            return self.gcd(phi, e % phi)

    # https: // stackoverflow.com / questions / 4798654 / modular - multiplicative - inverse - function - in -python
    def egcd(self, a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def modinv(self, a, m):
        g, x, y = self.egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m

    # https://www.youtube.com/watch?v=-0slxSL9B6A
    def Keys_gen(self):
        p, q = self.generate_prime(), self.generate_prime()
        while p == q:
            q = self.generate_prime()
        self.p, self.q = p, q
        n = p * q
        self.n = n
        phi = (p - 1) * (q - 1)  # Euler Totient  fun
        self.phi = phi
        e = random.randrange((2 ** (self.keysize - 1)), (2 ** self.keysize))
        # e - 1<e<Phi
        # e - Najwiekszy wsp dzielnik z Phi to 1 -  liczby sa wzglednie pierwsze
        while self.gcd(e, phi) != 1 and e >= phi:
            e = random.randrange((2 ** (self.keysize - 1)), (2 ** self.keysize))

        self.e = e
        # d - d*e mod phi = 1
        # self.d = self.modinv(self.e, self.phi)

        self.d = pow(self.e, -1, self.phi)
        self.public_key = (self.e, self.n)
        self.private_key = (self.d, self.n)

    def Print_Keys(self):
        print(f"Key Size {self.keysize}")
        print(f"Prime Size {self.prime}")
        print(f" p: {self.p} \n q: {self.q}  \n n: {self.n} \n d: {self.d}")


# key = KeyGen(1024)
#
# print(key.keysize)
# key.Keys_gen()
# key.Print_Keys()


# ograniczenie na długość bloku
class RSA:

    def __init__(self, size, filepath, key=None):

        if key is None:
            # Tworzenie klucza, jeśli nie jest dostarczony
            KEYGEN = KeyGen(size)
            KEYGEN.Keys_gen()
            self.public_keys_info = KEYGEN.public_key
            self.private_keys_info = KEYGEN.private_key
        else:
            # Ustawienie klucza, jeśli jest dostarczony
            self.public_keys_info = None  # Tutaj ustal, jak uzyskać informacje o kluczu publicznym
            self.private_keys_info = key
        self.filepath = filepath
        with open(filepath, 'rb') as file:
            self.file_data = file.read()

        self.metadata, self.Idat, self.recon = read_png_metadata(filepath)

        # zamiana bitów na bajty
        # Blok musi być o n-1 od klucza
        self.block_bytes_size = size // 8 - 1
        # Krypto blok musi być takiej samej długości co klucz
        self.crypto_block_bytes_size = size // 8

    def get_private_keys_info(self):
        return self.private_keys_info

    def ECB_encrypt(self, data):
        crypto_idat = []
        crypto_idat_len = []
        crypto_to_view = []
        added_zeros = []
        self.length_of_original_idat = len(data)

        for i in range(0, self.length_of_original_idat, self.block_bytes_size):
            raw_block = bytes(data[i:i + self.block_bytes_size])

            encryption = pow(int.from_bytes(raw_block, 'big'), self.public_keys_info[0], self.public_keys_info[1])
            encryption_bytes = encryption.to_bytes(self.crypto_block_bytes_size, 'big')

            crypto_idat.append(encryption_bytes)
            crypto_to_view.append(encryption_bytes[:-1])

            crypto_idat_len.extend(encryption_bytes)

            added_zeros.append(encryption_bytes[-1:])

        crypto_idat = b''.join(crypto_idat)
        crypto_to_view = b''.join(crypto_to_view)
        added_zeros = b''.join(added_zeros)

        # print("ECB IDAT" + str(crypto_idat))
        # print("ECB View" + str(crypto_to_view))
        # print("ECB ZEROS" + str(added_zeros))
        print("ECB LEN IDAT" + str(len(crypto_idat)))
        print("ECB LEN View" + str(len(crypto_to_view)))
        print("ECB LEN ZEROS" + str(len(added_zeros)))

        return crypto_idat, crypto_to_view, added_zeros
        # Szyfrujemy licznik dodajemy do niego sól na poczatku a pożniej wykonujemy operacje XOR plaintexta z licznikiem
        # plaintekst moze miec ta sama dlugosc co klucz

    def ECB_decrypt(self, data):

        decrypto_idat = []
        decrypto_bytes = []
        print("key " + str(len(self.private_keys_info)))
        print("key " + str(self.private_keys_info))
        print("crypto_block_bytes_size:", self.crypto_block_bytes_size)
        # data = b''.join(data)
        length_of_crypto_idat = len(data)
        print("length_of_crypto_idat:", length_of_crypto_idat)
        print("length_of_crypto_idat:", self.block_bytes_size)
        # print("DATA:", data)
        # self.length_of_original_idat = len(data)

        print("Orginal  Decrypt", self.length_of_original_idat)
        for i in range(0, length_of_crypto_idat, self.crypto_block_bytes_size):

            raw_block = bytes(data[i:i + self.crypto_block_bytes_size])
            # raw_block = b''.join(data[i:i + self.crypto_block_bytes_size])
            print("RAW",raw_block,"LEN", len(raw_block))

            decryption = pow(int.from_bytes(raw_block, 'big'), self.private_keys_info[0], self.private_keys_info[1])
            # print("EHH " + str(decryption))
            # decryption_bytes = decryption.to_bytes(self.block_bytes_size, 'big')
            # print("LEN DECRIpts",len(decrypto_bytes))
            # print("LEN ORGINAL ",self.length_of_original_idat)
            if len(decrypto_bytes) + self.block_bytes_size >= self.length_of_original_idat:

                print("NIEDOBOR :", self.length_of_original_idat - len(decrypto_bytes))
                # print("Problem " + str(decryption.to_bytes(self.length_of_original_idat - len(decrypto_bytes), 'big')))
                decryption_bytes = decryption.to_bytes(self.length_of_original_idat - len(decrypto_bytes), 'big')
                print("DECRYPTO BYTES ", decryption_bytes)

            else:
                # print("Block " + str(self.block_bytes_size))
                decryption_bytes = decryption.to_bytes(self.block_bytes_size, 'big')

            decrypto_bytes.extend(decryption_bytes)
            # print("I:", i)
            decrypto_idat.append(decryption_bytes)

        decrypto_idat = b''.join(decrypto_idat)
        # print("DECRYpto", decrypto_idat)

        return decrypto_idat

    def ECB_library(self, data):
        # 16 bajtów = 128 bit
        key_lib = os.urandom(16)
        key_length_bytes = len(key_lib)
        key_length_bits = key_length_bytes * 8
        print("key_lib   ", key_length_bits, rsa.size)
        aes_ecb_cipher = Cipher(AES(key_lib), ECB())
        encryptor = aes_ecb_cipher.encryptor()

        return encryptor.update(data)

    def Save_Png_Idat_lenght(self, data_to_view, added_mis_block):
        print("data_to_view", len(data_to_view))
        print("Orginal ", self.length_of_original_idat)
        print("data_to_view", data_to_view)

        idat = []
        missing_idat = []
        for i in range(self.length_of_original_idat):

                idat.append(data_to_view[i])


        missing_idat = data_to_view[self.length_of_original_idat:]
        missing_idat += b"SE"
        missing_idat += added_mis_block[0:]
        # print(missing_idat)
        print("len of missing ", len(missing_idat))

        idat_bytes = bytes(idat)
        print("len of idat ", len(idat_bytes))
        # print(idat_bytes)
        return idat_bytes, missing_idat

    def read_data_after_iend(self):
        self.length_of_original_idat = len(self.recon)
        print("Original LEN POWINNO BYC  " + str(len(self.recon)))
        IEND_SIGNATURE = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'

        with open(self.filepath, 'rb') as file:
            data = file.read()

        iend_pos = data.find(IEND_SIGNATURE)
        if iend_pos == -1:
            print("Blok IEND nie znaleziony w pliku")
            return None


        data_after_iend = data[iend_pos + len(IEND_SIGNATURE):]



        reconstructed_data = []
        data_after_separator = []
        final = []


        iend_index = 0



        found_separator = False
        for i, byte in enumerate(data_after_iend):
            if not found_separator:
                if byte == 83 and i < len(data_after_iend) - 1 and data_after_iend[i + 1] == 69:
                    data_after_separator.append(byte)
                    data_after_separator.append(69)
                    found_separator = True
                    print("witam")
                else:
                    print("cie")
                    reconstructed_data.append(byte)
            else:
                data_after_separator.append(byte)

        data_after_separator=bytes(data_after_separator)
        print(bytes(data_after_separator[0:2]))
        data_after_separator = data_after_separator[3:]
        print(bytes(data_after_separator[0:2]))

        print("data_after_iend  ", bytes(data_after_iend))
        print("reconstructed_data  ", bytes(reconstructed_data))
        print("separator " ,data_after_separator)

        iend_length = len(data_after_separator)

        self.recon += reconstructed_data


        for i in range(0, len(self.recon), self.block_bytes_size):
            # Get the next block of IDAT data
            block = self.recon[i:i + self.block_bytes_size]
            final.extend(block)


            if iend_index < iend_length:

                final.append(data_after_separator[iend_index])
                iend_index += 1


        if iend_index < iend_length:

            final.extend(data_after_separator[iend_index:])


        self.reconstructed_data = bytes(final)



        return self.reconstructed_data



    def CTR_encrypt(self, data):
        self.salt = random.getrandbits(self.size // 2)
        print('salt: ' + str(self.salt))
        self.salt_bytes = self.salt.to_bytes((self.size // 2 + 7) // 8, byteorder='big')

        self.length_of_original_idat = len(data)

        crypto_idat = []
        crypto_idat_len = []

        counter = 0

        for i in range(0, self.length_of_original_idat, self.crypto_block_bytes_size):
            counter_bytes = counter.to_bytes((self.size // 2 + 7) // 8, byteorder='big')
            IV = self.salt_bytes + counter_bytes
            # print("IV " + str(IV))
            # print("IV " + str(len(IV)))

            plaintext_block = bytes(data[i:i + self.crypto_block_bytes_size])

            encryption = pow(int.from_bytes(IV, 'big'), self.public_keys_info[0], self.public_keys_info[1])

            ciphertext_block = int.from_bytes(plaintext_block, 'big') ^ encryption

            encryption_bytes = ciphertext_block.to_bytes(self.crypto_block_bytes_size, 'big')
            # print("ciphertext" + str(encryption_bytes))
            # print("cipher ken " + str(len(encryption_bytes)))
            crypto_idat.append(encryption_bytes)
            crypto_idat_len.extend(encryption_bytes)

            counter += 1

            # print(len(crypto_idat))

            if len(crypto_idat_len) + self.crypto_block_bytes_size >= self.length_of_original_idat:
                print("Cryptographic")
                print(len(crypto_idat_len))
                print(self.length_of_original_idat)
                print(self.crypto_block_bytes_size)
            # crypto_idat_len.extend(encryption_bytes)

        crypto_idat = b''.join(crypto_idat)
        # print(len(crypto_idat))
        # Dodajemy asercję sprawdzającą rozmiar bloku
        # assert len(crypto_idat) == self.length_of_original_idat, "Encrypted data length mismatch"

        return crypto_idat

    def CTR_decrypt(self, data):

        # data to zakryptowane w bajtach
        decrypto_idat = []
        decrypto_bytes = []
        # print('salt: ' + str(self.salt))
        counter = 0

        length_of_crypto_idat = len(data)
        # print("Crypto Data " + str(length_of_crypto_idat))
        # print('Orginal: ' + str(self.length_of_original_idat))
        # print('crypto block : ' + str(self.crypto_block_bytes_size))

        for i in range(0, length_of_crypto_idat, self.crypto_block_bytes_size):
            counter_bytes = counter.to_bytes((self.size // 2 + 7) // 8, byteorder='big')
            IV = self.salt_bytes + counter_bytes
            # print("IV " + str(IV))
            # print("IV " + str(len(IV)))
            ciphertext_block = bytes(data[i:i + self.crypto_block_bytes_size])
            # print("ciphertext" + str(ciphertext_block))
            # print("cipher ken " + str(len(ciphertext_block)))

            # decryption = pow(int.from_bytes(IV, 'big'), self.private_keys_info[0], self.private_keys_info[1])
            decryption = pow(int.from_bytes(IV, 'big'), self.public_keys_info[0], self.public_keys_info[1])

            plaintex_block = int.from_bytes(ciphertext_block, 'big') ^ decryption
            # plaintex_block = decryption ^ int.from_bytes(ciphertext_block, 'big')

            if len(decrypto_bytes) + self.crypto_block_bytes_size >= self.length_of_original_idat:
                print("NIEDOBOR :", self.length_of_original_idat - len(decrypto_bytes))
                dencryption_bytes = plaintex_block.to_bytes(self.length_of_original_idat - len(decrypto_bytes), 'big')


            else:

                dencryption_bytes = plaintex_block.to_bytes(self.crypto_block_bytes_size, 'big')

            # print('decrypto block petla : ' + str(len(dencryption_bytes)))
            # print('decrypto block  : ' + str(dencryption_bytes))
            decrypto_bytes.extend(dencryption_bytes)
            # print("dec ext" + str(decrypto_bytes))
            decrypto_idat.append(dencryption_bytes)

            counter += 1

        decrypto_idat = b''.join(decrypto_idat)

        return decrypto_idat

#------------File Path-------------------
#file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\basn6a08.png"
#file_crypto = r"C:\Users\PRO\PycharmProjects\emedia-png\cryptop.png"
#file_crypto_decrypt = r"C:\Users\PRO\PycharmProjects\emedia-png\crypto2.png"
# file_path = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\2x2.png"
# file_crypto = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\crypto.png"

# key_lib = RSAA.construct(rsa.public_keys_info,rsa.private_keys_info)
#----------------------------------------





#----------Test CTR------------
# tekst = "SiemaEniuDobryZa1616161616161616"
# tekst = bytes(tekst, 'utf-8')

# T ,t= rsa.ECB_encrypt(tekst)
# print(T)
# TE = rsa.ECB_decrypt(T)
# print(TE)
#
# print("Tekst W bajtach",tekst)
# #
#
# C = rsa.CTR_encrypt(tekst)
# print(C)
# print(" ")

# CE = rsa.CTR_decrypt(C)
# print(CE)
#---------------------------------





#
# -------------------CTR--------------------------
# CTR = rsa.CTR_encrypt(recon)
# imageCTR = Image.frombytes('RGB',siz, CTR)
# plt.imshow(imageCTR)
# plt.show()
# idata = rsa.Save_Png_Idat_lenght(CTR)
# pixels_grouped_by_rows = [idata[i: i + bytes_row_width] for i in range(0, len(idata), bytes_row_width)]
# f = open(file_crypto, 'wb')
# png_write.write(f, pixels_grouped_by_rows)

# f.close()
# plt.clf()
# idata = rsa.Save_Png_Idat_lenght(CTR)
# pixels_grouped_by_rows = [idata[i: i + bytes_row_width] for i in range(0, len(idata), bytes_row_width)]
# f = open(file_crypto, 'wb')
# png_write.write(f, pixels_grouped_by_rows)
#
# f.close()
# #
# DCTR = rsa.CTR_decrypt(CTR)
# print("Decode CTR ",DCTR)
# imageDCTR = Image.frombytes('RGB',siz, DCTR)
# plt.imshow(imageDCTR)
# plt.show()

#
#
#
# encode_lib = rsa.ECB_library(recon)
#
#
# image = Image.frombytes('RGBA', siz, encode_lib)
# plt.imshow(image)
# plt.show()
# ------------------------------------------




#-----------Test ECB--------------------------
file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\basn6a08.png"
file_crypto = r"C:\Users\PRO\PycharmProjects\emedia-png\cryptop.png"
file_crypto_decrypt = r"C:\Users\PRO\PycharmProjects\emedia-png\decrypto.png"
# file_path = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\2x2.png"
# file_crypto = r"C:\Users\Jakub\Desktop\EMEDIA\emedia-png\pngs\crypto.png"

rsa = RSA(256, file_path)
recon = rsa.recon


byte_per_pix = calculate_bytes_per_pixel(rsa.metadata)
if byte_per_pix == 1:
    byte_per_pix = 3
print("Byte per pixel ", byte_per_pix)
print("colour type", rsa.metadata['IHDR']['color_type'])
print("Bit depth", rsa.metadata['IHDR']['bit_depth'])

png_write = png.Writer(rsa.metadata['IHDR']['width'], rsa.metadata['IHDR']['height'], greyscale=False, alpha=True)

bytes_row_width = rsa.metadata['IHDR']['width'] * byte_per_pix

plt.clf()

recon = bytes(recon)
siz = (rsa.metadata['IHDR']['width'], rsa.metadata['IHDR']['height'])
encodedata, enc_to_view, zeros = rsa.ECB_encrypt(recon)

imageECB = Image.frombytes('RGBA', siz, enc_to_view)
plt.imshow(imageECB)
plt.title("Encrypted Image")
plt.show()

idata, missing_idat = rsa.Save_Png_Idat_lenght(enc_to_view, zeros)

pixels_grouped_by_rows = [idata[i: i + bytes_row_width] for i in range(0, len(idata), bytes_row_width)]
f = open(file_crypto, 'wb')
png_write.write(f, pixels_grouped_by_rows)
f.write(missing_idat)

f.close()


decodedata = rsa.ECB_decrypt(encodedata)

decrypted_image = Image.frombytes('RGBA', siz, decodedata)
plt.imshow(decrypted_image)
plt.title("Decrypted Image")
plt.show()
print(" ")
#key = (32995941556654902429246324207303379571, 188728535301618933720544776724056167321)
decrypt = RSA(256, file_crypto, rsa.get_private_keys_info())


png_write_dec = png.Writer(rsa.metadata['IHDR']['width'], rsa.metadata['IHDR']['height'], greyscale=False, alpha=True)

bytes_row_width_dec = rsa.metadata['IHDR']['width'] * byte_per_pix

decodedata_to_decrytp = decrypt.read_data_after_iend()

# print("DO DECODE " + str(decodedata_to_decrytp))
decodedata1 = decrypt.ECB_decrypt(decodedata_to_decrytp)

pixels_grouped_by_rows = [decodedata1[i: i + bytes_row_width] for i in range(0, len(decodedata1), bytes_row_width)]
f = open(file_crypto_decrypt, 'wb')
png_write.write(f, pixels_grouped_by_rows)

f.close()

# decodedata = rsa.ECB_decrypt(encodedata)
decrypted_image1 = Image.frombytes('RGBA', siz, decodedata1)
plt.clf()
plt.imshow(decrypted_image1)
plt.title("Decrypted Image from File")
plt.show()
#----------------------------------------