from django.shortcuts import render

programms = [
    {
        "id": 1,
        "name": "Сварка всех типов сплавов и металлов",
        "description": "Сварка — процесс получения неразъёмных соединений посредством установления межатомных связей между свариваемыми частями при их местном или общем нагреве, пластическом деформировании или совместном действии того и другого. Специалист, занимающийся сварными работами, называется сварщик.",
        "price": 1500,
        "material": "металл",
        "image": "http://192.168.0.104:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Выточка и резка металлов",
        "description": "Выточка металла позволяет получить заготовки только простой формы. Резка более разнообразна. При наличии необходимого оборудования она позволяет работать практически с любыми металлами и получать детали сложной формы.",
        "price": 2500,
        "material": "металл",
        "image": "http://192.168.0.104:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "3Д формовка металла",
        "description": "Трехмерная 3d фрезеровка металла позволяет осуществлять резку материала одновременно по трем координатам. Металлообработка на оборудовании 2,5D происходит послойно и возможна синхронно только по двум осям. Изготовление трехмерной модели на таком станке занимает больше времени и требует дополнительных усилий.",
        "price": 4000,
        "material": "металл",
        "image": "http://192.168.0.104:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Гравировка по металлу",
        "description": "Гравировка на металле - это процесс нанесения текста, рисунков, декоративных узоров на поверхность металлического изделия с помощью специального оборудования. Гравировка выполняется на различных металлических предметах: таблички, шильды, ручки, медали, значки, памятные монеты, ключи, брелоки, фляжки и т. д.",
        "price": 2500,
        "material": "металл",
        "image": "http://192.168.0.104:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Формовка дерева и фанеры",
        "description": "Формовочная обрезка деревьев и кустарников представляет собой процесс придания им желаемой формы. Она проводится для того, чтобы улучшить эстетические характеристики кроны дерева и её объём. В случае, если речь идёт о пересаженном дереве, она способна улучшить его приживаемость.",
        "price": 1000,
        "material": "дерево",
        "image": "http://192.168.0.104:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Резка дерева и фанеры",
        "description": "Лазерная резка – это современная технология раскройки дерева, фанеры, МДФ и других твердых материалов. С ее помощью можно создать идеально ровные срезы, повторяющиеся кружева и четкие грани на обрабатываемой поверхности.",
        "price": 2500,
        "material": "дерево",
        "image": "http://192.168.0.104:9000/images/6.png"
    }
]

draft_manufacture = {
    "id": 123,
    "status": "Черновик",
    "date_created": "27 октября 2024г",
    "name": "ЧПУ3748",
    "date": "4 ноября 2024г",
    "programms": [
        {
            "id": 1,
            "value": 15
        },
        {
            "id": 2,
            "value": 25
        },
        {
            "id": 3,
            "value": 30
        }
    ]
}


def getProgrammById(programm_id):
    for programm in programms:
        if programm["id"] == programm_id:
            return programm


def getProgramms():
    return programms


def searchProgramms(programm_name):
    res = []

    for programm in programms:
        if programm_name.lower() in programm["name"].lower():
            res.append(programm)

    return res


def getDraftManufacture():
    return draft_manufacture


def getManufactureById(manufacture_id):
    return draft_manufacture


def index(request):
    programm_name = request.GET.get("programm_name", "")
    programms = searchProgramms(programm_name) if programm_name else getProgramms()
    draft_manufacture = getDraftManufacture()

    context = {
        "programms": programms,
        "programm_name": programm_name,
        "programms_count": len(draft_manufacture["programms"]),
        "draft_manufacture": draft_manufacture
    }

    return render(request, "programms_page.html", context)


def programm(request, programm_id):
    context = {
        "id": programm_id,
        "programm": getProgrammById(programm_id),
    }

    return render(request, "programm_page.html", context)


def manufacture(request, manufacture_id):
    manufacture = getManufactureById(manufacture_id)
    programms = [
        {**getProgrammById(programm["id"]), "value": programm["value"]}
        for programm in manufacture["programms"]
    ]

    context = {
        "manufacture": manufacture,
        "programms": programms
    }

    return render(request, "manufacture_page.html", context)
