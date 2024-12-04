import random
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_manufacture():
    return Manufacture.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_programms(request):
    programm_name = request.GET.get("programm_name", "")

    programms = Programm.objects.filter(status=1)

    if programm_name:
        programms = programms.filter(name__icontains=programm_name)

    serializer = ProgrammsSerializer(programms, many=True)
    
    draft_manufacture = get_draft_manufacture()

    resp = {
        "programms": serializer.data,
        "programms_count": ProgrammManufacture.objects.filter(manufacture=draft_manufacture).count() if draft_manufacture else None,
        "draft_manufacture": draft_manufacture.pk if draft_manufacture else None
    }

    return Response(resp)


@api_view(["GET"])
def get_programm_by_id(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)
    serializer = ProgrammSerializer(programm)

    return Response(serializer.data)


@api_view(["PUT"])
def update_programm(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)

    serializer = ProgrammSerializer(programm, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_programm(request):
    serializer = ProgrammSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Programm.objects.create(**serializer.validated_data)

    programms = Programm.objects.filter(status=1)
    serializer = ProgrammSerializer(programms, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_programm(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)
    programm.status = 2
    programm.save()

    programms = Programm.objects.filter(status=1)
    serializer = ProgrammSerializer(programms, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_programm_to_manufacture(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)

    draft_manufacture = get_draft_manufacture()

    if draft_manufacture is None:
        draft_manufacture = Manufacture.objects.create()
        draft_manufacture.owner = get_user()
        draft_manufacture.date_created = timezone.now()
        draft_manufacture.save()

    if ProgrammManufacture.objects.filter(manufacture=draft_manufacture, programm=programm).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = ProgrammManufacture.objects.create()
    item.manufacture = draft_manufacture
    item.programm = programm
    item.save()

    serializer = ManufactureSerializer(draft_manufacture)
    return Response(serializer.data["programms"])


@api_view(["POST"])
def update_programm_image(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)

    image = request.data.get("image")
    if image is not None:
        programm.image = image
        programm.save()

    serializer = ProgrammSerializer(programm)

    return Response(serializer.data)


@api_view(["GET"])
def search_manufactures(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    manufactures = Manufacture.objects.exclude(status__in=[1, 5])

    if status > 0:
        manufactures = manufactures.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        manufactures = manufactures.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        manufactures = manufactures.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = ManufacturesSerializer(manufactures, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_manufacture_by_id(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)
    serializer = ManufactureSerializer(manufacture, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_manufacture(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)
    serializer = ManufactureSerializer(manufacture, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    if manufacture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    manufacture.status = 2
    manufacture.date_formation = timezone.now()
    manufacture.save()

    serializer = ManufactureSerializer(manufacture, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    if manufacture.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        manufacture.marriage = random.randint(0, 1)

    manufacture.date_complete = timezone.now()
    manufacture.status = request_status
    manufacture.moderator = get_moderator()
    manufacture.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_manufacture(request, manufacture_id):
    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    if manufacture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    manufacture.status = 5
    manufacture.save()

    serializer = ManufactureSerializer(manufacture, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_programm_from_manufacture(request, manufacture_id, programm_id):
    if not ProgrammManufacture.objects.filter(manufacture_id=manufacture_id, programm_id=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProgrammManufacture.objects.get(manufacture_id=manufacture_id, programm_id=programm_id)
    item.delete()

    items = ProgrammManufacture.objects.filter(manufacture_id=manufacture_id)
    data = [ProgrammItemSerializer(item.programm, context={"duration": item.duration}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_programm_in_manufacture(request, manufacture_id, programm_id):
    if not ProgrammManufacture.objects.filter(programm_id=programm_id, manufacture_id=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProgrammManufacture.objects.get(programm_id=programm_id, manufacture_id=manufacture_id)

    serializer = ProgrammManufactureSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)