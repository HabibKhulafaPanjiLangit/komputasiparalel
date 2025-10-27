// Global state
let programs = [];
let runningStatus = {};

// Tab switching
function switchTab(event, tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked tab and corresponding content
    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Load data when switching tabs
    if (tabName === 'data') {
        loadKaryawan();
        loadAbsen();
    } else if (tabName === 'hasil') {
        loadGaji();
    } else if (tabName === 'interactive') {
        loadInteractiveStats();
        loadKaryawanForSelect();
    } else if (tabName === 'database') {
        loadDatabaseInfo();
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', function() {
    loadSystemInfo();
    loadPrograms();
    loadKaryawan();
    loadAbsen();
    updateStatus();
    setInterval(updateStatus, 2000); // Check status every 2 seconds
});

// Load system information
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system/info');
        const info = await response.json();
        
        const infoDiv = document.getElementById('systemInfo');
        let html = 'System: ';
        html += info.cpu_count + ' CPUs | ';
        html += 'Python ' + info.python_version + ' | ';
        
        if (info.mpi_available) {
            html += 'MPI: ' + info.mpi_version + ' (Optimal: ' + info.recommended_processes + ' processes)';
        } else {
            html += 'MPI: Not available (Serial mode only)';
        }
        
        infoDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading system info:', error);
    }
}

// Load available programs
async function loadPrograms() {
    try {
        const response = await fetch('/api/programs');
        programs = await response.json();
        
        const grid = document.getElementById('programsGrid');
        let html = '';
        
        for (const prog of programs) {
            html += '<div class="program-item" onclick="runProgram(\'' + prog.id + '\')">';
            html += '<h3>' + prog.name + '</h3>';
            html += '<p>' + prog.description + '</p>';
            html += '</div>';
        }
        
        grid.innerHTML = html;
    } catch (error) {
        console.error('Error loading programs:', error);
    }
}

// Run MPI program
async function runProgram(programId) {
    const statusText = document.getElementById('statusText');
    statusText.textContent = 'Running...';
    statusText.className = 'status-badge status-running';
    
    try {
        const response = await fetch('/api/run/' + programId, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Program started: ' + result.message);
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        statusText.textContent = 'Error';
        statusText.className = 'status-badge status-error';
        alert('Error: ' + error.message);
    }
}

// Update status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        const statusText = document.getElementById('statusText');
        statusText.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
        statusText.className = `status-badge status-${status.status}`;
        
        // Update results if available
        if (status.results && status.results.length > 0) {
            displayResults(status.results);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Display benchmark results
function displayResults(results) {
    const container = document.getElementById('benchmarkResults');
    
    if (results.length === 0) {
        container.innerHTML = '<p>Belum ada hasil benchmark.</p>';
        return;
    }
    
    container.innerHTML = results.map(result => `
        <div style="margin-bottom: 20px; border-left: 4px solid #667eea; padding-left: 15px;">
            <h3 style="color: #667eea;">${result.name}</h3>
            <p><strong>Waktu Eksekusi:</strong> ${result.timestamp}</p>
            <pre>${result.output}</pre>
        </div>
    `).join('');
}

// Clear results
async function clearResults() {
    if (!confirm('Hapus semua hasil benchmark?')) return;
    
    try {
        await fetch('/api/clear', { method: 'POST' });
        document.getElementById('benchmarkResults').innerHTML = '<p>Belum ada hasil benchmark.</p>';
        alert('Hasil benchmark telah dihapus.');
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ===== KARYAWAN FUNCTIONS =====

async function loadKaryawan() {
    try {
        const response = await fetch('/api/karyawan');
        const karyawan = await response.json();
        
        document.getElementById('totalKaryawan').textContent = karyawan.length;
        
        const table = document.getElementById('tableKaryawan');
        if (karyawan.length === 0) {
            table.innerHTML = '<p>Belum ada data karyawan.</p>';
            return;
        }
        
        table.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nama</th>
                        <th>Jabatan</th>
                        <th>Gaji Pokok/Hari</th>
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
                    ${karyawan.map(k => `
                        <tr>
                            <td>${k.id}</td>
                            <td>${k.nama}</td>
                            <td>${k.jabatan}</td>
                            <td>Rp ${k.gaji_pokok.toLocaleString()}</td>
                            <td><button class="delete-btn" onclick="deleteKaryawan('${k.id}')">Hapus</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        // Update select options for absen form
        const select = document.getElementById('absen_id');
        select.innerHTML = '<option value="">-- Pilih Karyawan --</option>' +
            karyawan.map(k => `<option value="${k.id}">${k.id} - ${k.nama}</option>`).join('');
    } catch (error) {
        console.error('Error loading karyawan:', error);
    }
}

async function addKaryawan(event) {
    event.preventDefault();
    
    const data = {
        id: document.getElementById('karyawan_id').value,
        nama: document.getElementById('karyawan_nama').value,
        jabatan: document.getElementById('karyawan_jabatan').value,
        gaji_pokok: parseFloat(document.getElementById('karyawan_gaji').value)
    };
    
    try {
        const response = await fetch('/api/karyawan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Karyawan berhasil ditambahkan!');
            document.getElementById('formKaryawan').reset();
            loadKaryawan();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteKaryawan(id) {
    if (!confirm(`Hapus karyawan ${id}?`)) return;
    
    try {
        await fetch(`/api/karyawan/${id}`, { method: 'DELETE' });
        alert('Karyawan berhasil dihapus!');
        loadKaryawan();
        loadAbsen();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ===== ABSEN FUNCTIONS =====

async function loadAbsen() {
    try {
        const response = await fetch('/api/absen');
        const absen = await response.json();
        
        const table = document.getElementById('tableAbsen');
        if (absen.length === 0) {
            table.innerHTML = '<p>Belum ada data absen.</p>';
            return;
        }
        
        table.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID Karyawan</th>
                        <th>Jumlah Hari Masuk</th>
                    </tr>
                </thead>
                <tbody>
                    ${absen.map(a => `
                        <tr>
                            <td>${a.id}</td>
                            <td>${a.hari_masuk} hari</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading absen:', error);
    }
}

async function addAbsen(event) {
    event.preventDefault();
    
    const data = {
        id: document.getElementById('absen_id').value,
        hari_masuk: parseInt(document.getElementById('absen_hari').value)
    };
    
    try {
        const response = await fetch('/api/absen', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Data absen berhasil disimpan!');
            document.getElementById('formAbsen').reset();
            loadAbsen();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ===== GAJI FUNCTIONS =====

async function hitungGaji(mode) {
    if (!confirm(`Hitung gaji menggunakan mode ${mode}?`)) return;
    
    try {
        const response = await fetch('/api/gaji/hitung', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`Gaji berhasil dihitung!\nWaktu eksekusi: ${result.waktu_eksekusi}`);
            loadGaji();
            
            // Switch to hasil tab
            document.querySelectorAll('.tab')[2].click();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function loadGaji() {
    try {
        const response = await fetch('/api/gaji');
        const gaji = await response.json();
        
        const table = document.getElementById('tableGaji');
        if (gaji.length === 0) {
            table.innerHTML = '<p>Belum ada hasil perhitungan gaji. Silakan hitung terlebih dahulu.</p>';
            return;
        }
        
        const total = gaji.reduce((sum, g) => sum + g.total_gaji, 0);
        
        table.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nama</th>
                        <th>Jabatan</th>
                        <th>Gaji Pokok/Hari</th>
                        <th>Hari Masuk</th>
                        <th>Total Gaji</th>
                    </tr>
                </thead>
                <tbody>
                    ${gaji.map(g => `
                        <tr>
                            <td>${g.id}</td>
                            <td>${g.nama}</td>
                            <td>${g.jabatan}</td>
                            <td>Rp ${g.gaji_pokok.toLocaleString()}</td>
                            <td>${g.hari_masuk} hari</td>
                            <td><strong>Rp ${g.total_gaji.toLocaleString()}</strong></td>
                        </tr>
                    `).join('')}
                    <tr style="background: #f7fafc; font-weight: bold;">
                        <td colspan="5" style="text-align: right;">TOTAL</td>
                        <td>Rp ${total.toLocaleString()}</td>
                    </tr>
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading gaji:', error);
    }
}

async function exportData() {
    try {
        window.location.href = '/api/data/export';
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function clearAll() {
    if (!confirm('Hapus semua data karyawan dan absen? Tindakan ini tidak dapat dibatalkan!')) return;
    
    try {
        const responseKaryawan = await fetch('/api/karyawan');
        const karyawan = await responseKaryawan.json();
        
        for (const k of karyawan) {
            await fetch(`/api/karyawan/${k.id}`, { method: 'DELETE' });
        }
        
        alert('Semua data telah dihapus!');
        loadKaryawan();
        loadAbsen();
        loadGaji();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ===== INTERACTIVE MODE FUNCTIONS =====

async function loadInteractiveStats() {
    try {
        const [karyawanRes, absenRes, gajiRes] = await Promise.all([
            fetch('/api/karyawan'),
            fetch('/api/absen'),
            fetch('/api/gaji')
        ]);
        
        const karyawan = await karyawanRes.json();
        const absen = await absenRes.json();
        const gaji = await gajiRes.json();
        
        document.getElementById('statKaryawan').textContent = karyawan.length;
        document.getElementById('statAbsen').textContent = absen.length;
        document.getElementById('statGaji').textContent = gaji.length;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function showInputKaryawanForm() {
    document.getElementById('formInputKaryawan').style.display = 'block';
    document.getElementById('formInputAbsen').style.display = 'none';
    document.getElementById('resultInteractive').style.display = 'none';
}

function hideInputKaryawanForm() {
    document.getElementById('formInputKaryawan').style.display = 'none';
}

function showInputAbsenForm() {
    loadKaryawanForSelect();
    document.getElementById('formInputAbsen').style.display = 'block';
    document.getElementById('formInputKaryawan').style.display = 'none';
    document.getElementById('resultInteractive').style.display = 'none';
}

function hideInputAbsenForm() {
    document.getElementById('formInputAbsen').style.display = 'none';
}

async function loadKaryawanForSelect() {
    try {
        const response = await fetch('/api/karyawan');
        const karyawan = await response.json();
        
        const select = document.getElementById('int_absen_id');
        select.innerHTML = '<option value="">-- Pilih Karyawan --</option>' +
            karyawan.map(k => `<option value="${k.id}">${k.id} - ${k.nama}</option>`).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function submitKaryawanInteractive(event) {
    event.preventDefault();
    
    const data = {
        id: document.getElementById('int_karyawan_id').value,
        nama: document.getElementById('int_karyawan_nama').value,
        jabatan: document.getElementById('int_karyawan_jabatan').value,
        gaji_pokok: parseFloat(document.getElementById('int_karyawan_gaji').value)
    };
    
    try {
        const response = await fetch('/api/karyawan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(`Berhasil! Karyawan ${data.nama} telah ditambahkan.`, 'success');
            document.querySelector('#formInputKaryawan form').reset();
            hideInputKaryawanForm();
            loadInteractiveStats();
        } else {
            showResult('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

async function submitAbsenInteractive(event) {
    event.preventDefault();
    
    const data = {
        id: document.getElementById('int_absen_id').value,
        hari_masuk: parseInt(document.getElementById('int_absen_hari').value)
    };
    
    try {
        const response = await fetch('/api/absen', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(`Berhasil! Data absen untuk ${data.id} telah disimpan (${data.hari_masuk} hari).`, 'success');
            document.querySelector('#formInputAbsen form').reset();
            hideInputAbsenForm();
            loadInteractiveStats();
        } else {
            showResult('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

async function hitungGajiInteractive(mode) {
    updateInteractiveStatus('running');
    showResult(`Menghitung gaji dalam mode ${mode.toUpperCase()}...`, 'info');
    
    try {
        const response = await fetch('/api/gaji/hitung', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            updateInteractiveStatus('success');
            showResult(
                `<strong>Perhitungan Selesai!</strong><br>
                Mode: ${mode.toUpperCase()}<br>
                Waktu Eksekusi: ${result.waktu_eksekusi}<br>
                Total Karyawan: ${result.jumlah}<br>
                <button class="btn" style="background: #4299e1; color: white; margin-top: 10px;" onclick="tampilkanDataGaji()">Lihat Hasil</button>`,
                'success'
            );
            loadInteractiveStats();
        } else {
            updateInteractiveStatus('error');
            showResult('Error: ' + result.error, 'error');
        }
    } catch (error) {
        updateInteractiveStatus('error');
        showResult('Error: ' + error.message, 'error');
    }
}

async function tampilkanDataGaji() {
    try {
        const response = await fetch('/api/gaji');
        const gaji = await response.json();
        
        if (gaji.length === 0) {
            showResult('Belum ada data gaji. Silakan hitung terlebih dahulu.', 'info');
            return;
        }
        
        const total = gaji.reduce((sum, g) => sum + g.total_gaji, 0);
        
        let html = `
            <h4>Data Gaji Karyawan (${gaji.length} karyawan)</h4>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nama</th>
                        <th>Jabatan</th>
                        <th>Hari Masuk</th>
                        <th>Total Gaji</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        gaji.forEach(g => {
            html += `
                <tr>
                    <td>${g.id}</td>
                    <td>${g.nama}</td>
                    <td>${g.jabatan}</td>
                    <td>${g.hari_masuk} hari</td>
                    <td><strong>Rp ${g.total_gaji.toLocaleString()}</strong></td>
                </tr>
            `;
        });
        
        html += `
                    <tr style="background: #f7fafc; font-weight: bold;">
                        <td colspan="4" style="text-align: right;">TOTAL SEMUA GAJI</td>
                        <td>Rp ${total.toLocaleString()}</td>
                    </tr>
                </tbody>
            </table>
        `;
        
        showResult(html, 'success');
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

async function simpanSemuaData() {
    try {
        const response = await fetch('/api/data/export');
        if (response.ok) {
            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `payroll_data_${new Date().getTime()}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showResult('Data berhasil disimpan dan didownload sebagai CSV!', 'success');
        } else {
            showResult('Error: Gagal menyimpan data', 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

async function muatDariCSV() {
    showResult('Fitur muat dari CSV akan mengambil data yang ada di server.', 'info');
    loadInteractiveStats();
}

async function generateDummyData() {
    const jumlah = prompt('Berapa jumlah karyawan dummy yang ingin dibuat?', '10');
    if (!jumlah) return;
    
    try {
        const response = await fetch('/api/generate-dummy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jumlah: parseInt(jumlah) })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(`Berhasil generate ${result.jumlah} karyawan dummy beserta data absennya!`, 'success');
            loadInteractiveStats();
        } else {
            showResult('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

async function hapusSemuaDataInteractive() {
    if (!confirm('Hapus semua data karyawan, absen, dan gaji? Tindakan ini tidak dapat dibatalkan!')) return;
    
    try {
        const responseKaryawan = await fetch('/api/karyawan');
        const karyawan = await responseKaryawan.json();
        
        for (const k of karyawan) {
            await fetch(`/api/karyawan/${k.id}`, { method: 'DELETE' });
        }
        
        showResult('Semua data telah dihapus!', 'success');
        loadInteractiveStats();
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

function showResult(message, type) {
    const resultDiv = document.getElementById('resultInteractive');
    const contentDiv = document.getElementById('resultContent');
    
    let className = '';
    if (type === 'success') className = 'status-success';
    else if (type === 'error') className = 'status-error';
    else if (type === 'info') className = 'status-running';
    
    contentDiv.innerHTML = `<div class="${className}" style="padding: 15px; border-radius: 5px;">${message}</div>`;
    resultDiv.style.display = 'block';
    
    // Hide forms when showing result
    hideInputKaryawanForm();
    hideInputAbsenForm();
}

function updateInteractiveStatus(status) {
    const statusSpan = document.getElementById('statusInteractive');
    statusSpan.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    statusSpan.className = `status-badge status-${status}`;
}

// ========================================
// DATABASE BROWSER FUNCTIONS
// ========================================

async function loadDatabaseInfo() {
    const infoDiv = document.getElementById('databaseInfo');
    infoDiv.innerHTML = '<p style="text-align: center; padding: 20px;">Loading database information...</p>';
    
    try {
        const response = await fetch('/api/database/browse');
        const result = await response.json();
        
        if (!result.success) {
            infoDiv.innerHTML = '<div class="status-error" style="padding: 15px;">' + result.message + '</div>';
            return;
        }
        
        const db = result.database;
        
        let html = '<div class="database-header" style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px;">';
        html += '<h3>Database Information</h3>';
        html += '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 10px;">';
        html += '<div><strong>Path:</strong><br><code style="font-size: 11px;">' + db.path + '</code></div>';
        html += '<div><strong>Size:</strong><br>' + formatBytes(db.size) + '</div>';
        html += '<div><strong>Last Modified:</strong><br>' + db.modified + '</div>';
        html += '</div>';
        html += '<div style="margin-top: 10px;"><strong>Tables:</strong> ' + db.tables.length + '</div>';
        html += '</div>';
        
        // Display each table
        for (const table of db.tables) {
            html += '<div class="database-table" style="margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden;">';
            html += '<div style="background: #2c3e50; color: white; padding: 10px 15px;">';
            html += '<h3 style="margin: 0;">' + table.name.toUpperCase() + '</h3>';
            html += '<small>' + table.count + ' records</small>';
            html += '</div>';
            
            html += '<div style="padding: 15px; background: #f9f9f9;">';
            html += '<strong>Columns:</strong>';
            html += '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 5px;">';
            for (const col of table.columns) {
                const bgColor = col.primary_key ? '#3498db' : '#95a5a6';
                const keyIcon = col.primary_key ? ' [PK]' : '';
                html += '<span style="background: ' + bgColor + '; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">';
                html += col.name + ' (' + col.type + ')' + keyIcon;
                html += '</span>';
            }
            html += '</div></div>';
            
            // Display sample data
            if (table.sample_data && table.sample_data.length > 0) {
                html += '<div style="overflow-x: auto; padding: 0;">';
                html += '<table style="width: 100%; border-collapse: collapse;">';
                html += '<thead><tr style="background: #34495e; color: white;">';
                
                for (const col of table.columns) {
                    html += '<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">' + col.name + '</th>';
                }
                html += '</tr></thead><tbody>';
                
                for (let idx = 0; idx < table.sample_data.length; idx++) {
                    const row = table.sample_data[idx];
                    const bgColor = idx % 2 === 0 ? 'white' : '#f9f9f9';
                    html += '<tr style="background: ' + bgColor + ';">';
                    
                    for (const col of table.columns) {
                        const value = row[col.name] || '-';
                        html += '<td style="padding: 8px; border: 1px solid #ddd;">' + value + '</td>';
                    }
                    html += '</tr>';
                }
                html += '</tbody></table></div>';
                
                if (table.count > table.sample_data.length) {
                    html += '<div style="padding: 10px; background: #ecf0f1; text-align: center; font-size: 12px; color: #7f8c8d;">';
                    html += 'Showing ' + table.sample_data.length + ' of ' + table.count + ' records';
                    html += '</div>';
                }
            } else {
                html += '<div style="padding: 20px; text-align: center; color: #7f8c8d;">';
                html += 'No data in this table';
                html += '</div>';
            }
            
            html += '</div>';
        }
        
        infoDiv.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading database info:', error);
        infoDiv.innerHTML = '<div class="status-error" style="padding: 15px;">Error: ' + error.message + '</div>';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

