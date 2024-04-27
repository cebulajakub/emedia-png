import random
import math


class KeyGen:
    def __init__(self, keysize):
        self.keysize = keysize
        self.prime = keysize / 2

        self.phi = 0
        self.n = 0
        self.e = 0
        self.d = 0

    # https://inventwithpython.com/rabinMiller.py
    def rabinMiller(self, num):
        # Returns True if num is a prime number.

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
            return True

        # See if any of the low prime numbers can divide num
        for prime in lowPrimes:
            if num % prime == 0:
                return False

        # If all else fails, call rabinMiller() to determine if num is a prime.
        return self.rabinMiller(num)

    def generate_prime(self):
        prime_gen = random.randrange(int(2 ** (self.prime - 1)), int(2 ** self.prime))
        print(f"prime_gen: {prime_gen} ")

        while not self.isPrime(prime_gen):
            prime_gen = random.randrange(int(2 ** (self.prime - 1)), int(2 ** self.prime))

        return prime_gen

    # Python program to demonstrate working of extended
    # Euclidean Algorithm
    # https://www.geeksforgeeks.org/python-program-for-basic-and-extended-euclidean-algorithms-2/
    # function for extended Euclidean Algorithm
    def gcdExtended(self, a, b):
        # Base Case
        if a == 0:
            return b, 0, 1

        gcd, x1, y1 = self.gcdExtended(b % a, a)

        # Update x and y using results of recursive
        # call
        x = y1 - (b // a) * x1
        y = x1

        return gcd, x, y

    def gcd(self, e, phi):
        if phi == 0:
            return e
        else:
            return self.gcd(phi, e % phi)

    def Keys_gen(self):
        p, q = self.generate_prime(), self.generate_prime()
        while p == q:
            q = self.generate_prime()
        print(q)
        n = p * q
        self.n = n
        phi = (p - 1) * (q - 1)
        self.phi = phi

    ''''''''''
    def Public_Private_gen(self, min_val, max_val):
        p, q = self.generate_prime(min_val, max_val), self.generate_prime(min_val, max_val)

        while p == q:
            q = self.generate_prime(min_val, max_val)

        n = p * q
        phi = (p - 1) * (q - 1)

        e = random.randint(3, phi - 1)
        while self.gcd(e, phi) != 1:
            e = random.randint(3, phi - 1)

        return p, q, n, phi, e
    '''''''''''




key = KeyGen(1024)

print(key.keysize)
key.Keys_gen()
