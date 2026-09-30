import time
import multiprocessing as mp
import json

def hitung_blok(rentang):
    start, end = rentang
    return sum(i * i for i in range(start, end))

def hitung_serial(BEBAN):
    t0 = time.perf_counter()
    hasil_serial = hitung_blok((0, BEBAN))
    t_serial = time.perf_counter() - t0
    return hasil_serial, t_serial

def run_multiprocess(BEBAN, BAGIAN, hasil_serial_ref=None):
    ukuran_blok = BEBAN // BAGIAN
    tugas = [(i * ukuran_blok, (i + 1) * ukuran_blok) for i in range(BAGIAN)]
    # sisa pembagian (jika BEBAN tidak habis dibagi BAGIAN) dimasukkan ke blok terakhir
    if tugas[-1][1] != BEBAN:
        tugas[-1] = (tugas[-1][0], BEBAN)

    t0 = time.perf_counter()
    with mp.Pool(BAGIAN) as pool:
        hasil_per_blok = pool.map(hitung_blok, tugas)
        hasil_paralel = sum(hasil_per_blok)
    t_paralel = time.perf_counter() - t0

    cocok = (hasil_serial_ref is None) or (hasil_paralel == hasil_serial_ref)
    return hasil_paralel, t_paralel, cocok

if __name__ == '__main__':
    BEBAN = 100_000_000
    daftar_bagian = [2, 4, 8, 10, 16]

    print(f'BEBAN = {BEBAN:,}')
    print('Menghitung baseline serial ...')
    hasil_serial, t_serial = hitung_serial(BEBAN)
    print(f'Hasil Serial   : {hasil_serial}')
    print(f'Waktu Serial   : {t_serial:.4f} s\n')

    hasil_lengkap = {'BEBAN': BEBAN, 't_serial': t_serial, 'per_bagian': []}

    for BAGIAN in daftar_bagian:
        hasil_paralel, t_paralel, cocok = run_multiprocess(BEBAN, BAGIAN, hasil_serial)
        speedup = t_serial / t_paralel
        efisiensi = speedup / BAGIAN
        print(f'BAGIAN={BAGIAN:>2} | t_paralel={t_paralel:.4f}s | '
              f'Speedup={speedup:.3f} | Efisiensi={efisiensi:.3f} | Hasil sama? {cocok}')
        hasil_lengkap['per_bagian'].append({
            'BAGIAN': BAGIAN,
            't_paralel': t_paralel,
            'speedup': speedup,
            'efisiensi': efisiensi,
            'cocok': cocok,
        })

    with open('hasil_multiprocess.json', 'w') as f:
        json.dump(hasil_lengkap, f, indent=2)