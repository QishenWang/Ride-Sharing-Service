from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(label="Password",
                               max_length=50,
                               widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(label="Password",
                               max_length=50,
                               widget=forms.PasswordInput)
    password_repeat = forms.CharField(label="Repeat Password",
                                      max_length=50,
                                      widget=forms.PasswordInput)
