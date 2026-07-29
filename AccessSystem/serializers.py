from rest_framework.serializers import ModelSerializer, CharField, BooleanField
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import AbstractBaseUser
from .models import MyUser, Segment

class SegmentSerializer(ModelSerializer):
    class Meta:
        model = Segment
        fields = ['id', 'videoUrl', 'category', 'action', 'start', 'end', 'submiter', 'is_protected', 'rating']
        depth = 1

class PostSegmentSerializer(ModelSerializer):
    vote = BooleanField(default=False)
    class Meta:
        model = Segment
        fields = ['videoUrl', 'category', 'action', 'start', 'end', 'vote']

class PatchSegmentSerializer(ModelSerializer):
    vote = BooleanField(default=False)
    class Meta:
        model = Segment
        fields = '__all__'
        exculde = ['videoUrl', 'start', 'end', 'submiter']

class UserSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['email', 'name', 'surname', 'patronymic', 'password', 'groups']

class NewUserSerializer(ModelSerializer):
    repeat_password = CharField()
    class Meta:
        model = MyUser
        fields = ['email', 'name', 'surname', 'patronymic', 'password', 'repeat_password']

class LoginSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['email', 'password']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: AbstractBaseUser | TokenUser):
        token = super().get_token(user)
        token['email'] = user.email
        return token