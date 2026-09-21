Name : Kusuma Putra Abdillah Adhimaya

NPM : 2506656936

Class : PBP D

### Tugas 1

1. Saya menggunakan elemen seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>`. Elemen ini memberikan struktur hirarki yang jelas, memudahkan keterbacaan kode, dan memperjelas pembagian area konten murni seperti seksi profil dan kartu keahlian.

2. Tantangan utamanya adalah menjaga agar tampilan tetap rapi saat berpindah dari multi-kolom desktop ke satu kolom mobile. Evaluasi dilakukan dengan memprioritaskan keterbacaan informasi utama. Pada CSS Grid (`.skills-grid`), saya menggunakan `repeat(auto-fit, minmax(260px, 1fr))` agar kartu keahlian otomatis menyesuaikan lebar layar dan menumpuk secara vertikal di mobile tanpa memicu horizontal scroll.

3. Batasan utama static web adalah konten bersifat hardcoded sehingga pembaruan data harus mengubah kode HTML secara manual. Tidak ada juga interaksi dua arah seperti formulir atau basis data. Pada iterasi selanjutnya, saya ingin menambahkan backend Django untuk mengelola data portofolio secara dinamis via database dan menyediakan formulir kontak interaktif.

#### Pernyataan Penggunaan AI
Dalam pengerjaan Tugas 1 PBP, AI (Gemini) digunakan sebagai bantuan untuk struktur HTML5/CSS Grid. Seluruh kode dipelajari dan diimplementasikan secara mandiri.

### Tugas 2
1. Permintaan dari browser diterima oleh `urls.py` di level proyek, lalu diteruskan ke `urls.py` di aplikasi `main` untuk dicocokkan dengan path `skills/`. Path ini terhubung ke view `show_skills`, yang mengambil semua data `Skill` dari database lewat model, memasukkannya ke context, lalu mengirimkannya ke template `skills.html` untuk dirender menjadi HTML dan ditampilkan di browser.

2. Karena data yang disimpan di model bisa diubah lewat shell tanpa mengedit kode HTML, sehingga lebih mudah ditambah, diubah, atau dihapus, dan tidak rawan salah ketik.

3. `makemigrations` membuat berkas migrasi berdasarkan perubahan di `models.py`, sedangkan `migrate` menerapkan perubahan itu ke database. Contohnya saat saya menambahkan model `Skill`, saya menjalankan `makemigrations` untuk membuat berkas migrasinya, lalu `migrate` agar tabelnya benar-benar dibuat di database.

### Tugas 3

1. `ModelForm` mempermudah pembuatan form berdasarkan model Django tanpa harus membuat setiap field secara manual. `{% csrf_token %}` digunakan untuk mencegah serangan CSRF pada request `POST`.

2. JSON lebih disukai karena sintaksnya lebih sederhana, ringan, mudah dibaca, dan mudah diproses oleh aplikasi web dibandingkan XML.

3. Serialization diperlukan untuk mengubah data model Django menjadi format yang dapat dikirim melalui response JSON dan diproses oleh client.

### AI Disclosure

I used AI as a guide to help me implement the features I wanted and to better understand the code and concepts involved.