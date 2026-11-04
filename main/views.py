from django.shortcuts import render


def show_main(request):
    context = {
        "name": "Kusuma Putra Abdillah Adhimaya",
        "npm": "2506656936",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada web development."
        ),
        "last_login": request.COOKIES.get(
            "last_login",
            "Belum ada sesi login / Cookie tidak ditemukan",
        ),
    }
    return render(request, "index.html", context)
