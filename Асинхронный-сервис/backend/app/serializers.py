import os

from rest_framework import serializers

from .models import *


class SubstancesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, substance):
        if substance.image:
            return substance.image.url.replace("minio", os.getenv("IP_ADDRESS"), 1)

        return f"http://{os.getenv("IP_ADDRESS")}:9000/images/default.png"

    class Meta:
        model = Substance
        fields = ("id", "name", "status", "number", "image")


class SubstanceSerializer(SubstancesSerializer):
    class Meta:
        model = Substance
        fields = "__all__"


class SubstanceAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substance
        fields = ("name", "description", "number", "image")


class MedicinesSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Medicine
        fields = "__all__"


class MedicineSerializer(MedicinesSerializer):
    substances = serializers.SerializerMethodField()

    def get_substances(self, medicine):
        items = SubstanceMedicine.objects.filter(medicine=medicine)
        return [SubstanceItemSerializer(item.substance, context={"weight": item.weight}).data for item in items]


class SubstanceItemSerializer(SubstanceSerializer):
    weight = serializers.SerializerMethodField()

    def get_weight(self, _):
        return self.context.get("weight")

    class Meta:
        model = Substance
        fields = ("id", "name", "status", "number", "image", "weight")


class SubstanceMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubstanceMedicine
        fields = "__all__"


class UpdateMedicineStatusAdminSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
