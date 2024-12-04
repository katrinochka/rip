from rest_framework import serializers

from .models import *


class ProgrammsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, programm):
        if programm.image:
            return programm.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Programm
        fields = ("id", "name", "status", "price", "image")


class ProgrammSerializer(ProgrammsSerializer):
    class Meta(ProgrammsSerializer.Meta):
        fields = "__all__"


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
        fields = ('id', 'email', 'username')


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
