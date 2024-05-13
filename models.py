from tortoise import fields
from tortoise.models import Model
from enum import Enum


class UserType(Enum):
    CUSTOMER = "заказчик"
    CLIENT = "клиент"
    ADMIN = "админ"

class BriefStatus(Enum):
    NEW = "новый"
    IN_WORK = "в работе"
    COMPLETED = "завершен"    

class BriefType(Enum):
    DESIGN = "проектирование"
    CONFIGURATION = "комплектация"
    READY_VERSION = "готовый вариант"

class AnswerType(Enum):
    TEXT = "текст"
    CHOICE = "выбор"
    FILE = "файл" 
    COMBO = "комбинированный"


class User(Model):
    id = fields.IntField(pk=True)
    telegram_user_id = fields.IntField(unique=True)
    telegram_fullname = fields.CharField(max_length=255, null=True)
    name = fields.CharField(max_length=155, null=True)
    username = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, null=True)
    location = fields.CharField(max_length=255, null=True)
    user_type = fields.CharEnumField(
        enum_type=UserType,
        default=UserType.CUSTOMER,
    )

    def __str__(self):
        return f"{self.fullname} ({self.username})"


class Brief(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=True)
    status = fields.CharEnumField(
        enum_type=BriefStatus,
        default=BriefStatus.NEW
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField('models.User', related_name='briefs')
    brief_type = fields.CharEnumField(
        enum_type=BriefType,
        # default=null
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.brief_type})"


class Question(Model):
    id = fields.IntField(pk=True)
    question = fields.CharField(max_length=855)
    image_url = fields.CharField(max_length=855)
    consultation_url = fields.CharField(max_length=855)
    answer_type = fields.CharEnumField(
        enum_type=AnswerType,
        # default=null
        null=True
    )
    answer_options = fields.JSONField(null=True)
    next_question_id = fields.IntField(null=True)

    def __str__(self):
        return f"{self.question}"


class Answer(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='answers')
    brief = fields.ForeignKeyField('models.Brief', related_name='answers')
    question = fields.ForeignKeyField('models.Question', related_name='answers')
    answer = fields.TextField()

    def __str__(self):
        return f"{self.answer}"
    

class UserState(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='state')
    current_question = fields.ForeignKeyField('models.Question', related_name='state', null=True)
    context_data = fields.JSONField(default=dict)  # Это поле может хранить любые дополнительные данные

    class Meta:
        table = "user_states"