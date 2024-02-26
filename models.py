from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    telegram_user_id = fields.IntField(unique=True)
    fullname = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, null=True)
    location = fields.CharField(max_length=255, null=True)


class Question(Model):
    id = fields.IntField(pk=True)
    question = fields.CharField(max_length=855)
    answer_option = fields.CharField(max_length=555, null=True)
    image = fields.CharField(max_length=255, null=True)
    consalting_link = fields.CharField(max_length=455, null=True)


class Answer(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='answers')
    question = fields.ForeignKeyField('models.Question', related_name='answers')
    answer = fields.TextField()
    date = fields.DatetimeField(auto_now_add=True)