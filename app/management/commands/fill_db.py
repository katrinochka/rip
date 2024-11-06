import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


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

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_manufactures():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    programms = Programm.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_manufacture(status, programms, owner, moderators)

    add_manufacture(1, programms, users[0], moderators)
    add_manufacture(2, programms, users[0], moderators)

    print("Заявки добавлены")


def add_manufacture(status, programms, owner, moderators):
    manufacture = Manufacture.objects.create()
    manufacture.status = status

    if manufacture.status in [3, 4]:
        manufacture.date_complete = random_date()
        manufacture.date_formation = manufacture.date_complete - random_timedelta()
        manufacture.date_created = manufacture.date_formation - random_timedelta()
    else:
        manufacture.date_formation = random_date()
        manufacture.date_created = manufacture.date_formation - random_timedelta()

    manufacture.owner = owner
    manufacture.moderator = random.choice(moderators)

    manufacture.name = "ЧПУ3748"
    manufacture.date = random_date()

    for programm in random.sample(list(programms), 3):
        item = ProgrammManufacture(
            manufacture=manufacture,
            programm=programm,
            value=random.randint(15, 60)
        )
        item.save()

    manufacture.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_programms()
        add_manufactures()
