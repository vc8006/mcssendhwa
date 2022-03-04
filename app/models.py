from django.db import models
from datetime import datetime
# Create your models here.

class Bookings(models.Model):
    name = models.CharField(unique=True,max_length=70)
    email = models.EmailField(max_length=100,default='sendhwamadhurcourierservices@gmail.com')
    s_no = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class User(models.Model):
    sno = models.IntegerField(default=0)
    date = models.DateField(default=datetime.now)
    docket_no = models.CharField(max_length=20,unique=True)
    name = models.CharField(max_length=100)
    weight = models.FloatField(default=0)
    city = models.CharField(max_length=100)
    price = models.IntegerField()
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE)

class Bill(models.Model):
    billof = models.ForeignKey(Bookings,on_delete=models.CASCADE,default = 2)
    bill_no = models.IntegerField()
    date_generate = models.DateField(default=datetime.now)
    bill_date_from = models.DateField(default=datetime.now)
    bill_date_to = models.DateField(default=datetime.now)
    price = models.CharField(max_length=70)