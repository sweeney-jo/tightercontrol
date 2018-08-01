from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from resInput.models import Input
from django.core.exceptions import ValidationError
import pandas as pd
from django.utils.translation import ugettext_lazy as _


# registrationForm inherits from UsercreationForm
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        # cleaned data prevents any malicious sql injections/code//it is defined in parent class
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']


        if commit:
            user.save()

        return user


class EditProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = {
            'email',
            'first_name',
            'last_name',
            'password'
        }
        #exclude = {}


    
class TwentyFourHourForm(forms.Form):
    TwentyFourHour_date = forms.DateField(help_text="Enter a date before last date in db (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['TwentyFourHour_date']
        df = pd.DataFrame(
        list(Input.objects.all().values('time')))
        range_max = df['time'].max()
        range_min = df['time'].min()
        #Check date is not in past. 
        if data > range_max:
            raise ValidationError(_('Invalid date - your dataset stops at  '))
        if data < range_min:
            raise ValidationError(_('Invalid date - please pick a date within your dataset'))
        return data