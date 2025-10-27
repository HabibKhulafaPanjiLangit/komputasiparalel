# 🚀 Panduan Deploy MPI Payroll System - GRATIS

Aplikasi ini bisa di-deploy ke beberapa platform gratis. Berikut panduannya:

---

## 1️⃣ Railway.app (RECOMMENDED) ⭐

**Keunggulan:**
- ✅ Gratis $5 credit/bulan (cukup untuk 1 app)
- ✅ Auto deploy dari GitHub
- ✅ Support MPI via nixpacks
- ✅ Setup paling mudah

**Cara Deploy:**

1. **Buat Akun Railway:**
   - Kunjungi https://railway.app
   - Sign up dengan GitHub account
   - Verifikasi email

2. **Deploy dari GitHub:**
   - Klik "New Project"
   - Pilih "Deploy from GitHub repo"
   - Pilih repository: `HabibKhulafaPanjiLangit/komputasiparalel`
   - Railway akan auto-detect settings dari `nixpacks.toml`

3. **Add Environment Variables (Opsional):**
   - PORT akan otomatis di-set oleh Railway
   - Tidak perlu konfigurasi tambahan

4. **Deploy:**
   - Railway akan otomatis build dan deploy
   - Tunggu 3-5 menit
   - URL public akan muncul (contoh: `https://your-app.up.railway.app`)

**Status:** ✅ Sudah siap deploy!

---

## 2️⃣ Render.com (Alternative)

**Keunggulan:**
- ✅ Gratis untuk web services
- ✅ Auto deploy dari GitHub
- ✅ 750 jam gratis/bulan
- ⚠️ Sleep after 15 menit tidak ada traffic (free tier)

**Cara Deploy:**

1. **Buat Akun Render:**
   - Kunjungi https://render.com
   - Sign up dengan GitHub

2. **Create New Web Service:**
   - Dashboard → "New +"
   - Pilih "Web Service"
   - Connect repository: `komputasiparalel`

3. **Konfigurasi:**
   - Name: `mpi-payroll-system`
   - Region: `Singapore` (terdekat)
   - Branch: `main`
   - Build Command: `bash render-build.sh`
   - Start Command: `python web_server.py`
   - Instance Type: `Free`

4. **Deploy:**
   - Klik "Create Web Service"
   - Tunggu build selesai (5-10 menit)
   - URL: `https://mpi-payroll-system.onrender.com`

**Status:** ✅ Sudah siap deploy!

---

## 3️⃣ Docker + Fly.io (Advanced)

**Keunggulan:**
- ✅ Gratis untuk 1 app
- ✅ Support Docker
- ✅ Global CDN

**Cara Deploy:**

1. **Install Fly CLI:**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login & Init:**
   ```bash
   fly auth login
   cd d:\mpi-demo
   fly launch
   ```

3. **Deploy:**
   ```bash
   fly deploy
   ```

**Status:** ✅ Dockerfile sudah siap!

---

## 📋 Files yang Sudah Dibuat untuk Deploy

✅ `Procfile` - Untuk Railway/Heroku
✅ `nixpacks.toml` - Konfigurasi Railway
✅ `Dockerfile` - Untuk Docker-based deployment
✅ `render-build.sh` - Build script untuk Render
✅ `render.yaml` - Konfigurasi Render
✅ `runtime.txt` - Python version
✅ `.dockerignore` - Files to ignore di Docker

---

## 🎯 Rekomendasi Platform

| Platform | Gratis? | MPI Support | Setup | Uptime |
|----------|---------|-------------|-------|---------|
| **Railway** | ✅ $5/bulan | ✅ Yes | ⭐⭐⭐ Easy | 24/7 |
| **Render** | ✅ Yes | ✅ Yes | ⭐⭐ Medium | 15 min idle* |
| **Fly.io** | ✅ Yes | ✅ Yes | ⭐ Advanced | 24/7 |

*Render free tier sleep setelah 15 menit idle, butuh waktu startup ~30 detik

---

## 🔥 Quick Start - Railway (Tercepat)

1. Push code ke GitHub (sudah ✅)
2. Login ke https://railway.app
3. New Project → Deploy from GitHub
4. Pilih repo `komputasiparalel`
5. Done! 🎉

URL akan tersedia dalam 3-5 menit.

---

## 📝 Catatan Penting

1. **MPI Processes:** Di production, batasi jumlah processes MPI (max 4) karena keterbatasan resources free tier

2. **File Storage:** CSV files akan hilang saat restart di free tier. Untuk persistent storage:
   - Railway: Tambah Volume (berbayar)
   - Render: Gunakan database PostgreSQL (gratis)

3. **Performance:** Free tier memiliki RAM terbatas (~512MB), cocok untuk demo dan testing

4. **Custom Domain:** Bisa ditambahkan di semua platform (gratis di Railway & Render)

---

## 🆘 Troubleshooting

**Error: MPI not found**
- Railway: Pastikan `nixpacks.toml` ada
- Render: Cek `render-build.sh` executable

**Error: Port binding**
- Pastikan `web_server.py` menggunakan `os.environ.get('PORT', 5000)`

**Build timeout**
- Normal untuk first deployment (5-10 menit)
- Coba lagi jika gagal

---

## 📞 Support

Jika ada masalah saat deploy, cek:
- Railway Logs: Dashboard → Deployments → Logs
- Render Logs: Dashboard → Logs tab
- GitHub Issues: Report di repository

---

**Happy Deploying! 🚀**
