from django.contrib import admin
from account.models import Account
from django.contrib.auth.admin import UserAdmin


#Този клас указва как ще изглежда информацията за потребителите от админ страницата
class AccountAdmin(UserAdmin):
    #Какво да бъде показано в колоната на админ страницата
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')

    #Създава search bar, от който можем да търсим потребители с указаните данни
    search_fields = ('email', 'username')

    #Полета, които могат да бъдат само четени, но не променяни
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)

