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
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', function() {
    loadPrograms();
    loadKaryawan();
    loadAbsen();
    updateStatus();
    setInterval(updateStatus, 2000); // Check status every 2 seconds
});

// Load available programs
async function loadPrograms() {
    try {
        const response = await fetch('/api/programs');
        programs = await response.json();
        
        const grid = document.getElementById('programsGrid');
        grid.innerHTML = programs.map(prog => `
            <div class="program-item" onclick="runProgram('${prog.filename}')">
                <h3>${prog.name}</h3>
                <p>${prog.description}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading programs:', error);
    }
}

// Run MPI program
async function runProgram(filename) {
    const statusText = document.getElementById('statusText');
    statusText.textContent = 'Running...';
    statusText.className = 'status-badge status-running';
    
    try {
        const response = await fetch('/api/run/' + filename.replace('.py', ''), {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'running') {
            alert('Program sedang berjalan...');
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
