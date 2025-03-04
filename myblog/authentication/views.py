from django.shortcuts import render
from .forms import SignupForm, LoginForm, PasswordChange, PasswordReset
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfullly")
            return redirect('/')

    else:
        form = SignupForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChange(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important to update the session with the new password hash
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('/')  # Redirect to a success page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChange(request.user)
    return render(request, 'registration/passwordChange.html', {'form': form})


def passwordReset(request):
    if request.method == 'POST':
        form = PasswordReset(request.POST)
        if form.is_valid():
            messages.success(request, 'Check your Mail')
            return redirect('/')  # Redirect to a success page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordReset()
    return render(request, 'registration/reset_password.html', {'form': form})
