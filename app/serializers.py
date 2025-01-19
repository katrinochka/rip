import os
from rest_framework import serializers

from .models import *


class ProgrammsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, programm):
        if programm.image:
            return programm.image.url.replace("minio", os.getenv("IP_ADDRESS"), 1)

        return f"http://{os.getenv("IP_ADDRESS")}:9000/images/default.png"

    class Meta:
        model = Programm
        fields = ("id", "name", "status", "price", "material", "image")


class ProgrammSerializer(ProgrammsSerializer):
    class Meta:
        model = Programm
        fields = "__all__"


class ProgrammAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programm
        fields = ("name", "description", "price", "material", "image")


class ManufacturesSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Manufacture
        fields = "__all__"


class ManufactureSerializer(ManufacturesSerializer):
    programms = serializers.SerializerMethodField()

    def get_programms(self, manufacture):
        items = ProgrammManufacture.objects.filter(manufacture=manufacture)
        return [ProgrammItemSerializer(item.programm, context={"duration": item.duration}).data for item in items]


class ProgrammItemSerializer(ProgrammSerializer):
    duration = serializers.SerializerMethodField()

    def get_duration(self, _):
        return self.context.get("duration")

    class Meta:
        model = Programm
        fields = ("id", "name", "status", "price", "image", "duration")


class ProgrammManufactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammManufacture
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', "is_superuser")


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
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
