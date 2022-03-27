from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Log
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy

from django.contrib import messages

class LogListView(LoginRequiredMixin, ListView):
    model = Log
    ordering = ['added_on']
    template_name = 'logbook/log_list.html'

class LogDetailView(LoginRequiredMixin, DetailView):
    model = Log
    template_name = 'logbook/log_detail.html'

class LogCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Log
    success_message = "Log sucessvol toegevoegd."
    fields = ['log', 'file1', 'file2']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button'] = 'Add'
        return context

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

class LogUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Log
    success_message = "Log sucessvol bijgewerkt."
    fields = ['log', 'file1', 'file2']

    def test_func(self):
        log = self.get_object()
        if self.request.user == log.added_by:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button'] = 'Update'
        return context

class LogDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Log
    success_message = "Log verwijderd."

    def get_success_url(self):
        item = self.object.item
        return reverse_lazy('logbook')

    def test_func(self):
        log = self.get_object()
        if self.request.user == log.added_by:
            return True
        return False