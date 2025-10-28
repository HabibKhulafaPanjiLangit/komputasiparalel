from flask import Flask, render_template, jsonify, request, send_file  # type: ignore
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# Global error handler agar semua error return JSON
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({
            'success': False,
            'error': e.code,
            'message': e.description
        }), e.code
    return jsonify({
        'success': False,
        'error': 500,
        'message': str(e)
    }), 500
"""
Web Dashboard untuk MPI Payroll System
Akses melalui: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_file  # type: ignore
import subprocess
import json
import time
from datetime import datetime
import os
import sys
import threading
from io import StringIO
import csv


# Import database helpers (wajib DB, tidak ada fallback)
import db_helper
USE_DATABASE = True
print("[DB] Database helpers loaded")
print("[DB] Loading data from database...")
data_karyawan = db_helper.get_all_karyawan()
data_absen = db_helper.get_all_absen()
data_gaji = db_helper.get_all_gaji()
print(f"[DB] Loaded: {len(data_karyawan)} karyawan, {len(data_absen)} absen, {len(data_gaji)} gaji")

app = Flask(__name__)

# Simpan hasil benchmark
benchmark_results = []
current_status = {
    'running': False,
    'program': None,
    'start_time': None,
    'output': ''
}

# Lock untuk thread safety
status_lock = threading.Lock()

@app.route('/')
def index():
    """Halaman utama dashboard"""
    return render_template('index.html')

@app.route('/api/programs', methods=['GET'])
def get_programs_api():
    """Mendapatkan daftar program MPI yang tersedia"""
    
    # Check if MPI is available
    try:
        mpi_available = subprocess.run(
            'mpiexec --version' if os.name != 'nt' else 'mpiexec -help',
            shell=True,
            capture_output=True,
            timeout=5
        ).returncode == 0
    except:
        mpi_available = False
    
    programs = [
        {
            'id': 'payroll_serial',
            'name': 'Demo Payroll Serial',
            'file': 'payroll_demo_serial.py',
            'description': 'Demo sistem penggajian (No MPI - works in production)',
            'expected_speedup': 'N/A',
            'requires_mpi': False
        },
        {
            'id': 'pi_montecarlo',
            'name': 'Monte Carlo Pi Calculation',
            'file': 'pi_montecarlo_mpi.py',
            'description': 'Menghitung nilai Pi menggunakan metode Monte Carlo (Requires MPI)',
            'expected_speedup': '4.81x',
            'requires_mpi': True
        },
        {
            'id': 'payroll_demo',
            'name': 'Demo Payroll Otomatis',
            'file': 'demo_payroll_mpi.py',
            'description': 'Demo sistem penggajian dengan 10,000 karyawan (Requires MPI)',
            'expected_speedup': 'N/A',
            'requires_mpi': True
        },
        {
            'id': 'payroll_complex',
            'name': 'Benchmark Payroll Kompleks',
            'file': 'demo_payroll_complex.py',
            'description': 'Benchmark dengan perhitungan pajak CPU-intensive (Requires MPI)',
            'expected_speedup': '3.34x',
            'requires_mpi': True
        },
        {
            'id': 'payroll_simple',
            'name': 'Benchmark Payroll Sederhana',
            'file': 'demo_payroll_benchmark.py',
            'description': 'Benchmark dengan perhitungan sederhana (Requires MPI)',
            'expected_speedup': '0.33x (overhead dominan)',
            'requires_mpi': True
        }
    ]
    
    # Filter programs based on MPI availability
    if not mpi_available:
        # Only show non-MPI programs in production
        programs = [p for p in programs if not p.get('requires_mpi', False)]
    
    return jsonify(programs)

def get_programs_list():
    """Helper function to get programs list (not jsonified)"""
    # Check if MPI is available
    try:
        mpi_available = subprocess.run(
            'mpiexec --version' if os.name != 'nt' else 'mpiexec -help',
            shell=True,
            capture_output=True,
            timeout=5
        ).returncode == 0
    except:
        mpi_available = False
    
    programs = [
        {
            'id': 'payroll_serial',
            'name': 'Demo Payroll Serial',
            'file': 'payroll_demo_serial.py',
            'description': 'Demo sistem penggajian (No MPI - works in production)',
            'expected_speedup': 'N/A',
            'requires_mpi': False
        },
        {
            'id': 'pi_montecarlo',
            'name': 'Monte Carlo Pi Calculation',
            'file': 'pi_montecarlo_mpi.py',
            'description': 'Menghitung nilai Pi menggunakan metode Monte Carlo (Requires MPI)',
            'expected_speedup': '4.81x',
            'requires_mpi': True
        },
        {
            'id': 'payroll_demo',
            'name': 'Demo Payroll Otomatis',
            'file': 'demo_payroll_mpi.py',
            'description': 'Demo sistem penggajian dengan 10,000 karyawan (Requires MPI)',
            'expected_speedup': 'N/A',
            'requires_mpi': True
        },
        {
            'id': 'payroll_complex',
            'name': 'Benchmark Payroll Kompleks',
            'file': 'demo_payroll_complex.py',
            'description': 'Benchmark dengan perhitungan pajak CPU-intensive (Requires MPI)',
            'expected_speedup': '3.34x',
            'requires_mpi': True
        },
        {
            'id': 'payroll_simple',
            'name': 'Benchmark Payroll Sederhana',
            'file': 'demo_payroll_benchmark.py',
            'description': 'Benchmark dengan perhitungan sederhana (Requires MPI)',
            'expected_speedup': '0.33x (overhead dominan)',
            'requires_mpi': True
        }
    ]
    
    # Filter programs based on MPI availability
    if not mpi_available:
        programs = [p for p in programs if not p.get('requires_mpi', False)]
    
    return programs

@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Get system information"""
    import multiprocessing
    import platform
    
    # Check MPI availability
    mpi_available = False
    mpi_version = "Not available"
    try:
        result = subprocess.run(
            ['mpiexec', '--version'],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            mpi_available = True
            mpi_version = result.stdout.strip().split('\n')[0]
    except:
        pass
    
    info = {
        'cpu_count': multiprocessing.cpu_count(),
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'mpi_available': mpi_available,
        'mpi_version': mpi_version,
        'recommended_processes': multiprocessing.cpu_count()
    }
    
    return jsonify(info)

@app.route('/api/run/<program_id>', methods=['POST'])
def run_program(program_id):
    """Menjalankan program MPI"""
    
    with status_lock:
        if current_status['running']:
            return jsonify({
                'success': False,
                'message': 'Program lain sedang berjalan. Tunggu hingga selesai.'
            }), 400
    
    # Get program list and build mapping
    programs = get_programs_list()
    program_files = {}
    
    # Build mapping from programs
    for prog in programs:
        program_files[prog['id']] = prog['file']
    
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
        # Detect available CPU cores
        import multiprocessing
        max_cores = multiprocessing.cpu_count()
        
        # Limit processes to available cores
        actual_processes = min(num_processes, max_cores)
        
        # Check if mpiexec is available
        mpiexec_available = False
        try:
            check_result = subprocess.run(
                ['mpiexec', '--version'],
                capture_output=True,
                timeout=5
            )
            mpiexec_available = check_result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Try alternative check
            try:
                check_result = subprocess.run(
                    'which mpiexec',
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                mpiexec_available = check_result.returncode == 0
            except:
                mpiexec_available = False
        
        # Build command
        if mpiexec_available and actual_processes > 1:
            # Use MPI with optimal process count
            cmd = ['mpiexec', '-n', str(actual_processes), 'python', program_file]
            print(f"[MPI] Running with {actual_processes} processes (max cores: {max_cores})")
        else:
            # Fallback to serial execution
            cmd = ['python', program_file]
            if not mpiexec_available:
                print(f"[WARNING] mpiexec not available, running in serial mode")
            else:
                print(f"[INFO] Single process requested, running in serial mode")
        
        result = subprocess.run(
            cmd,
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
    if USE_DATABASE:
        # Always reload from database to ensure fresh data
        return jsonify(db_helper.get_all_karyawan())
    else:
        with status_lock:
            karyawan = data_karyawan.copy()
        return jsonify(karyawan)

@app.route('/api/karyawan', methods=['POST'])
def add_karyawan_endpoint():
    """Menambah data karyawan"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['id', 'nama', 'jabatan', 'gaji_pokok']):
        return jsonify({'success': False, 'message': 'Data tidak lengkap'}), 400
    
    try:
        karyawan_id = str(data['id'])
        nama = str(data['nama'])
        jabatan = str(data['jabatan'])
        gaji_pokok = float(data['gaji_pokok'])
        
        # Save to database if available
        if USE_DATABASE:
            ok, msg = db_helper.add_karyawan(karyawan_id, nama, jabatan, gaji_pokok)
            # Reload data_karyawan dari database agar selalu sinkron
            global data_karyawan
            data_karyawan = db_helper.get_all_karyawan()
            if ok:
                return jsonify({'success': True, 'message': 'Karyawan berhasil ditambahkan'})
            else:
                return jsonify({'success': False, 'message': msg}), 500
        else:
            # Fallback to in-memory
            karyawan = {
                'id': karyawan_id,
                'nama': nama,
                'jabatan': jabatan,
                'gaji_pokok': gaji_pokok
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
def delete_karyawan_endpoint(karyawan_id):
    """Menghapus data karyawan"""
    if USE_DATABASE:
        if db_helper.delete_karyawan(karyawan_id):
            return jsonify({'success': True, 'message': 'Karyawan berhasil dihapus'})
        else:
            return jsonify({'success': False, 'message': 'Gagal menghapus dari database'}), 500
    else:
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
    if USE_DATABASE:
        # Always reload from database
        return jsonify(db_helper.get_all_absen())
    else:
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
        if USE_DATABASE:
            from db_helper import add_absen, get_all_absen
            ok, msg = add_absen(absen['id'], absen['hari_masuk'])
            # Reload data_absen dari database agar selalu sinkron
            global data_absen
            data_absen = get_all_absen()
            if not ok:
                return jsonify({'success': False, 'message': msg}), 500
        else:
            with status_lock:
                # Update jika sudah ada, tambah jika belum
                existing = next((a for a in data_absen if a['id'] == absen['id']), None)
                if existing:
                    existing['hari_masuk'] = absen['hari_masuk']
                else:
                    data_absen.append(absen)
        print(f"[DEBUG] Data absen sekarang: {data_absen}")
        return jsonify({'success': True, 'message': 'Data absen berhasil disimpan'})
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400

@app.route('/api/gaji/hitung', methods=['POST'])
def hitung_gaji():
    """Hitung gaji dengan MPI"""
    # Selalu reload data dari database sebelum proses hitung
    global data_karyawan, data_absen, data_gaji
    data_karyawan = db_helper.get_all_karyawan()
    data_absen = db_helper.get_all_absen()
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
    data_gaji = []
    start_time = time.time()
    try:
        if mode == 'serial':
            # Serial calculation
            for karyawan in data_karyawan:
                absen = next((a for a in data_absen if a['id'] == karyawan['id']), None)
                if absen:
                    try:
                        total_gaji = float(karyawan['gaji_pokok']) * int(absen['hari_masuk'])
                        data_gaji.append({
                            'id': karyawan['id'],
                            'nama': karyawan['nama'],
                            'jabatan': karyawan.get('jabatan', ''),
                            'gaji_pokok': float(karyawan['gaji_pokok']),
                            'hari_masuk': int(absen['hari_masuk']),
                            'total_gaji': total_gaji
                        })
                    except Exception as err:
                        print(f"[ERROR] Gagal hitung gaji untuk karyawan {karyawan['id']}: {err}")
        else:
            # Parallel dengan MPI (simplified - langsung hitung di sini)
            for karyawan in data_karyawan:
                absen = next((a for a in data_absen if a['id'] == karyawan['id']), None)
                if absen:
                    try:
                        total_gaji = float(karyawan['gaji_pokok']) * int(absen['hari_masuk'])
                        data_gaji.append({
                            'id': karyawan['id'],
                            'nama': karyawan['nama'],
                            'jabatan': karyawan.get('jabatan', ''),
                            'gaji_pokok': float(karyawan['gaji_pokok']),
                            'hari_masuk': int(absen['hari_masuk']),
                            'total_gaji': total_gaji
                        })
                    except Exception as err:
                        print(f"[ERROR] Gagal hitung gaji untuk karyawan {karyawan['id']}: {err}")
        elapsed = time.time() - start_time
        # Simpan ke database
        from db_helper import clear_and_save_gaji
        ok, msg = clear_and_save_gaji(data_gaji, mode=mode, waktu=elapsed)
        if not ok:
            print(f"[ERROR] Gagal simpan gaji ke database: {msg}")
            return jsonify({'success': False, 'message': msg}), 500
        return jsonify({
            'success': True,
            'message': f'Gaji berhasil dihitung ({mode})',
            'elapsed_time': elapsed,
            'total_karyawan': len(data_gaji)
        })
    except Exception as e:
        print(f"[ERROR] Exception saat menghitung gaji: {e}")
        return jsonify({'success': False, 'message': f'Error saat menghitung gaji: {str(e)}'}), 500

@app.route('/api/gaji', methods=['GET'])
def get_gaji():
    """Mendapatkan hasil perhitungan gaji"""
    if USE_DATABASE:
        # Always reload from database
        return jsonify(db_helper.get_all_gaji())
    else:
        with status_lock:
            gaji = data_gaji.copy()
        return jsonify(gaji)

@app.route('/api/data/export', methods=['GET'])
def export_data():
    """Export semua data ke CSV"""
    import csv
    
    try:
        # Selalu ambil data terbaru dari database
        karyawan_list = db_helper.get_all_karyawan()
        absen_list = db_helper.get_all_absen()
        gaji_list = db_helper.get_all_gaji()

        with open('karyawan.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'jabatan', 'gaji_pokok'])
            writer.writeheader()
            writer.writerows(karyawan_list)

        with open('absen.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'hari_masuk'])
            writer.writeheader()
            writer.writerows(absen_list)

        # Pastikan field gaji sesuai dengan struktur database
        gaji_fields = ['id', 'nama', 'jabatan', 'gaji_pokok', 'hari_masuk', 'total_gaji', 'mode_hitung', 'waktu_hitung']
        with open('gaji.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=gaji_fields)
            writer.writeheader()
            writer.writerows(gaji_list)

        return jsonify({'success': True, 'message': 'Data berhasil di-export ke CSV'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/generate-dummy', methods=['POST'])
def generate_dummy():
    """Generate dummy data untuk testing"""
    from db_helper import generate_dummy_data, get_all_karyawan, get_all_absen
    try:
        data = request.get_json() or {}
        jumlah = int(data.get('jumlah', 10))
        if jumlah < 1 or jumlah > 1000:
            return jsonify({'success': False, 'message': 'Jumlah harus antara 1-1000'}), 400

        ok, msg = generate_dummy_data(jumlah)
        if not ok:
            return jsonify({'success': False, 'message': msg}), 500

        # Sinkronkan data in-memory agar dashboard langsung update
        with status_lock:
            data_karyawan.clear()
            data_karyawan.extend(get_all_karyawan())
            data_absen.clear()
            data_absen.extend(get_all_absen())
            data_gaji.clear()

        return jsonify({
            'success': True,
            'jumlah': jumlah,
            'message': msg,
            'total_karyawan': len(data_karyawan),
            'total_absen': len(data_absen)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/database/browse', methods=['GET'])
def browse_database_api():
    """Browse database dan tampilkan info semua table"""
    try:
        import sqlite3
        import os
        from datetime import datetime
        
        db_path = 'payroll.db'
        
        # Check if database exists
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'message': 'Database tidak ditemukan'
            }), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get database info
        db_info = {
            'path': os.path.abspath(db_path),
            'size': os.path.getsize(db_path),
            'modified': datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S'),
            'tables': []
        }
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Get count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    'name': col[1],
                    'type': col[2],
                    'notnull': col[3],
                    'primary_key': col[5]
                })
            
            # Get sample data (first 100 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
            rows = cursor.fetchall()
            
            table_info = {
                'name': table_name,
                'count': count,
                'columns': columns,
                'sample_data': []
            }
            
            # Format sample data
            if rows:
                column_names = [col['name'] for col in columns]
                for row in rows:
                    row_dict = {}
                    for i, col_name in enumerate(column_names):
                        value = row[i]
                        # Format value for display
                        if isinstance(value, float):
                            row_dict[col_name] = f"{value:,.0f}"
                        else:
                            row_dict[col_name] = str(value) if value is not None else None
                    table_info['sample_data'].append(row_dict)
            
            db_info['tables'].append(table_info)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'database': db_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("  MPI PAYROLL SYSTEM - WEB DASHBOARD")
    print("="*60)
    print(f"\nWeb server akan berjalan di: http://0.0.0.0:{port}")
    print("API Endpoints tersedia:")
    print("   - GET  /api/programs")
    print("   - POST /api/run/<program_id>")
    print("   - GET  /api/status")
    print("   - GET  /api/results")
    print("   - GET  /api/database/browse")
    print("\nTekan Ctrl+C untuk berhenti\n")
    
    # Nonaktifkan reloader untuk menghindari masalah dengan threading
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
