from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'alias',
            'email',
            'profile_picture',
            'display_name_preference',
            'theme'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'display_name_preference': forms.Select(attrs={'class': 'form-select'}),
            'theme': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            display_choices = [
                ('full', f"{self.instance.first_name} {self.instance.last_name}"),
                ('username', self.instance.user_name),
            ]
            if self.instance.alias:
                display_choices.append(('alias', self.instance.alias))
            
            self.fields['display_name_preference'].widget.choices = display_choices

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email