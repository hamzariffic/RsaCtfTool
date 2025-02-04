#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from attacks.abstract_attack import AbstractAttack
from tqdm import tqdm
from lib.keys_wrapper import PrivateKey
from lib.number_theory import log, gcd, isqrt, primes, powmod


def pollard_P_1(n, progress=True):
    """Pollard P1 implementation"""
    z = []
    logn = log(isqrt(n))
    prime = primes(997)

    for j in range(0, len(prime)):
        primej = prime[j]
        logp = log(primej)
        z.extend(primej for _ in range(1, int(logn / logp) + 1))

    for pp in tqdm(prime, disable=(not progress)):
        for i in range(0, len(z)):
            pp = powmod(pp, z[i], n)
            p = gcd(n, pp - 1)
            if n > p > 1:
                return p, n // p


class Attack(AbstractAttack):
    def __init__(self, timeout=60):
        super().__init__(timeout)
        self.speed = AbstractAttack.speed_enum["medium"]

    def attack(self, publickey, cipher=[], progress=True):
        """Run attack with Pollard P1"""
        if not hasattr(publickey, "p"):
            publickey.p = None
        if not hasattr(publickey, "q"):
            publickey.q = None

        # Pollard P-1 attack
        poll_res = pollard_P_1(publickey.n, progress)
        if poll_res and len(poll_res) > 1:
            publickey.p, publickey.q = poll_res

        if publickey.q is not None:
            priv_key = PrivateKey(
                int(publickey.p),
                int(publickey.q),
                int(publickey.e),
                int(publickey.n),
            )
            return priv_key, None

        return None, None

    def test(self):
        from lib.keys_wrapper import PublicKey

        key_data = """-----BEGIN PUBLIC KEY-----
MBswDQYJKoZIhvcNAQEBBQADCgAwBwICCg0CAQc=
-----END PUBLIC KEY-----"""
        result = self.attack(PublicKey(key_data), progress=False)
        return result != (None, None)
