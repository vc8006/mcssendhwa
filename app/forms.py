from django import forms
from .models import User,Bookings

class StudentRegistration(forms.ModelForm):
    class Meta:
        model = User
        fields = ['date','docket_no','name','weight','city','price']
        widgets = {
            # 'date':forms.DateInput(attrs={'class':'form-control','id':'dateid'}),
            'date': forms.DateInput(attrs={'type': 'date','class':'form-control','id':'dateid'}),
            'docket_no':forms.TextInput(attrs={'class':'form-control','id':'docket_noid'}),
            'name':forms.TextInput(attrs={'class':'form-control','id':'nameid'}),
            'weight':forms.TextInput(attrs={'class':'form-control','id':'weightid'}),
            'city':forms.TextInput(attrs={'class':'form-control','id':'cityid'}),
            'price':forms.TextInput(attrs={'class':'form-control','id':'priceid'}),
        }

class BookingRegistration(forms.ModelForm):
    class Meta:
        model = Bookings
        fields = ['name','email']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','id':'booknameid'}),
            'email':forms.TextInput(attrs={'class':'form-control','id':'bookemailid','placeholder':'sendhwamadhurcourierservices@gmail.com'}),
        }