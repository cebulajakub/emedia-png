import random
import math





class KeyGen:
    def __init__(self, keysize):
        self.keysize = keysize
        self.prime = keysize / 2
        self.n = 0
        self.e = 0
        self.d = 0

    # https://inventwithpython.com/rabinMiller.py
    def is_prime(self, num):
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

    def generate_prime(self):
        prime_gen = random.randrange(2 ** (self.prime - 1), 2 ** (self.prime))
        while not self.is_prime(prime_gen):
            prime = random.randrange(2 ** (self.prime - 1), 2 ** (self.prime))

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
    ''''''''''''