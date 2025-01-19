import random
import requests
from datetime import timedelta
import uuid

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


def get_draft_medicine(request):
    user = identity_user(request)

    if user is None:
        return None

    medicine = Medicine.objects.filter(owner=user).filter(status=1).first()

    return medicine


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'substance_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_substances(request):
    substance_name = request.GET.get("substance_name", "")

    substances = Substance.objects.filter(status=1)

    if substance_name:
        substances = substances.filter(name__icontains=substance_name)

    serializer = SubstancesSerializer(substances, many=True)

    draft_medicine = get_draft_medicine(request)

    resp = {
        "substances": serializer.data,
        "substances_count": SubstanceMedicine.objects.filter(medicine=draft_medicine).count() if draft_medicine else None,
        "draft_medicine_id": draft_medicine.pk if draft_medicine else None
    }

    return Response(resp)


@api_view(["GET"])
def get_substance_by_id(request, substance_id):
    if not Substance.objects.filter(pk=substance_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    substance = Substance.objects.get(pk=substance_id)
    serializer = SubstanceSerializer(substance)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=SubstanceSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_substance(request, substance_id):
    if not Substance.objects.filter(pk=substance_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    substance = Substance.objects.get(pk=substance_id)

    serializer = SubstanceSerializer(substance, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=SubstanceAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_substance(request):
    serializer = SubstanceAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Substance.objects.create(**serializer.validated_data)

    substances = Substance.objects.filter(status=1)
    serializer = SubstancesSerializer(substances, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_substance(request, substance_id):
    if not Substance.objects.filter(pk=substance_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    substance = Substance.objects.get(pk=substance_id)
    substance.status = 2
    substance.save()

    substance = Substance.objects.filter(status=1)
    serializer = SubstanceSerializer(substance, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_substance_to_medicine(request, substance_id):
    if not Substance.objects.filter(pk=substance_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    substance = Substance.objects.get(pk=substance_id)

    draft_medicine = get_draft_medicine(request)

    if draft_medicine is None:
        draft_medicine = Medicine.objects.create()
        draft_medicine.date_created = timezone.now()
        draft_medicine.owner = identity_user(request)
        draft_medicine.save()

    if SubstanceMedicine.objects.filter(medicine=draft_medicine, substance=substance).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = SubstanceMedicine.objects.create()
    item.medicine = draft_medicine
    item.substance = substance
    item.save()

    serializer = MedicineSerializer(draft_medicine)
    return Response(serializer.data["substances"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_substance_image(request, substance_id):
    if not Substance.objects.filter(pk=substance_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    substance = Substance.objects.get(pk=substance_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    substance.image = image
    substance.save()

    serializer = SubstanceSerializer(substance)

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
def search_medicines(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    medicines = Medicine.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        medicines = medicines.filter(owner=user)

    if status_id > 0:
        medicines = medicines.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        medicines = medicines.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        medicines = medicines.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = MedicinesSerializer(medicines, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_medicine_by_id(request, medicine_id):
    user = identity_user(request)

    if not Medicine.objects.filter(pk=medicine_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    medicine = Medicine.objects.get(pk=medicine_id)

    if not user.is_superuser and medicine.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MedicineSerializer(medicine)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=MedicineSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_medicine(request, medicine_id):
    user = identity_user(request)

    if not Medicine.objects.filter(pk=medicine_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    medicine = Medicine.objects.get(pk=medicine_id)
    serializer = MedicineSerializer(medicine, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsRemoteService])
def update_dose(request, medicine_id):
    if not Medicine.objects.filter(pk=medicine_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    medicine = Medicine.objects.get(pk=medicine_id)

    medicine.dose = request.data.get("value")
    medicine.save()

    serializer = MedicineSerializer(medicine, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, medicine_id):
    user = identity_user(request)

    if not Medicine.objects.filter(pk=medicine_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    medicine = Medicine.objects.get(pk=medicine_id)

    if medicine.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    medicine.status = 2
    medicine.date_formation = timezone.now()
    medicine.save()

    serializer = MedicineSerializer(medicine)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=UpdateMedicineStatusAdminSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, medicine_id):
    if not Medicine.objects.filter(pk=medicine_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    medicine = Medicine.objects.get(pk=medicine_id)

    if medicine.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        calculate_dose(medicine_id)

    medicine.status = request_status
    medicine.date_complete = timezone.now()
    medicine.moderator = identity_user(request)
    medicine.save()

    serializer = MedicineSerializer(medicine)

    return Response(serializer.data)


def calculate_dose(medicine_id):
    data = {
        "medicine_id": medicine_id
    }

    requests.post("http://remote_service:8080/calc_dose/", json=data, timeout=3)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_medicine(request, medicine_id):
    user = identity_user(request)

    if not Medicine.objects.filter(pk=medicine_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    medicine = Medicine.objects.get(pk=medicine_id)

    if medicine.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    medicine.status = 5
    medicine.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_substance_from_medicine(request, medicine_id, substance_id):
    user = identity_user(request)

    if not Medicine.objects.filter(pk=medicine_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not SubstanceMedicine.objects.filter(medicine_id=medicine_id, substance_id=substance_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SubstanceMedicine.objects.get(medicine_id=medicine_id, substance_id=substance_id)
    item.delete()

    medicine = Medicine.objects.get(pk=medicine_id)

    serializer = MedicineSerializer(medicine)
    substances = serializer.data["substances"]

    return Response(substances)


@swagger_auto_schema(method='PUT', request_body=SubstanceMedicineSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_substance_in_medicine(request, medicine_id, substance_id):
    user = identity_user(request)

    if not Medicine.objects.filter(pk=medicine_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not SubstanceMedicine.objects.filter(substance_id=substance_id, medicine_id=medicine_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SubstanceMedicine.objects.get(substance_id=substance_id, medicine_id=medicine_id)

    serializer = SubstanceMedicineSerializer(item, data=request.data, partial=True)

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
