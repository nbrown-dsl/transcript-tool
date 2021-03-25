from django.forms import ModelForm,DateInput,Textarea,forms
from django import forms
from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple
from .models import *

class DateInput(DateInput):
    input_type = 'date'

class entityForm(ModelForm):
    abtract = True

class TaskForm(entityForm):
    class Meta:
        model = Task
        fields = "__all__"

class UsertaskForm(entityForm):
    class Meta:
        model = Usertask
        exclude = ['name']

class gradeForm(entityForm):
    class Meta:
        model = grade
        fields = "__all__"

class systemForm(entityForm):
    class Meta:
        model = System
        fields = '__all__'

class roleForm(entityForm):
    class Meta:
        model = Role
        fields = '__all__'

class profileForm(entityForm):
    class Meta:
        model = Profile
        exclude = ['name']
        
class requirementForm(entityForm):
    class Meta:
        model = Requirement
        fields = '__all__'