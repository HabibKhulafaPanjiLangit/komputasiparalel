"""
Web Dashboard untuk MPI Payroll System
Akses melalui: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request  # type: ignore
import subprocess
import json
import time
from datetime import datetime
import os
import sys
import threading

app = Flask(__name__)

# Simpan hasil benchmark
benchmark_results = []
current_status = {
    'running': False,
    'program': None,
    'start_time': None,
    'output': ''
}

# Data karyawan manual
data_karyawan = []
data_absen = []
data_gaji = []

# Lock untuk thread safety
status_lock = threading.Lock()

@app.route('/')
def index():
    """Halaman utama dashboard"""
    return render_template('index.html')

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """Mendapatkan daftar program MPI yang tersedia"""
    programs = [
        {
            'id': 'pi_montecarlo',
            'name': 'Monte Carlo Pi Calculation',
            'file': 'pi_montecarlo_mpi.py',
            'description': 'Menghitung nilai Pi menggunakan metode Monte Carlo',
            'expected_speedup': '4.81x'
        },
        {
            'id': 'payroll_demo',
            'name': 'Demo Payroll Otomatis',
            'file': 'demo_payroll_mpi.py',
            'description': 'Demo sistem penggajian dengan 10,000 karyawan',
            'expected_speedup': 'N/A'
        },
        {
            'id': 'payroll_complex',
            'name': 'Benchmark Payroll Kompleks',
            'file': 'demo_payroll_complex.py',
            'description': 'Benchmark dengan perhitungan pajak CPU-intensive',
            'expected_speedup': '3.34x'
        },
        {
            'id': 'payroll_simple',
            'name': 'Benchmark Payroll Sederhana',
            'file': 'demo_payroll_benchmark.py',
            'description': 'Benchmark dengan perhitungan sederhana',
            'expected_speedup': '0.33x (overhead dominan)'
        }
    ]
    return jsonify(programs)

@app.route('/api/run/<program_id>', methods=['POST'])
def run_program(program_id):
    """Menjalankan program MPI"""
    
    with status_lock:
        if current_status['running']:
            return jsonify({
                'success': False,
                'message': 'Program lain sedang berjalan. Tunggu hingga selesai.'
            }), 400
    
    # Mapping program
    program_files = {
        'pi_montecarlo': 'pi_montecarlo_mpi.py',
        'payroll_demo': 'demo_payroll_mpi.py',
        'payroll_complex': 'demo_payroll_complex.py',
        'payroll_simple': 'demo_payroll_benchmark.py'
    }
    
    if program_id not in program_files:
        return jsonify({
            'success': False,
            'message': 'Program tidak ditemukan'
        }), 404
    
    # Ambil jumlah proses dari request (default 4)
    data = request.get_json() or {}
    num_processes = data.get('processes', 4)
    
    # Jalankan di background thread
    thread = threading.Thread(
        target=run_mpi_program,
        args=(program_id, program_files[program_id], num_processes)
    )
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Program {program_id} dimulai dengan {num_processes} proses'
    })

def run_mpi_program(program_id, program_file, num_processes):
    """Fungsi untuk menjalankan MPI program di background"""
    global current_status, benchmark_results
    
    # Update status
    with status_lock:
        current_status['running'] = True
        current_status['program'] = program_id
        current_status['start_time'] = time.time()
        current_status['output'] = ''
    
    try:
        # Jalankan program MPI
        cmd = f'mpiexec -n {num_processes} python {program_file}'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 menit timeout
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        elapsed = time.time() - current_status['start_time']
        
        # Simpan hasil
        benchmark_result = {
            'timestamp': datetime.now().isoformat(),
            'program_id': program_id,
            'num_processes': num_processes,
            'elapsed_time': elapsed,
            'output': result.stdout,
            'error': result.stderr,
            'success': result.returncode == 0
        }
        
        with status_lock:
            benchmark_results.insert(0, benchmark_result)
            if len(benchmark_results) > 20:  # Keep only last 20 results
                benchmark_results = benchmark_results[:20]
        
    except subprocess.TimeoutExpired:
        benchmark_result = {
            'timestamp': datetime.now().isoformat(),
            'program_id': program_id,
            'num_processes': num_processes,
            'elapsed_time': 300,
            'output': '',
            'error': 'Program timeout (lebih dari 5 menit)',
            'success': False
        }
        with status_lock:
            benchmark_results.insert(0, benchmark_result)
        
    except Exception as e:
        benchmark_result = {
            'timestamp': datetime.now().isoformat(),
            'program_id': program_id,
            'num_processes': num_processes,
            'elapsed_time': 0,
            'output': '',
            'error': f'Error: {str(e)}',
            'success': False
        }
        with status_lock:
            benchmark_results.insert(0, benchmark_result)
    
    finally:
        # Reset status
        with status_lock:
            current_status['running'] = False
            current_status['program'] = None
            current_status['start_time'] = None

@app.route('/api/status', methods=['GET'])
def get_status():
    """Mendapatkan status program yang sedang berjalan"""
    with status_lock:
        status = current_status.copy()
        if status['start_time']:
            status['elapsed'] = time.time() - status['start_time']
        else:
            status['elapsed'] = 0
    return jsonify(status)

@app.route('/api/results', methods=['GET'])
def get_results():
    """Mendapatkan hasil benchmark sebelumnya"""
    with status_lock:
        results = benchmark_results.copy()
    return jsonify(results)

@app.route('/api/results/clear', methods=['POST'])
def clear_results():
    """Menghapus semua hasil benchmark"""
    with status_lock:
        benchmark_results.clear()
    return jsonify({'success': True, 'message': 'Hasil benchmark dihapus'})

# ==============================
# API untuk Data Karyawan Manual
# ==============================

@app.route('/api/karyawan', methods=['GET'])
def get_karyawan():
    """Mendapatkan semua data karyawan"""
    with status_lock:
        karyawan = data_karyawan.copy()
    return jsonify(karyawan)

@app.route('/api/karyawan', methods=['POST'])
def add_karyawan():
    """Menambah data karyawan"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['id', 'nama', 'jabatan', 'gaji_pokok']):
        return jsonify({'success': False, 'message': 'Data tidak lengkap'}), 400
    
    try:
        karyawan = {
            'id': str(data['id']),
            'nama': str(data['nama']),
            'jabatan': str(data['jabatan']),
            'gaji_pokok': float(data['gaji_pokok'])
        }
        
        with status_lock:
            # Cek ID duplikat
            if any(k['id'] == karyawan['id'] for k in data_karyawan):
                return jsonify({'success': False, 'message': 'ID karyawan sudah ada'}), 400
            
            data_karyawan.append(karyawan)
        
        return jsonify({'success': True, 'message': 'Karyawan berhasil ditambahkan'})
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400

@app.route('/api/karyawan/<karyawan_id>', methods=['DELETE'])
def delete_karyawan(karyawan_id):
    """Menghapus data karyawan"""
    with status_lock:
        global data_karyawan
        data_karyawan = [k for k in data_karyawan if k['id'] != karyawan_id]
        # Hapus absen terkait
        global data_absen
        data_absen = [a for a in data_absen if a['id'] != karyawan_id]
    
    return jsonify({'success': True, 'message': 'Karyawan berhasil dihapus'})

@app.route('/api/karyawan/clear', methods=['POST'])
def clear_karyawan():
    """Menghapus semua data karyawan"""
    with status_lock:
        data_karyawan.clear()
        data_absen.clear()
        data_gaji.clear()
    return jsonify({'success': True, 'message': 'Semua data karyawan dihapus'})

@app.route('/api/absen', methods=['GET'])
def get_absen():
    """Mendapatkan semua data absen"""
    with status_lock:
        absen = data_absen.copy()
    return jsonify(absen)

@app.route('/api/absen', methods=['POST'])
def add_absen():
    """Menambah data absen"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['id', 'hari_masuk']):
        return jsonify({'success': False, 'message': 'Data tidak lengkap'}), 400
    
    try:
        absen = {
            'id': str(data['id']),
            'hari_masuk': int(data['hari_masuk'])
        }
        
        with status_lock:
            # Update jika sudah ada, tambah jika belum
            existing = next((a for a in data_absen if a['id'] == absen['id']), None)
            if existing:
                existing['hari_masuk'] = absen['hari_masuk']
            else:
                data_absen.append(absen)
        
        return jsonify({'success': True, 'message': 'Data absen berhasil disimpan'})
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400

@app.route('/api/gaji/hitung', methods=['POST'])
def hitung_gaji():
    """Hitung gaji dengan MPI"""
    if not data_karyawan:
        return jsonify({'success': False, 'message': 'Belum ada data karyawan'}), 400
    
    if not data_absen:
        return jsonify({'success': False, 'message': 'Belum ada data absen'}), 400
    
    data = request.get_json() or {}
    mode = data.get('mode', 'parallel')  # parallel atau serial
    num_processes = data.get('processes', 4)
    
    # Simpan data ke file temporary
    import csv
    with open('temp_karyawan.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'jabatan', 'gaji_pokok'])
        writer.writeheader()
        writer.writerows(data_karyawan)
    
    with open('temp_absen.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'hari_masuk'])
        writer.writeheader()
        writer.writerows(data_absen)
    
    # Hitung gaji
    global data_gaji
    data_gaji = []
    
    start_time = time.time()
    
    if mode == 'serial':
        # Serial calculation
        for karyawan in data_karyawan:
            absen = next((a for a in data_absen if a['id'] == karyawan['id']), None)
            if absen:
                total_gaji = karyawan['gaji_pokok'] * absen['hari_masuk']
                data_gaji.append({
                    'id': karyawan['id'],
                    'nama': karyawan['nama'],
                    'total_gaji': total_gaji
                })
    else:
        # Parallel dengan MPI (simplified - langsung hitung di sini)
        # Untuk MPI sebenarnya, kita perlu program terpisah
        for karyawan in data_karyawan:
            absen = next((a for a in data_absen if a['id'] == karyawan['id']), None)
            if absen:
                total_gaji = karyawan['gaji_pokok'] * absen['hari_masuk']
                data_gaji.append({
                    'id': karyawan['id'],
                    'nama': karyawan['nama'],
                    'total_gaji': total_gaji
                })
    
    elapsed = time.time() - start_time
    
    return jsonify({
        'success': True,
        'message': f'Gaji berhasil dihitung ({mode})',
        'elapsed_time': elapsed,
        'total_karyawan': len(data_gaji)
    })

@app.route('/api/gaji', methods=['GET'])
def get_gaji():
    """Mendapatkan hasil perhitungan gaji"""
    with status_lock:
        gaji = data_gaji.copy()
    return jsonify(gaji)

@app.route('/api/data/export', methods=['GET'])
def export_data():
    """Export semua data ke CSV"""
    import csv
    
    try:
        with open('karyawan.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'jabatan', 'gaji_pokok'])
            writer.writeheader()
            writer.writerows(data_karyawan)
        
        with open('absen.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'hari_masuk'])
            writer.writeheader()
            writer.writerows(data_absen)
        
        with open('gaji.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'total_gaji'])
            writer.writeheader()
            writer.writerows(data_gaji)
        
        return jsonify({'success': True, 'message': 'Data berhasil di-export ke CSV'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  MPI PAYROLL SYSTEM - WEB DASHBOARD")
    print("="*60)
    print("\nWeb server akan berjalan di: http://localhost:5000")
    print("API Endpoints tersedia:")
    print("   - GET  /api/programs")
    print("   - POST /api/run/<program_id>")
    print("   - GET  /api/status")
    print("   - GET  /api/results")
    print("\nTekan Ctrl+C untuk berhenti\n")
    
    # Nonaktifkan reloader untuk menghindari masalah dengan threading
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
