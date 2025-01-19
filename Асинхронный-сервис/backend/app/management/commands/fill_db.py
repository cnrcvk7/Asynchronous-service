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


def add_substances():
    Substance.objects.create(
        name="Парацетомол",
        description="Осельтамивира фосфат — предшественник осельтамивира карбоксилата, который является ингибитором нейраминидазы. Карбоксилат образуется в организме из фосфата под действием пищеварительных ферментов.",
        number=12,
        image="1.png"
    )

    Substance.objects.create(
        name="Кремния диоксид коллоидный",
        description="Кремния диоксид коллоидный — форма диоксида кремния. В коллоидной форме применяется в медицине в качестве энтеросорбента (Полисорб МП) и наружно при гнойно-воспалительных заболеваниях мягких тканей (гнойные раны, флегмона, абсцесс, мастит).",
        number=31,
        image="2.png"
    )

    Substance.objects.create(
        name="Коповидон",
        description="Коповидон, аналог повидона, используется в качестве связующего вещества для таблеток, пленкообразователя и как часть матричного материала, используемого в формулах с контролируемым высвобождением",
        number=45,
        image="3.png"
    )

    Substance.objects.create(
        name="Крахмал прежелатинизированный",
        description="Прежелатинизированный крахмал - это крахмал из кукурузы, который прошел процессы: удаления связей между его молекулами с помощью тепловой обработки и воды, что позволяет ему стать более гигроскопичным, т. е.",
        number=61,
        image="4.png"
    )

    Substance.objects.create(
        name="Кроскармеллоза натрия",
        description="Кроскармеллоза - это натриевая соль целлюлозогликолевой кислоты со сложными эфирными связями. Согласно ГОСТ 33782-2016 является стабилизатором пищевого вещества. Ее получает путем замачивания целлюлозной пульпы в щелочи с последующим карбоксилированием хлоруксусной кислотой, дегидрированием до частичной сшивки.",
        number=4,
        image="5.png"
    )

    Substance.objects.create(
        name="Натрия стеарилфумарат",
        description="Натрия стеарил фумарат инертен и гидрофилен. Данные свойства позволяют использовать его в качестве оптимального вспомогательного вещества в производстве лекарственных форм с такими активными фармингредиентами (АФИ) как Ибупрофен, Диклофенак, Нифедипин, Омепразол, Левофлоксацин, Клопидогрел и другими.",
        number=23,
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_medicines():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    substances = Substance.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_medicine(status, substances, owner, moderators)

    add_medicine(1, substances, users[0], moderators)

    for _ in range(10):
        status = random.randint(2, 5)
        add_medicine(status, substances, users[0], moderators)


def add_medicine(status, substances, owner, moderators):
    medicine = Medicine.objects.create()
    medicine.status = status

    if status in [3, 4]:
        medicine.moderator = random.choice(moderators)
        medicine.date_complete = random_date()
        medicine.date_formation = medicine.date_complete - random_timedelta()
        medicine.date_created = medicine.date_formation - random_timedelta()
    else:
        medicine.date_formation = random_date()
        medicine.date_created = medicine.date_formation - random_timedelta()

    if status == 3:
        if random.randint(1, 10) > 3:
            medicine.dose = random.randint(1, 3)
        else:
            medicine.dose = -1

    medicine.name = "Номидес капсулы"
    medicine.description = "Номидес- это противовирусный препарат, в состав которого входит осельтамивиракарбоксилат, который ингибирует вирусы гриппа А и В. В результате этого подавляется: высвобождение вновь образованных вирусных частиц из инфицированных клеток, их проникновение в клетки эпителия дыхательных путей и дальнейшее распространение вируса в организме."

    medicine.owner = owner

    for substance in random.sample(list(substances), 3):
        item = SubstanceMedicine(
            medicine=medicine,
            substance=substance,
            weight=random.randint(1, 10)
        )
        item.save()

    medicine.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_substances()
        add_medicines()
