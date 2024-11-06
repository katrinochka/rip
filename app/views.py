from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Programm, Manufacture, ProgrammManufacture


def index(request):
    programm_name = request.GET.get("programm_name", "")
    programms = Programm.objects.filter(status=1)

    if programm_name:
        programms = programms.filter(name__icontains=programm_name)

    draft_manufacture = get_draft_manufacture()

    context = {
        "programm_name": programm_name,
        "programms": programms
    }

    if draft_manufacture:
        context["programms_count"] = len(draft_manufacture.get_programms())
        context["draft_manufacture"] = draft_manufacture

    return render(request, "programms_page.html", context)


def add_programm_to_draft_manufacture(request, programm_id):
    programm_name = request.POST.get("programm_name")
    redirect_url = f"/?programm_name={programm_name}" if programm_name else "/"

    programm = Programm.objects.get(pk=programm_id)

    draft_manufacture = get_draft_manufacture()

    if draft_manufacture is None:
        draft_manufacture = Manufacture.objects.create()
        draft_manufacture.owner = get_current_user()
        draft_manufacture.date_created = timezone.now()
        draft_manufacture.save()

    if ProgrammManufacture.objects.filter(manufacture=draft_manufacture, programm=programm).exists():
        return redirect(redirect_url)

    item = ProgrammManufacture(
        manufacture=draft_manufacture,
        programm=programm
    )
    item.save()

    return redirect(redirect_url)


def programm_details(request, programm_id):
    context = {
        "programm": Programm.objects.get(id=programm_id)
    }

    return render(request, "programm_page.html", context)


def delete_manufacture(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE manufactures SET status=5 WHERE id = %s", [manufacture_id])

    return redirect("/")


def manufacture(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return render(request, "404.html")

    manufacture = Manufacture.objects.get(id=manufacture_id)
    if manufacture.status == 5:
        return render(request, "404.html")

    context = {
        "manufacture": manufacture,
    }

    return render(request, "manufacture_page.html", context)


def get_draft_manufacture():
    return Manufacture.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()