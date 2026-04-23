from django import forms
from .models import Member, FitnessClass, Instructor, MembershipPlan, Registration
import re

DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

class MemberForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=20, required=False)
    planid = forms.ModelChoiceField(queryset=MembershipPlan.objects.all(), label="Membership Plan")
    active = forms.BooleanField(required=False, initial=True)

    def clean_first_name(self):
        val = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z\s]+$', val):
            raise forms.ValidationError("First name must contain letters only.")
        return val

    def clean_last_name(self):
        val = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-Z\s]+$', val):
            raise forms.ValidationError("Last name must contain letters only.")
        return val

    def clean_phone(self):
        val = self.cleaned_data['phone']
        if val and not re.match(r'^\d{10}$', val):
            raise forms.ValidationError("Phone must be exactly 10 digits.")
        return val


class InstructorForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    specialty = forms.CharField(max_length=100, required=False)

    def clean_first_name(self):
        val = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z\s]+$', val):
            raise forms.ValidationError("First name must contain letters only.")
        return val

    def clean_last_name(self):
        val = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-Z\s]+$', val):
            raise forms.ValidationError("Last name must contain letters only.")
        return val


class FitnessClassForm(forms.Form):
    class_name = forms.CharField(max_length=100)
    instructorid = forms.ModelChoiceField(queryset=Instructor.objects.all(), label="Instructor")
    day_of_week = forms.ChoiceField(choices=[(d, d) for d in DAYS])
    class_time = forms.CharField(max_length=20)
    capacity = forms.IntegerField(min_value=1)
    duration = forms.IntegerField(min_value=1)


class MembershipPlanForm(forms.Form):
    plan_name = forms.CharField(max_length=100)
    price_per_month = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0)
    classes_per_month = forms.IntegerField(min_value=1)
    description = forms.CharField(widget=forms.Textarea, required=False, max_length=500)


class RegistrationForm(forms.Form):
    memberid = forms.ModelChoiceField(
        queryset=Member.objects.filter(active=True).order_by('last_name'),
        label="Member"
    )
    classid = forms.ModelChoiceField(
        queryset=FitnessClass.objects.all().order_by('class_name'),
        label="Class"
    )