# check_continuity.py
import numpy as np
import sys
from math import atan2, pi

def read_complex_tail_head(f1, f2, n=200000):
    # читаем последние n комплексных сэмплов из f1 и первые n из f2
    dtype = np.int8  # assuming -b 8 output
    with open(f1,'rb') as a:
        a.seek(0,2)
        size = a.tell()
        bytes_needed = n*2
        a.seek(max(0, size-bytes_needed))
        d1 = np.fromfile(a, dtype=dtype)
    with open(f2,'rb') as b:
        d2 = np.fromfile(b, dtype=dtype, count=bytes_needed)
    if len(d1)%2 != 0: d1 = d1[:-1]
    if len(d2)%2 != 0: d2 = d2[:-1]
    c1 = d1.reshape(-1,2).astype(np.float32).view(np.complex64)[:,0]
    c1 = d1.reshape(-1,2)[:,0] + 1j*d1.reshape(-1,2)[:,1]
    c2 = d2.reshape(-1,2)[:,0] + 1j*d2.reshape(-1,2)[:,1]
    return c1, c2

def phase_diff(c1, c2):
    # возьмём last K из c1 и first K из c2, усредним
    K = min(len(c1), len(c2), 100000)
    a = c1[-K:]
    b = c2[:K]
    # remove DC by normalizing amplitude
    a /= np.abs(a)+1e-12
    b /= np.abs(b)+1e-12
    prod = np.conj(a) * b
    angles = np.angle(prod)
    mean = np.angle(np.sum(np.exp(1j*angles)))
    return mean, np.std(angles)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python check_continuity.py seg1.bin seg2.bin")
        sys.exit(1)
    c1, c2 = read_complex_tail_head(sys.argv[1], sys.argv[2], n=200000)
    mean, std = phase_diff(c1, c2)
    print(f"Mean phase difference (rad): {mean:.6f}, std: {std:.6f}")
    print(f"Mean (deg): {mean*180.0/np.pi:.3f}")
