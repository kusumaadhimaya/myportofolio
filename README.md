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

I used AI (ChatGPT) as a guide to help me implement the features I wanted and to better understand the code and concepts involved.

### AI Disclosure Tugas 4

I used ChatGPT to guide me in implementing the required features and to help me understand the code and concepts.

### Tugas 5

1. Debouncing adalah teknik untuk menunda pengiriman request sampai pengguna berhenti melakukan suatu aksi selama waktu tertentu. Pada fitur pencarian AJAX, debouncing penting agar request tidak dikirim setiap kali pengguna mengetik satu karakter. Dengan begitu, jumlah request ke server berkurang dan pencarian menjadi lebih efisien.

2. await digunakan untuk menunggu hingga fetch() selesai dan menghasilkan response sebelum kode berikutnya dijalankan. Jika tidak menggunakan await, fetch() langsung mengembalikan Promise, sehingga kode berikutnya dapat berjalan sebelum response dari server tersedia. Akibatnya, kita tidak dapat langsung menggunakan hasil response tersebut.

3. XSS (Cross-Site Scripting) adalah serangan dengan memasukkan kode HTML atau JavaScript berbahaya ke dalam data. AJAX/JavaScript lebih berisiko kalau data langsung dimasukkan sebagai HTML, misalnya dengan innerHTML, karena kode tersebut bisa dijalankan oleh browser. Karena itu, data dari AJAX harus di-escape atau ditampilkan dengan cara yang aman seperti textContent.

### AI Disclosure

Saya menggunakan ChatGPT hanya untuk mengarahin saya cara mengimplementasikan fitur jika saya ada kesusahan dan untuk mengertikannya.