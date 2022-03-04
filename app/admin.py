from django.contrib import admin
from .models import User,Bookings,Bill
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','name','docket_no','city')

@admin.register(Bookings)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','name','email','s_no')

@admin.register(Bill)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','bill_no')