from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import MyUser, Segment

# Django Admin

class UserCreationForm(forms.ModelForm):
    '''Форма для создания пользователя.'''

    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ['email', 'name', 'surname']

    def check_two_passwords(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Введённые пароли не совпадают!")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit: user.save()
        return user


class UserChangeForm(forms.ModelForm):
    '''Форма для изменения данных пользователя. Подменяет поле ввода пароля на недоступное для ввода поле хеша этого пароля.'''

    password = ReadOnlyPasswordHashField()
    class Meta:
        model = MyUser
        fields = ['email', 'password', 'name', 'surname', 'patronymic']


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['email', 'name', 'surname', 'patronymic']
    list_filter = ['is_superuser']
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Personal info', {'fields': ['name', 'surname', 'patronymic']}),
        ('Permissions', {'fields': ['is_superuser', 'is_active']})
    ]
    add_fieldsets = [(None, {
        'classes': ['wide'],
        'fields': ['email', 'name', 'surname', 'patronymic', 'password1', 'password2']
    })]
    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = []


# Регистрация нового администратора
admin.site.register(MyUser, UserAdmin)
admin.site.register(Segment)


# group_admin, _ = Group.objects.get_or_create(name='Администраторы')
# group_moder, _ = Group.objects.get_or_create(name='Модераторы')
# group_ordinary, _ = Group.objects.get_or_create(name='Обычные пользователи')


# perm_protect_segment = Permission.objects.get(codename='protect_segment')
# perm_change_segment = Permission.objects.get(codename='change_segment')
# perm_delete_segment = Permission.objects.get(codename='delete_segment')
# common_permissions_segment = (
#     Permission.objects.get(codename='change_category'),
#     Permission.objects.get(codename='change_action'),
#     Permission.objects.get(codename='vote')
# )

# group_ordinary.permissions.add(*common_permissions_segment)
# group_moder.permissions.add(*common_permissions_segment, perm_protect_segment)
# group_admin.permissions.add(*common_permissions_segment, perm_protect_segment, perm_delete_segment)

# # group_moder.permissions.add(perm_protect_segment)
# # group_admin.permissions.add(perm_protect_segment, perm_delete_segment)


# user_admin = MyUser.objects.create_superuser(email='admin@example.com', name='Михаил', surname='К', password='pass1')
# user_moder = MyUser.objects.create_user(email='moder@example.com', name='Григорий', surname='К', password='pass2')
# user_ordinary = MyUser.objects.create_user(email='ordinary@example.com', name='Василий', surname='Т', patronymic='Иванович', password='pass3')

# group_admin.user_set.add(user_admin)
# group_moder.user_set.add(user_moder)
# group_ordinary.user_set.add(user_ordinary)
