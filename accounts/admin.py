from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Инлайн для профиля в админке пользователя
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'

# Расширяем стандартную админку User
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Отменяем регистрацию стандартного User
admin.site.unregister(User)
# Регистрируем User с расширенной админкой
admin.site.register(User, UserAdmin)

# Опционально: регистрируем отдельно, если хочешь видеть профили отдельно
# admin.site.register(UserProfile)