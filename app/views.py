import random
from datetime import datetime, timedelta
import uuid
from functools import partial

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_manufacture(request):
    user = identity_user(request)

    if user is None:
        return None

    manufacture = Manufacture.objects.filter(owner=user).filter(status=1).first()

    return manufacture


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'programm_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_programms(request):
    programm_name = request.GET.get("programm_name", "")

    programms = Programm.objects.filter(status=1)

    if programm_name:
        programms = programms.filter(name__icontains=programm_name)

    serializer = ProgrammsSerializer(programms, many=True)

    draft_manufacture = get_draft_manufacture(request)

    resp = {
        "programms": serializer.data,
        "programms_count": ProgrammManufacture.objects.filter(manufacture=draft_manufacture).count() if draft_manufacture else None,
        "draft_manufacture_id": draft_manufacture.pk if draft_manufacture else None
    }

    return Response(resp)


@api_view(["GET"])
def get_programm_by_id(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)
    serializer = ProgrammSerializer(programm)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ProgrammSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_programm(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)

    serializer = ProgrammSerializer(programm, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=ProgrammAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_programm(request):
    serializer = ProgrammAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Programm.objects.create(**serializer.validated_data)

    programms = Programm.objects.filter(status=1)
    serializer = ProgrammsSerializer(programms, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_programm(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)
    programm.status = 2
    programm.save()

    programm = Programm.objects.filter(status=1)
    serializer = ProgrammSerializer(programm, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_programm_to_manufacture(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)

    draft_manufacture = get_draft_manufacture(request)

    if draft_manufacture is None:
        draft_manufacture = Manufacture.objects.create()
        draft_manufacture.date_created = timezone.now()
        draft_manufacture.owner = identity_user(request)
        draft_manufacture.save()

    if ProgrammManufacture.objects.filter(manufacture=draft_manufacture, programm=programm).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = ProgrammManufacture.objects.create()
    item.manufacture = draft_manufacture
    item.programm = programm
    item.save()

    serializer = ManufactureSerializer(draft_manufacture)
    return Response(serializer.data["programms"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_programm_image(request, programm_id):
    if not Programm.objects.filter(pk=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    programm = Programm.objects.get(pk=programm_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    programm.image = image
    programm.save()

    serializer = ProgrammSerializer(programm)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_manufactures(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    manufactures = Manufacture.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        manufactures = manufactures.filter(owner=user)

    if status_id > 0:
        manufactures = manufactures.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        manufactures = manufactures.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        manufactures = manufactures.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = ManufacturesSerializer(manufactures, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_manufacture_by_id(request, manufacture_id):
    user = identity_user(request)

    if not Manufacture.objects.filter(pk=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    if not user.is_superuser and manufacture.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ManufactureSerializer(manufacture)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ManufactureSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_manufacture(request, manufacture_id):
    user = identity_user(request)

    if not Manufacture.objects.filter(pk=manufacture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)
    serializer = ManufactureSerializer(manufacture, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, manufacture_id):
    user = identity_user(request)

    if not Manufacture.objects.filter(pk=manufacture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    if manufacture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    manufacture.status = 2
    manufacture.date_formation = timezone.now()
    manufacture.save()

    serializer = ManufactureSerializer(manufacture)

    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(["PUT"])
@permission_classes([IsModerator])
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

    manufacture.status = request_status
    manufacture.date_complete = timezone.now()
    manufacture.moderator = identity_user(request)
    manufacture.save()

    serializer = ManufactureSerializer(manufacture)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_manufacture(request, manufacture_id):
    user = identity_user(request)

    if not Manufacture.objects.filter(pk=manufacture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    if manufacture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    manufacture.status = 5
    manufacture.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_programm_from_manufacture(request, manufacture_id, programm_id):
    user = identity_user(request)

    if not Manufacture.objects.filter(pk=manufacture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ProgrammManufacture.objects.filter(manufacture_id=manufacture_id, programm_id=programm_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProgrammManufacture.objects.get(manufacture_id=manufacture_id, programm_id=programm_id)
    item.delete()

    manufacture = Manufacture.objects.get(pk=manufacture_id)

    serializer = ManufactureSerializer(manufacture)
    programms = serializer.data["programms"]

    return Response(programms)


@swagger_auto_schema(method='PUT', request_body=ProgrammManufactureSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_programm_in_manufacture(request, manufacture_id, programm_id):
    user = identity_user(request)

    if not Manufacture.objects.filter(pk=manufacture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ProgrammManufacture.objects.filter(programm_id=programm_id, manufacture_id=manufacture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProgrammManufacture.objects.get(programm_id=programm_id, manufacture_id=manufacture_id)

    serializer = ProgrammManufactureSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
