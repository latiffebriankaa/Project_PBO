# BeresFile

Smart File Organizer & Renamer untuk UAS Pemrograman Berorientasi Objek (PBO).

## di kerjakan oleh :

- Latip 20240040036
- Muhammad Bagus Dwi Erlangga 20240040290
- Rassya Ramadhani Priadi 20230040142
- Mariana Kalilago 20240040225

## Latar Belakang & Inspirasi

Aplikasi ini terinspirasi dari kebiasaan saya (dan banyak pengguna komputer) yang sering kali menumpuk berbagai macam file di folder `Downloads` atau `Desktop` hingga menjadi sangat berantakan dan menyulitkan pencarian file penting di kemudian hari. Dengan BeresFile, semua file tersebut dapat diorganisasikan secara otomatis hanya dengan satu klik.

Proyek ini dibuat untuk memenuhi tugas besar UAS Pemrograman Berorientasi Objek (PBO) dengan menerapkan pilar-pilar OOP secara nyata, yaitu:

- Encapsulation
- Inheritance
- Abstract Class
- Polymorphism

## Ringkasan Proyek

BeresFile adalah aplikasi desktop berbasis Python dan Tkinter yang membantu merapikan folder secara otomatis. Aplikasi ini memindai isi folder target, mengelompokkan file berdasarkan kategorinya, memindahkan file tersebut ke subfolder kategori masing-masing, serta melakukan penggantian nama (renaming) agar format file menjadi teratur dan rapi.

## Masalah yang Diselesaikan

Banyak folder berisi file campur aduk seperti PDF tugas, screenshot, file installer, arsip, dan file kode. Akibatnya:

- file penting sulit dicari
- nama file tidak konsisten
- waktu terbuang untuk memilah file manual
- folder terasa berantakan dan tidak produktif

## Fitur Utama

- Auto-scan folder target
- Auto-pindah file ke folder kategori
- Auto-rename file dengan format terstruktur
- Mode simulasi / dry-run
- Backup log proses
- Undo untuk membatalkan proses terakhir
- AI Vision opsional untuk file gambar
- Kategori file yang lebih detail seperti PDF, Word, Spreadsheet, Presentasi, Screenshot, Logo, Installer, Config, dan lain-lain

## Struktur Project

```text
Project_PBO/
├── config.py
├── Demo aplikasi.mp4
├── main.py
├── requirements.txt
├── README.md
├── models/
│   ├── __init__.py
│   └── file_item.py
├── rules/
│   ├── __init__.py
│   ├── rule_ekstensi.py
│   ├── rule_ai.py
│   └── rule_engine.py
├── services/
│   ├── __init__.py
│   └── file_organizer.py
├── tests/
│   └── test_organizer.py
└── utils/
    ├── __init__.py
    └── logger.py
```

## Teknologi

- Python 3.8+
- Tkinter untuk GUI
- Library standar Python
- `requests` untuk fitur AI Vision opsional

## Cara Menjalankan

1. Pastikan Python sudah terpasang.
2. Buka terminal di folder project.
3. Install dependency jika ingin fitur AI opsional:

```bash
pip install -r requirements.txt
```

4. Jalankan aplikasi:

```bash
python main.py
```

### Cara Menjalankan Unit Test

Untuk menjalankan seluruh unit test guna memverifikasi kebenaran dan keandalan kode, jalankan perintah berikut pada terminal:

```bash
python -m unittest discover -s tests
```

## Cara Pakai

1. Buka aplikasi BeresFile.
2. Pilih folder target yang ingin dirapikan.
3. Aktifkan atau nonaktifkan `Dry-Run` sesuai kebutuhan.
4. Klik tombol **Jalankan**.
5. Untuk membatalkan perubahan terakhir, gunakan tombol **Undo Proses Terakhir**.

## Format Hasil File

File akan diubah menjadi format seperti:

```text
2026-06-17_nama_file_PDF.pdf
2026-06-17_catatan_Word.docx
2026-06-17_laporan_Spreadsheet.xlsx
2026-06-17_presentasi_Presentasi.pptx
2026-06-17_screenshot_Screenshot.png
2026-06-17_logo_Logo.svg
2026-06-17_setup_Installer.exe
2026-06-17_setup_Program.exe
```

## Konsep OOP yang Dipakai

### 1. Encapsulation

Digunakan pada class `FileItem` dengan atribut privat dan akses lewat property/method.

### 2. Inheritance

`RuleEkstensi` dan `RuleAI` mewarisi `RuleEngine`.

### 3. Abstract Class

`RuleEngine` memakai `ABC` dan `@abstractmethod`.

### 4. Polymorphism

`FileOrganizer` memanggil method rule dengan cara yang sama, tanpa peduli rule yang dipakai.

## Catatan AI Vision

Fitur AI Vision bersifat opsional. Jika API key belum diisi, aplikasi tetap berjalan normal menggunakan `RuleEkstensi`.

## Catatan Log dan Undo

Saat proses nyata dijalankan, aplikasi akan membuat:

- log teks di folder `BeresFile_Logs`
- manifest JSON untuk undo

Undo hanya membatalkan proses terakhir yang memiliki manifest.

## video demo

<video src="Demo aplikasi.mp4"></video>

## Lisensi

Project ini dibuat untuk keperluan pembelajaran dan sebagai Essay UAS PBO.
