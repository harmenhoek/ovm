from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, FormView, DetailView
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# @method_decorator(staff_member_required, name='dispatch') #only staff can add new
# class UserCreateView(PermissionRequiredMixin, SuccessMessageMixin, LoginRequiredMixin, CreateView):
#     permission_required = 'users.is_usermoderator'
#     # model = get_user_model()
#     model = CustomUser
#
#
#     form_class = UserRegisterForm
#
#     # fields = ['first_name', 'last_name', 'email', 'is_staff']
#     template_name = 'ems_manage/user_form.html'
#
#     def form_valid(self, form):
#         form.instance.username = f"{form.instance.first_name.lower()}{form.instance.last_name.lower()}"
#
#         response = super(UserCreateView, self).form_valid(form)
#         self.object = form.save()
#         return response