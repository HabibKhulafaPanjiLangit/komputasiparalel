"""
Database Helper Functions
Wrapper functions untuk operasi database dengan fallback ke in-memory
"""


try:
    from database import get_session, Karyawan, Absen, Gaji
    USE_DATABASE = True
except Exception as e:
    print(f"[DB Helper] Database not available: {e}")
    raise RuntimeError("FATAL: Database tidak tersedia. Pastikan database.py dan koneksi DB siap sebelum menjalankan aplikasi!")


def get_all_karyawan():
    """Get all karyawan data"""
    if USE_DATABASE:
        session = get_session()
        try:
            karyawan_list = session.query(Karyawan).all()
            return [k.to_dict() for k in karyawan_list]
        finally:
            session.close()
    else:
        return _memory_karyawan.copy()


def add_karyawan(id, nama, jabatan, gaji_pokok):
    """Add new karyawan"""
    if USE_DATABASE:
        session = get_session()
        try:
            # Check if exists
            existing = session.query(Karyawan).filter_by(id=id).first()
            if existing:
                return False, "ID karyawan sudah ada"
            
            karyawan = Karyawan(
                id=id,
                nama=nama,
                jabatan=jabatan,
                gaji_pokok=float(gaji_pokok)
            )
            session.add(karyawan)
            session.commit()
            return True, "Karyawan berhasil ditambahkan"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    else:
        # Check duplicate
        if any(k['id'] == id for k in _memory_karyawan):
            return False, "ID karyawan sudah ada"
        
        _memory_karyawan.append({
            'id': id,
            'nama': nama,
            'jabatan': jabatan,
            'gaji_pokok': float(gaji_pokok)
        })
        return True, "Karyawan berhasil ditambahkan"


def delete_karyawan(id):
    """Delete karyawan by ID"""
    if USE_DATABASE:
        session = get_session()
        try:
            karyawan = session.query(Karyawan).filter_by(id=id).first()
            if karyawan:
                session.delete(karyawan)
                # Also delete related absen and gaji
                session.query(Absen).filter_by(id=id).delete()
                session.query(Gaji).filter_by(karyawan_id=id).delete()
                session.commit()
                return True
            return False
        finally:
            session.close()
    else:
        global _memory_karyawan, _memory_absen, _memory_gaji
        _memory_karyawan = [k for k in _memory_karyawan if k['id'] != id]
        _memory_absen = [a for a in _memory_absen if a['id'] != id]
        _memory_gaji = [g for g in _memory_gaji if g['id'] != id]
        return True


def get_all_absen():
    """Get all absen data"""
    if USE_DATABASE:
        session = get_session()
        try:
            absen_list = session.query(Absen).all()
            return [a.to_dict() for a in absen_list]
        finally:
            session.close()
    else:
        return _memory_absen.copy()


def add_absen(id, hari_masuk):
    """Add or update absen data"""
    if USE_DATABASE:
        session = get_session()
        try:
            # Check if exists, update or create
            existing = session.query(Absen).filter_by(id=id).first()
            if existing:
                existing.hari_masuk = hari_masuk
            else:
                absen = Absen(id=id, hari_masuk=hari_masuk)
                session.add(absen)
            session.commit()
            return True, "Data absen berhasil disimpan"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    else:
        # Update if exists, else append
        for a in _memory_absen:
            if a['id'] == id:
                a['hari_masuk'] = hari_masuk
                return True, "Data absen berhasil diupdate"
        
        _memory_absen.append({
            'id': id,
            'hari_masuk': hari_masuk
        })
        return True, "Data absen berhasil ditambahkan"


def get_all_gaji():
    """Get all gaji data"""
    if USE_DATABASE:
        session = get_session()
        try:
            gaji_list = session.query(Gaji).all()
            return [g.to_dict() for g in gaji_list]
        finally:
            session.close()
    else:
        return _memory_gaji.copy()


def clear_and_save_gaji(gaji_data, mode='serial', waktu=0):
    """Clear old gaji and save new calculated gaji"""
    if USE_DATABASE:
        session = get_session()
        try:
            # Clear old data
            session.query(Gaji).delete()
            
            # Add new data
            for g in gaji_data:
                gaji_obj = Gaji(
                    karyawan_id=g['id'],
                    nama=g['nama'],
                    jabatan=g['jabatan'],
                    gaji_pokok=g['gaji_pokok'],
                    hari_masuk=g['hari_masuk'],
                    total_gaji=g['total_gaji'],
                    mode_hitung=mode,
                    waktu_hitung=waktu
                )
                session.add(gaji_obj)
            
            session.commit()
            return True, "Gaji berhasil dihitung dan disimpan"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    else:
        global _memory_gaji
        _memory_gaji = gaji_data.copy()
        return True, "Gaji berhasil dihitung"


def generate_dummy_data(jumlah):
    """Generate dummy karyawan and absen data"""
    import random
    
    jabatan_list = ["Manager", "Supervisor", "Staff Senior", "Staff", "Operator"]
    nama_depan = ["Andi", "Budi", "Citra", "Deni", "Eka", "Fajar", "Gita", "Hadi", "Indra", "Joko",
                  "Kiki", "Lina", "Maya", "Nana", "Omar", "Putri", "Qori", "Rina", "Sari", "Tono"]
    nama_belakang = ["Pratama", "Wijaya", "Santoso", "Permana", "Saputra", "Kurniawan", 
                     "Putra", "Wibowo", "Setiawan", "Hidayat"]
    
    if USE_DATABASE:
        session = get_session()
        try:
            # Clear existing
            session.query(Karyawan).delete()
            session.query(Absen).delete()
            session.query(Gaji).delete()
            
            for i in range(1, jumlah + 1):
                # Add karyawan
                karyawan = Karyawan(
                    id=f"K{i:03d}",
                    nama=f"{random.choice(nama_depan)} {random.choice(nama_belakang)}",
                    jabatan=random.choice(jabatan_list),
                    gaji_pokok=random.randint(150, 500) * 1000
                )
                session.add(karyawan)
                
                # Add absen
                absen = Absen(
                    id=f"K{i:03d}",
                    hari_masuk=random.randint(15, 30)
                )
                session.add(absen)
            
            session.commit()
            return True, f"{jumlah} data berhasil di-generate"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    else:
        global _memory_karyawan, _memory_absen
        _memory_karyawan.clear()
        _memory_absen.clear()
        
        for i in range(1, jumlah + 1):
            _memory_karyawan.append({
                'id': f"K{i:03d}",
                'nama': f"{random.choice(nama_depan)} {random.choice(nama_belakang)}",
                'jabatan': random.choice(jabatan_list),
                'gaji_pokok': random.randint(150, 500) * 1000
            })
            _memory_absen.append({
                'id': f"K{i:03d}",
                'hari_masuk': random.randint(15, 30)
            })
        
        return True, f"{jumlah} data berhasil di-generate"
