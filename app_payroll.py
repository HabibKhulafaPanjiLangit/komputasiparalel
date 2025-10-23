"""
Web Application untuk Sistem Penggajian Karyawan
Mendukung: Input Data, Perhitungan Serial/Parallel, CSV, dan Grafik
Akses di: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_file  # type: ignore
import subprocess
import time
import csv
import os
import io
import base64
from datetime import datetime
import threading
import random

app = Flask(__name__)

# Data global
data_karyawan = []
data_absen = []
data_gaji = []
serial_times = []
parallel_times = []
jumlah_data = []

# Lock untuk thread safety
data_lock = threading.Lock()

@app.route('/')
def index():
    """Halaman utama"""
    return render_template('payroll.html')

# ==================== KARYAWAN ====================
@app.route('/api/karyawan', methods=['GET'])
def get_karyawan():
    """Ambil semua data karyawan"""
    with data_lock:
        return jsonify(data_karyawan)

@app.route('/api/karyawan', methods=['POST'])
def add_karyawan():
    """Tambah karyawan baru"""
    try:
        data = request.get_json()
        with data_lock:
            data_karyawan.append(data)
        return jsonify({'success': True, 'message': 'Karyawan berhasil ditambahkan'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/karyawan/generate', methods=['POST'])
def generate_karyawan():
    """Generate karyawan otomatis untuk testing"""
    try:
        data = request.get_json()
        jumlah = data.get('jumlah', 100)
        
        jabatan_list = ["Manager", "Staff", "Supervisor", "Admin", "Developer"]
        nama_list = ["Andi", "Budi", "Citra", "Dewi", "Eko", "Fitri", "Gani", "Hana", "Indra", "Joko"]
        
        with data_lock:
            data_karyawan.clear()
            for i in range(jumlah):
                data_karyawan.append({
                    "id": f"K{i+1:04d}",
                    "nama": f"{random.choice(nama_list)} {i+1}",
                    "jabatan": random.choice(jabatan_list),
                    "gaji_pokok": 150000 + (i % 5) * 50000
                })
        
        return jsonify({'success': True, 'message': f'{jumlah} karyawan berhasil dibuat'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/karyawan/clear', methods=['POST'])
def clear_karyawan():
    """Hapus semua data karyawan"""
    with data_lock:
        data_karyawan.clear()
        data_absen.clear()
        data_gaji.clear()
    return jsonify({'success': True, 'message': 'Semua data dihapus'})

# ==================== ABSEN ====================
@app.route('/api/absen', methods=['GET'])
def get_absen():
    """Ambil data absen"""
    with data_lock:
        return jsonify(data_absen)

@app.route('/api/absen/generate', methods=['POST'])
def generate_absen():
    """Generate absen otomatis"""
    try:
        with data_lock:
            if not data_karyawan:
                return jsonify({'success': False, 'message': 'Belum ada data karyawan'}), 400
            
            data_absen.clear()
            for karyawan in data_karyawan:
                data_absen.append({
                    "id": karyawan["id"],
                    "hari_masuk": random.randint(20, 26)
                })
        
        return jsonify({'success': True, 'message': f'{len(data_absen)} absen berhasil dibuat'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==================== GAJI ====================
@app.route('/api/gaji', methods=['GET'])
def get_gaji():
    """Ambil data gaji"""
    with data_lock:
        return jsonify(data_gaji)

@app.route('/api/gaji/hitung/serial', methods=['POST'])
def hitung_gaji_serial():
    """Hitung gaji secara serial"""
    try:
        with data_lock:
            if not data_absen:
                return jsonify({'success': False, 'message': 'Data absen belum ada'}), 400
            
            data_gaji.clear()
            start = time.time()
            
            for i, k in enumerate(data_karyawan):
                hari_masuk = int(data_absen[i]["hari_masuk"])
                total = float(k["gaji_pokok"]) * hari_masuk
                data_gaji.append({
                    "id": k["id"],
                    "nama": k["nama"],
                    "total_gaji": total
                })
            
            elapsed = time.time() - start
            serial_times.append(elapsed)
            jumlah_data.append(len(data_karyawan))
        
        return jsonify({
            'success': True,
            'message': f'Gaji dihitung (Serial)',
            'waktu': elapsed,
            'jumlah': len(data_gaji)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/gaji/hitung/parallel', methods=['POST'])
def hitung_gaji_parallel_mpi():
    """Hitung gaji secara parallel dengan MPI"""
    try:
        data = request.get_json() or {}
        num_processes = data.get('processes', 4)
        
        with data_lock:
            if not data_absen:
                return jsonify({'success': False, 'message': 'Data absen belum ada'}), 400
            
            # Simpan data sementara ke file
            with open('temp_karyawan.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'jabatan', 'gaji_pokok'])
                writer.writeheader()
                writer.writerows(data_karyawan)
            
            with open('temp_absen.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'hari_masuk'])
                writer.writeheader()
                writer.writerows(data_absen)
        
        # Jalankan MPI program
        start = time.time()
        cmd = f'mpiexec -n {num_processes} python compute_salary_mpi.py'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        elapsed = time.time() - start
        
        # Baca hasil
        with data_lock:
            if os.path.exists('temp_gaji.csv'):
                data_gaji.clear()
                with open('temp_gaji.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data_gaji.extend(list(reader))
                
                # Convert string to float
                for g in data_gaji:
                    g['total_gaji'] = float(g['total_gaji'])
                
                parallel_times.append(elapsed)
                jumlah_data.append(len(data_gaji))
                
                # Cleanup
                os.remove('temp_karyawan.csv')
                os.remove('temp_absen.csv')
                os.remove('temp_gaji.csv')
                
                return jsonify({
                    'success': True,
                    'message': f'Gaji dihitung (Parallel MPI - {num_processes} proses)',
                    'waktu': elapsed,
                    'jumlah': len(data_gaji),
                    'output': result.stdout
                })
            else:
                return jsonify({'success': False, 'message': 'Error: ' + result.stderr}), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Timeout'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== STATS & CHART ====================
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Ambil statistik perbandingan"""
    with data_lock:
        stats = []
        for i in range(min(len(serial_times), len(parallel_times))):
            speedup = serial_times[i] / parallel_times[i] if parallel_times[i] != 0 else 0
            stats.append({
                'jumlah': jumlah_data[i] if i < len(jumlah_data) else 0,
                'serial': serial_times[i],
                'parallel': parallel_times[i],
                'speedup': speedup
            })
        
        return jsonify(stats)

@app.route('/api/stats/clear', methods=['POST'])
def clear_stats():
    """Hapus statistik"""
    with data_lock:
        serial_times.clear()
        parallel_times.clear()
        jumlah_data.clear()
    return jsonify({'success': True, 'message': 'Statistik dihapus'})

# ==================== CSV ====================
@app.route('/api/csv/save', methods=['POST'])
def save_csv():
    """Simpan semua data ke CSV"""
    try:
        with data_lock:
            # Simpan karyawan
            with open('karyawan.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'jabatan', 'gaji_pokok'])
                writer.writeheader()
                writer.writerows(data_karyawan)
            
            # Simpan absen
            with open('absen.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'hari_masuk'])
                writer.writeheader()
                writer.writerows(data_absen)
            
            # Simpan gaji
            with open('gaji.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'total_gaji'])
                writer.writeheader()
                writer.writerows(data_gaji)
        
        return jsonify({'success': True, 'message': 'Data berhasil disimpan ke CSV'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/csv/load', methods=['POST'])
def load_csv():
    """Muat data dari CSV"""
    try:
        with data_lock:
            # Muat karyawan
            if os.path.exists('karyawan.csv'):
                data_karyawan.clear()
                with open('karyawan.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data_karyawan.extend(list(reader))
            
            # Muat absen
            if os.path.exists('absen.csv'):
                data_absen.clear()
                with open('absen.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data_absen.extend(list(reader))
            
            # Muat gaji
            if os.path.exists('gaji.csv'):
                data_gaji.clear()
                with open('gaji.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data_gaji.extend(list(reader))
        
        return jsonify({
            'success': True,
            'message': f'Data dimuat: {len(data_karyawan)} karyawan, {len(data_absen)} absen, {len(data_gaji)} gaji'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  SISTEM PENGGAJIAN KARYAWAN - WEB APPLICATION")
    print("="*60)
    print("\nAkses aplikasi di: http://localhost:5000")
    print("\nFitur:")
    print("  - Input & Generate Data Karyawan")
    print("  - Input & Generate Data Absen")
    print("  - Hitung Gaji (Serial & Parallel MPI)")
    print("  - Statistik & Perbandingan Performa")
    print("  - Save/Load CSV")
    print("\nTekan Ctrl+C untuk berhenti\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
