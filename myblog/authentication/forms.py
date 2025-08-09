from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username...'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address...'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password...'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat password...'}))


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username...'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password...'}))


class PasswordChange(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Your old password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Your new password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Your new password repeat'}))


class PasswordReset(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Your email address...'}))
