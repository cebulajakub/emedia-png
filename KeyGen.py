import random
import math
import zlib

from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

from metadata import read_png_metadata, read_IDAT_chunk


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
        #print("Miller")
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
                #print("false")
                return False

        # If all else fails, call rabinMiller() to determine if num is a prime.
        return self.rabinMiller(num)

    def generate_prime(self):
        prime_gen = random.randrange((2 ** (self.prime - 1)), (2 ** self.prime))
        #print(f"prime_gen: {prime_gen} ")

        while not self.isPrime(prime_gen):
            prime_gen = random.randrange((2 ** (self.prime - 1)), (2 ** self.prime))

        return prime_gen



    # https://www.geeksforgeeks.org/python-program-for-basic-and-extended-euclidean-algorithms-2/
    def gcd(self, e, phi):
        if phi == 0:
            return e
        else:
            return self.gcd(phi, e % phi)

    #https: // stackoverflow.com / questions / 4798654 / modular - multiplicative - inverse - function - in -python
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


#https://www.youtube.com/watch?v=-0slxSL9B6A
    def Keys_gen(self):
        p, q = self.generate_prime(), self.generate_prime()
        while p == q:
            q = self.generate_prime()
        self.p, self.q = p, q
        n = p * q
        self.n = n
        phi = (p - 1) * (q - 1) # Euler Totient  fun
        self.phi = phi
        e = random.randrange((2 ** (self.keysize - 1)), (2 ** self.keysize))
        # e - 1<e<Phi
        # e - Najwiekszy wsp dzielnik z Phi to 1 -  liczby sa wzglednie pierwsze
        while self.gcd(e, phi) != 1 and e >= phi:
            e = random.randrange((2 ** (self.keysize - 1)), (2 ** self.keysize))

        self.e = e
        # d - d*e mod phi = 1
        #self.d = self.modinv(self.e, self.phi)

        self.d = pow(self.e, -1, self.phi)
        self.public_key = (self.e, self.n)
        self.private_key = (self.d, self.n)


    def Print_Keys(self):
        print(f"Key Size {self.keysize}")
        print(f"Prime Size {self.prime}")
        print(f" p: {self.p} \n q: {self.q}  \n n: {self.n} \n d: {self.d}")




#key = KeyGen(1024)

#print(key.keysize)
#key.Keys_gen()
#key.Print_Keys()
#amount_of_bytes_to_substract_from_chunk_size = 1
#encrypted_chunk_size_in_bytes_substracted = key.keysize // 8 - amount_of_bytes_to_substract_from_chunk_size
#print(f"encrypted_chunk_size_in_bytes_substracted{encrypted_chunk_size_in_bytes_substracted}  Klucz W BAJTACH = {key.keysize // 8}")

'''
    def Electronic_Code_Book_encrypt(self):
        crypto_idat = []
        crypto_junk =[]
        decompress_idat = zlib.decompress(self.Idat)
        # Czy zdekompresowane czy nie
        length_of_original_idat = len(decompress_idat)
        print("length_of_original_idat:",length_of_original_idat)
        print("block_bytes_size:", self.block_bytes_size)
        print("crypto_block_bytes_size",self.crypto_block_bytes_size)
        for i in range(0, length_of_original_idat, self.block_bytes_size):


            raw_block = bytes(decompress_idat[i:i + self.block_bytes_size])

            #Liczba^e mod n
            encryption = pow(int.from_bytes(raw_block, 'big'), self.public_keys_info[0], self.public_keys_info[1])
            encryption_bytes = encryption.to_bytes(self.crypto_block_bytes_size, 'big')
            print("encryption_bytes:",encryption_bytes)
            #osatni ne przechowuje informacji tylko jest zgodny z kluczem
            crypto_idat.append(encryption_bytes[:-1])
            crypto_junk.append(encryption_bytes[-1])

            #crypto_idat.append(encryption_bytes)


        return crypto_idat
        
    def create_encrypted_image(self, encrypted_data, output_path):
        try:
            with open(self.filepath, 'rb') as file:
                # Odczytaj nagłówek PNG
                png_header = file.read(8)

                # Odczytaj chunk IHDR
                ihdr_chunk_length_bytes = file.read(4)
                ihdr_chunk_length = int.from_bytes(ihdr_chunk_length_bytes, byteorder='big')
                ihdr_chunk = ihdr_chunk_length_bytes + file.read(ihdr_chunk_length + 8)

                # Odczytaj pozostałe chunki metadanych (z wyjątkiem IDAT i IEND)
                other_chunks = b''
                while True:
                    length_bytes = file.read(4)
                    if not length_bytes:
                        break

                    chunk_length = int.from_bytes(length_bytes, byteorder='big')
                    chunk_type = file.read(4)
                    chunk_data = file.read(chunk_length)
                    crc = file.read(4)

                    if chunk_type not in [b'IDAT', b'IEND']:  # Pomijamy IDAT i IEND
                        other_chunks += length_bytes + chunk_type + chunk_data + crc

                # Otwórz nowy plik PNG w trybie zapisu binarnego
                with open(output_path, 'wb') as ofile:
                    # Zapisz nagłówek PNG
                    ofile.write(png_header)

                    # Zapisz chunk IHDR
                    ofile.write(ihdr_chunk)

                    # Zapisz pozostałe chunki metadanych
                    ofile.write(other_chunks)

                    # Zapisz chunk IDAT
                    idat_length = sum(len(block) for block in encrypted_data)
                    ofile.write(idat_length.to_bytes(4, byteorder='big'))  # Długość IDAT
                    ofile.write(b'IDAT')  # Typ chunku
                    for encrypted_block in encrypted_data:
                        ofile.write(encrypted_block)  # Zaszyfrowane dane

                    # Oblicz i zapisz CRC dla chunku IDAT
                    crc_data = b'IDAT' + b''.join(encrypted_data)
                    crc32_idat = zlib.crc32(crc_data).to_bytes(4, byteorder='big')
                    ofile.write(crc32_idat)

                    # Dodaj chunk IEND na koniec pliku
                    ofile.write(b'\x00\x00\x00\x00IEND\xaeB`\x82')

        except Exception as e:
            print("Błąd podczas tworzenia zaszyfrowanego obrazka PNG:", e)
        
        
        
        '''

""""
    def ECB_decrypt(self,data):
        crypto_idat = data
        decrypto_idat =[]
        crypto_junk =[]
        #decompress_idat = zlib.decompress(self.Idat)
        # Czy zdekompresowane czy nie
        length_of_crypto_idat = len(data)
        print("length_of_crypto_idat:",length_of_crypto_idat)
        print("block_bytes_size:", self.block_bytes_size)
        print("crypto_block_bytes_size",self.crypto_block_bytes_size)
        for i in range(0, length_of_crypto_idat, self.crypto_block_bytes_size):


            raw_block = bytes(data[i:i + self.crypto_block_bytes_size])

            #Liczba^e mod n
            decryption = pow(int.from_bytes(raw_block, 'big'), self.private_keys_info[0], self.private_keys_info[1])
            decryption_bytes = decryption.to_bytes(self.crypto_block_bytes_size, 'big')

            if len(decrypto_idat) + self.block_bytes_size > self.length_of_original_idat:
                decryption_length = self.length_of_original_idat - len(decrypto_idat)
            else:
                decryption_length = self.block_bytes_size

            decryption_bytes = decryption.to_bytes(decryption_length, 'big')

            for bytes in decryption_bytes:
                decrypto_idat.append(bytes)
            #print("encryption_bytes:",decryption_bytes)
            #osatni ne przechowuje informacji tylko jest zgodny z kluczem
            #crypto_idat.append(encryption_bytes[:-1])
            #crypto_junk.append(encryption_bytes[-1])




        return decrypto_idat"
    """""




class RSA:

    def __init__(self, size, filepath):
        KEYGEN = KeyGen(size)
        KEYGEN.Keys_gen()
        self.public_keys_info = KEYGEN.public_key
        self.private_keys_info = KEYGEN.private_key
        self.filepath = filepath

        with open(filepath, 'rb') as file:
            self.file_data = file.read()

        self.metadata, self.Idat, self.recon = read_png_metadata(filepath)


        # Blok musi być o n-1 od klucza
        self.block_bytes_size = size // 8 - 1
        # Krypto blok musi być takiej samej długości co klucz
        self.crypto_block_bytes_size = size // 8

    def ECB_encrypt(self,data):
        first_byte = data[:1]
        data = data[1:]#pierwszy bajt to filtracja
        crypto_idat = []
        crypto_idat_len=[]
        crypto_junk =[]
        #decompress_idat = zlib.decompress(self.Idat)
        #data = zlib.decompress(data)
        # Czy zdekompresowane czy nie
        self.length_of_original_idat = len(data)
        #print("Orginal DATA:", data)
        #print("Orginal DATA DECopmress:", data)
        #print("length_of_original_idat:",self.length_of_original_idat)
        #print("block_bytes_size:", self.block_bytes_size)
        ##print("crypto_block_bytes_size",self.crypto_block_bytes_size)

        for i in range(0, self.length_of_original_idat, self.block_bytes_size):

            #print("PRZED SZYFR: ", data[i:i + self.block_bytes_size])
            raw_block = bytes(data[i:i + self.block_bytes_size])

            #Liczba^e mod n
            encryption = pow(int.from_bytes(raw_block, 'big'), self.public_keys_info[0], self.public_keys_info[1])
            encryption_bytes = encryption.to_bytes(self.crypto_block_bytes_size, 'big')
            #print("encryption_bytes:",encryption_bytes)
            #osatni ne przechowuje informacji tylko jest zgodny z kluczem
            #crypto_idat.append(encryption_bytes[:-1])
            #crypto_junk.append(encryption_bytes[-1])

            crypto_idat.append(encryption_bytes)
            crypto_idat_len.extend(encryption_bytes)
        #print("crypto_idat:",crypto_idat)
        #print("Cripto len",len(crypto_idat_len))
        crypto_idat = b''.join(crypto_idat)
        crypto_idat = int.from_bytes(crypto_idat, 'big'),

        return crypto_idat

    def ECB_decrypt(self, data):

        decrypto_idat = []
        decrypto_bytes = []
        #print("crypto_block_bytes_size:", self.crypto_block_bytes_size)
        #data = b''.join(data)
        length_of_crypto_idat = len(data)
        #print("length_of_crypto_idat:", length_of_crypto_idat)
        #print("DATA:", data)
        for i in range(0, length_of_crypto_idat, self.crypto_block_bytes_size):
            raw_block = bytes(data[i:i + self.crypto_block_bytes_size])
            #raw_block = b''.join(data[i:i + self.crypto_block_bytes_size])
            #print("RAW",raw_block,"LEN", len(raw_block))

            decryption = pow(int.from_bytes(raw_block, 'big'), self.private_keys_info[0], self.private_keys_info[1])
            #decryption_bytes = decryption.to_bytes(self.block_bytes_size, 'big')
            #print("LEN DECRIpts",len(decrypto_bytes))
            #print("LEN ORGINAL ",self.length_of_original_idat)
            if len(decrypto_bytes) +self.block_bytes_size >= self.length_of_original_idat:
              # print("NIEDOBOR :",self.length_of_original_idat-len(decrypto_bytes))
               decryption_bytes = decryption.to_bytes(self.length_of_original_idat-len(decrypto_bytes), 'big')

            else:
                decryption_bytes = decryption.to_bytes(self.block_bytes_size, 'big')


            decrypto_bytes.extend(decryption_bytes)
           # print("I:", i)
            decrypto_idat.append(decryption_bytes)

        decrypto_idat = b''.join(decrypto_idat)
        print("DECRYpto", decrypto_idat)

        return decrypto_idat





file_path = r"C:\Users\PRO\PycharmProjects\emedia-png\pngs\basn6a08.png"
file_crypto = r"C:\Users\PRO\PycharmProjects\emedia-png\crypto.png"
rsa = RSA(1024, file_path)
data = rsa.Idat
recon = rsa.recon
print("Orginal :", recon)
encodedata = rsa.ECB_encrypt(recon)

#print(f"Image size: {image.size}")
#print(f"Image Mode:{image.mode}")
print("Encoded :", encodedata)
image_array = np.array(encodedata).reshape((rsa.metadata['IHDR']['height'], rsa.metadata['IHDR']['width'], 3))

plt.imshow(image_array)
plt.show()
#decodedata = rsa.ECB_decrypt(encodedata)
#decrypted_image = Image.frombytes('RGB', image.size, decodedata)
#plt.imshow(decrypted_image)
#plt.show()


#print("moja",zlib.decompress(data))
''''
image = Image.open(file_path)
#print("moja idat",data)
print("Tryb kolorów:", image.mode)
#encodedata = rsa.ECB_encrypt(zlib.decompress(data))
encodedata = rsa.ECB_encrypt(data)
encrypted_image_path = "zaszyfrowany_obraz.png"
#read_IDAT_chunk(encodedata,rsa.metadata)
encrypted_image = Image.frombytes(image.mode, image.size, encodedata)
encrypted_image.save(encrypted_image_path)
decodedata = rsa.ECB_decrypt(encodedata)
decrypted_image_path = "odszyfrowany_obraz.png"
decrypted_image = Image.frombytes(image.mode, image.size, decodedata)
decrypted_image.save(decrypted_image_path)
'''

'''''
image = Image.open(file_path)
print("Tryb kolorów:", image.mode)
pixel_data = image.tobytes()
encrypted_pixels = rsa.ECB_encrypt(pixel_data)
#print("PIxwele  ", pixel_data)
encrypted_image = Image.frombytes('RGB', image.size, encrypted_pixels)
encrypted_image.show()
decrypted_pixels = rsa.ECB_decrypt(encrypted_pixels)
decrypted_image = Image.frombytes(image.mode, image.size, decrypted_pixels)
decrypted_image.show()
'''''
#image = Image.frombytes('RGBA', (width, height), data)
#image.show()
#zlibdata = zlib.compress(decodedata)
#print("Zlib Compressed", zlibdata)
#crypto_data = rsa.Electronic_Code_Book_encrypt()
#key_str = str(rsa.public_keys_info[0])
#print("key lenght",len(key_str))




#rsa.create_encrypted_image(crypto_data, file_crypto)
#text = b'WitamJaksiemASZasdwasdwadsawdsadawdaergaergeargfadbv'
#encode = rsa.ECB_encrypt(text)
#decode = rsa.ECB_decrypt(encode)

#print(zlib)# w bytes

#print(rsa.block_bytes_size)
