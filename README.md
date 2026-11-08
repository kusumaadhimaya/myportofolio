<div align="center">

# Kusuma Putra Abdillah Adhimaya

**NPM:** 2506656936<br>
**Class:** PBP D

</div>

---

## Table of Contents

- [Tugas 1](#tugas-1)
- [Tugas 2](#tugas-2)
- [Tugas 3](#tugas-3)
- [Tugas 4](#tugas-4)
- [Tugas 5](#tugas-5)
- [Tugas 6](#tugas-6)
- [AI Disclosure](#ai-disclosure)

---

## Tugas 1

1. Saya menggunakan elemen seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>`. Elemen ini memberikan struktur hirarki yang jelas, memudahkan keterbacaan kode, dan memperjelas pembagian area konten murni seperti seksi profil dan kartu keahlian.

2. Tantangan utamanya adalah menjaga agar tampilan tetap rapi saat berpindah dari multi-kolom desktop ke satu kolom mobile. Evaluasi dilakukan dengan memprioritaskan keterbacaan informasi utama. Pada CSS Grid (`.skills-grid`), saya menggunakan `repeat(auto-fit, minmax(260px, 1fr))` agar kartu keahlian otomatis menyesuaikan lebar layar dan menumpuk secara vertikal di mobile tanpa memicu horizontal scroll.

3. Batasan utama static web adalah konten bersifat hardcoded sehingga pembaruan data harus mengubah kode HTML secara manual. Tidak ada juga interaksi dua arah seperti formulir atau basis data. Pada iterasi selanjutnya, saya ingin menambahkan backend Django untuk mengelola data portofolio secara dinamis via database dan menyediakan formulir kontak interaktif.

**AI Disclosure:** [Lihat bagian AI Disclosure](#ai-disclosure)

---

## Tugas 2

1. Permintaan dari browser diterima oleh `urls.py` di level proyek, lalu diteruskan ke `urls.py` di aplikasi `main` untuk dicocokkan dengan path `skills/`. Path ini terhubung ke view `show_skills`, yang mengambil semua data `Skill` dari database lewat model, memasukkannya ke `context`, lalu mengirimkannya ke template `skills.html` untuk dirender menjadi HTML dan ditampilkan di browser.

2. Karena data yang disimpan di model bisa diubah lewat shell tanpa mengedit kode HTML, sehingga lebih mudah ditambah, diubah, atau dihapus, dan tidak rawan salah ketik.

3. `makemigrations` membuat berkas migrasi berdasarkan perubahan di `models.py`, sedangkan `migrate` menerapkan perubahan itu ke database. Contohnya saat saya menambahkan model `Skill`, saya menjalankan `makemigrations` untuk membuat berkas migrasinya, lalu `migrate` agar tabelnya benar-benar dibuat di database.

**AI Disclosure:** [Lihat bagian AI Disclosure](#ai-disclosure)

---

## Tugas 3

1. `ModelForm` mempermudah pembuatan form berdasarkan model Django tanpa harus membuat setiap field secara manual. `{% csrf_token %}` digunakan untuk mencegah serangan CSRF pada request `POST`.

2. JSON lebih disukai karena sintaksnya lebih sederhana, ringan, mudah dibaca, dan mudah diproses oleh aplikasi web dibandingkan XML.

3. Serialization diperlukan untuk mengubah data model Django menjadi format yang dapat dikirim melalui response JSON dan diproses oleh client.

**AI Disclosure:** [Lihat bagian AI Disclosure](#ai-disclosure)

---

## Tugas 4

Pada Tugas 4, tidak terdapat pertanyaan reflektif.

**AI Disclosure:** [Lihat bagian AI Disclosure](#ai-disclosure)

---

## Tugas 5

1. Debouncing adalah teknik untuk menunda pengiriman request sampai pengguna berhenti melakukan suatu aksi selama waktu tertentu. Pada fitur pencarian AJAX, debouncing penting agar request tidak dikirim setiap kali pengguna mengetik satu karakter. Dengan begitu, jumlah request ke server berkurang dan pencarian menjadi lebih efisien.

2. `await` digunakan untuk menunggu hingga `fetch()` selesai dan menghasilkan response sebelum kode berikutnya dijalankan. Jika tidak menggunakan `await`, `fetch()` langsung mengembalikan `Promise`, sehingga kode berikutnya dapat berjalan sebelum response dari server tersedia. Akibatnya, kita tidak dapat langsung menggunakan hasil response tersebut.

3. XSS (Cross-Site Scripting) adalah serangan dengan memasukkan kode HTML atau JavaScript berbahaya ke dalam data. AJAX/JavaScript lebih berisiko kalau data langsung dimasukkan sebagai HTML, misalnya dengan `innerHTML`, karena kode tersebut bisa dijalankan oleh browser. Karena itu, data dari AJAX harus di-escape atau ditampilkan dengan cara yang aman seperti `textContent`.

**AI Disclosure:** [Lihat bagian AI Disclosure](#ai-disclosure)

---

## Tugas 6

1. REST adalah gaya arsitektur API yang menggunakan resource dan aturan HTTP secara konsisten. Mengembalikan JSON saja belum cukup karena API juga perlu mengikuti prinsip REST, seperti menggunakan URL untuk resource dan method HTTP sesuai fungsinya. `PUT` digunakan untuk mengganti seluruh data, sedangkan `PATCH` digunakan untuk mengubah sebagian data. Contohnya, `PUT` cocok saat semua field dikirim ulang, sementara `PATCH` cocok untuk mengubah judul saja.

2. Serializer mengubah data model Django menjadi format yang dapat dikirim lewat API dan memvalidasi data yang diterima. Dibandingkan merakit dictionary secara manual dengan `JsonResponse`, `ModelSerializer` lebih ringkas dan membantu menjaga proses representasi serta validasi data tetap konsisten.

3. Autentikasi memeriksa siapa pengguna yang mengirim request, sedangkan otorisasi memeriksa tindakan apa yang boleh dilakukan pengguna tersebut. Permission class memeriksa hak akses di server untuk setiap request, sehingga aturan tetap berlaku meskipun seseorang mencoba memanggil API secara langsung. Menyembunyikan tombol di template hanya mengatur tampilan dan tidak cukup untuk melindungi data.

4. `SessionAuthentication` menggunakan session login, sehingga request yang mengubah data tetap perlu token CSRF untuk memastikan request berasal dari halaman yang sah. `force_authenticate` langsung menetapkan pengguna pada test tanpa menjalankan proses login dan pemeriksaan CSRF seperti request session biasa, jadi test tersebut saja tidak membuktikan perlindungan CSRF bekerja.

**AI Disclosure:** [Lihat bagian AI Disclosure](#ai-disclosure)

---

## AI Disclosure

While developing this portfolio, I used ChatGPT Luna 6 and Gemini 3.8 Flash to help me understand the tutorials, assignments, and concepts. I also used them to guide me while implementing my ideas, explore different solutions, keep my project files organized, and troubleshoot issues. I reviewed and verified the suggestions, then made the final decisions about what to use.

### Prompting Strategy

At the start of each task, I shared the relevant tutorial or assignment instructions to give the AI context. I then explained what I was trying to do and shared relevant code, errors, or screenshots when I needed help. I asked follow-up questions to understand the suggestions and refine them until they fit my project.

### How I Used the Suggestions

I treated AI suggestions as guidance. I reviewed the code and explanations, checked how they fit with my project, and tested changes when appropriate before deciding to keep them.

### AI Limitations

I realize that AI suggestions can have limitations and may need to be corrected. Sometimes the code or explanations do not fully match my project, or they can miss details that only become clear when I try them out. I still need to review the suggestions, check whether they make sense for my project, and test the changes to make sure they work as intended.

### Code Review and Organization

I also used AI to review my project’s structure and code organization. I asked it to help me spot possible mistakes, duplicated or unused code, and files that could be organized more clearly. I used its feedback to decide what to clean up and how to keep related parts of the project consistent.
