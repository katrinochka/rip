import random

from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_programms():
    Programm.objects.create(
        name="Сварка всех типов сплавов и металлов",
        description="Сварка — процесс получения неразъёмных соединений посредством установления межатомных связей между свариваемыми частями при их местном или общем нагреве, пластическом деформировании или совместном действии того и другого. Специалист, занимающийся сварными работами, называется сварщик.",
        price=1500,
        material="металл",
        image="1.png"
    )

    Programm.objects.create(
        name="Выточка и резка металлов",
        description="Выточка металла позволяет получить заготовки только простой формы. Резка более разнообразна. При наличии необходимого оборудования она позволяет работать практически с любыми металлами и получать детали сложной формы.",
        price=2500,
        material="металл",
        image="2.png"
    )

    Programm.objects.create(
        name="3Д формовка металла",
        description="Трехмерная 3d фрезеровка металла позволяет осуществлять резку материала одновременно по трем координатам. Металлообработка на оборудовании 2,5D происходит послойно и возможна синхронно только по двум осям. Изготовление трехмерной модели на таком станке занимает больше времени и требует дополнительных усилий.",
        price=4000,
        material="металл",
        image="3.png"
    )

    Programm.objects.create(
        name="Гравировка по металлу",
        description="Гравировка на металле - это процесс нанесения текста, рисунков, декоративных узоров на поверхность металлического изделия с помощью специального оборудования. Гравировка выполняется на различных металлических предметах: таблички, шильды, ручки, медали, значки, памятные монеты, ключи, брелоки, фляжки и т. д.",
        price=2500,
        material="металл",
        image="4.png"
    )

    Programm.objects.create(
        name="Формовка дерева и фанеры",
        description="Формовочная обрезка деревьев и кустарников представляет собой процесс придания им желаемой формы. Она проводится для того, чтобы улучшить эстетические характеристики кроны дерева и её объём. В случае, если речь идёт о пересаженном дереве, она способна улучшить его приживаемость.",
        price=1000,
        material="дерево",
        image="5.png"
    )

    Programm.objects.create(
        name="Резка дерева и фанеры",
        description="Лазерная резка – это современная технология раскройки дерева, фанеры, МДФ и других твердых материалов. С ее помощью можно создать идеально ровные срезы, повторяющиеся кружева и четкие грани на обрабатываемой поверхности.",
        price=2500,
        material="дерево",
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_manufactures():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    programms = Programm.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_manufacture(status, programms, owner, moderators)

    add_manufacture(1, programms, users[0], moderators)
    add_manufacture(2, programms, users[0], moderators)
    add_manufacture(3, programms, users[0], moderators)
    add_manufacture(4, programms, users[0], moderators)
    add_manufacture(5, programms, users[0], moderators)


def add_manufacture(status, programms, owner, moderators):
    manufacture = Manufacture.objects.create()
    manufacture.status = status

    if status in [3, 4]:
        manufacture.moderator = random.choice(moderators)
        manufacture.date_complete = random_date()
        manufacture.date_formation = manufacture.date_complete - random_timedelta()
        manufacture.date_created = manufacture.date_formation - random_timedelta()
    else:
        manufacture.date_formation = random_date()
        manufacture.date_created = manufacture.date_formation - random_timedelta()

    if status == 3:
        manufacture.marriage = random.randint(0, 1)

    manufacture.name = "ЧПУ3748"

    manufacture.owner = owner

    for programm in random.sample(list(programms), 3):
        item = ProgrammManufacture(
            manufacture=manufacture,
            programm=programm,
            duration=random.randint(1, 10)
        )
        item.save()

    manufacture.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_programms()
        add_manufactures()
