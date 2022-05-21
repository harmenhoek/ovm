from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Log
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
import json
from django.shortcuts import render, get_object_or_404, redirect
from central.models import Planning, ShiftDay, Post
from datetime import datetime, timedelta, date

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa


def logbooktable(request, dayname=None):
    if dayname is None:
        # see if current date is in list
        if ShiftDay.objects.filter(active=True, date=date.today()):
            daydate = ShiftDay.objects.get(active=True, date=date.today()).date
            dayname = ShiftDay.objects.get(active=True, date=date.today()).dayname
        else:
            daydate = ShiftDay.objects.filter(active=True)[0].date
            dayname = ShiftDay.objects.filter(active=True)[0].dayname
        logs = Log.objects.filter(deleted=False, added_on=daydate)
    elif dayname == "all":
        logs = Log.objects.filter(deleted=False)
    else:
        daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date
        logs = Log.objects.filter(deleted=False, added_on=daydate)

    return render(request, 'logbook/log_list_table.html', {'logs': logs})

def logbook(request, dayname=None):
    if dayname == "all" or (dayname is None and not ShiftDay.objects.filter(active=True, date=date.today())):
        # show all days when: day=all, or when no day is passed and current date is not one of the Shiftdays
        logs = Log.objects.filter(deleted=False)
        dayname = 'all'
    elif ShiftDay.objects.filter(active=True, date=date.today()):
        # no day is passed (condition automatically agreed) and current date is one of ShiftDays
        daydate = ShiftDay.objects.get(active=True, date=date.today()).date
        dayname = ShiftDay.objects.get(active=True, date=date.today()).dayname
        logs = Log.objects.filter(deleted=False, added_on=daydate)
    else:
        # exact day is passed
        daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date
        logs = Log.objects.filter(deleted=False, added_on=daydate)

    alldays = ShiftDay.objects.filter(active=True)
    return render(request, 'logbook/log_list.html', {'logs': logs, 'alldays': alldays, 'currentday': dayname, })

# # defining the function to convert an HTML file to a PDF file
# def html_to_pdf(template_src, context_dict={}):
#      template = get_template(template_src)
#      html  = template.render(context_dict)
#      result = BytesIO()
#      pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#      if not pdf.err:
#          return HttpResponse(result.getvalue(), content_type='application/pdf')
#      return None


# class GeneratePdf(View):
#     def get(self, request, *args, **kwargs):
#         data = models.Employees.objects.all().order_by('first_name')
#         open('templates/temp.html', "w").write(render_to_string('result.html', {'data': data}))
#
#         # Converting the HTML template into a PDF file
#         pdf = html_to_pdf('temp.html')
#
#         # rendering the template
#         return HttpResponse(pdf, content_type='application/pdf')




# class GeneratePdf(View):
#     def get(self, request, *args, **kwargs):
#         pdf = html_to_pdf('logbook/exportpage.html')
#         return HttpResponse(pdf, content_type='application/pdf')

# from django.template.loader import render_to_string
# def generatepdf(request, dayname):
#     if dayname == "all":
#         logs = Log.objects.filter(deleted=False)
#     else:
#         daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date
#         logs = Log.objects.filter(deleted=False, added_on=daydate)
#     open('logbook/tempexport.html', "w").write(render_to_string('logbook/exportpage.html', {'logs': logs, 'currentday': dayname, }))
#     pdf = html_to_pdf('logbook/tempexport.html')
#     return HttpResponse(pdf, content_type='application/pdf')
#
#



# @method_decorator(staff_member_required, name='dispatch')  # this should be changed to simple def view
# class LogListView(LoginRequiredMixin, ListView):
#     model = Log
#     ordering = ['added_on']
#     template_name = 'logbook/log_list.html'

@method_decorator(staff_member_required, name='dispatch')
class LogDetailView(LoginRequiredMixin, DetailView):
    model = Log
    template_name = 'logbook/log_detail.html'

@method_decorator(staff_member_required, name='dispatch')
class LogCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Log
    fields = ['log', 'file1', 'file2']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button'] = 'Toevoegen'
        return context

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        super().form_valid(form)
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "showMessage": f"Log toegevoegd.",
                    "logsUpdated": None
                })
            })

@method_decorator(staff_member_required, name='dispatch')
class LogUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Log
    fields = ['log', 'file1', 'file2']

    def test_func(self):
        log = self.get_object()
        if self.request.user == log.added_by:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button'] = 'Opslaan'
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "showMessage": f"Log Bijgewerkt.",
                    "logsUpdated": None
                })
            })

@method_decorator(staff_member_required, name='dispatch')
class LogDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Log

    def post(self, request, *args, **kwargs):
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "showMessage": f"Log verwijderd.",
                    "logsUpdated": None
                })
            })

    # def get_success_url(self):
    #     item = self.object.item
    #     return reverse_lazy('logbook')

    def test_func(self):
        log = self.get_object()
        if self.request.user == log.added_by:
            return True
        return False


#
# import os
# from django.conf import settings
# from django.http import HttpResponse
# from django.template import Context
# from django.template.loader import get_template
# import datetime
# from xhtml2pdf import pisa
# import reportlab
# from io import BytesIO
#
# # def generatepdf(request, dayname):
# #     if dayname == "all":
# #         logs = Log.objects.filter(deleted=False)
# #     else:
# #         daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date
# #         logs = Log.objects.filter(deleted=False, added_on=daydate)
# #
# #
# #     template = get_template('logbook/exportpage.html')
# #     html = template.render({'logs': logs, 'currentday': dayname, })
# #
# #     file = open('test.pdf', "w+b")
# #     pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
# #                                 encoding='utf-8')
# #
# #     file.seek(0)
# #     pdf = file.read()
# #     file.close()
# #     return HttpResponse(pdf, 'application/pdf')
#
# def render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None
#
#
# def generatepdf(request, dayname):
#     if dayname == "all":
#         logs = Log.objects.filter(deleted=False)
#     else:
#         daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date
#         logs = Log.objects.filter(deleted=False, added_on=daydate)
#
#     pdf = render_to_pdf("logbook/exportpage.html", {'logs': logs, 'currentday': dayname, })
#     return HttpResponse(pdf, content_type='application/pdf')

def exportpage(request, dayname):
    if dayname == "all":
        logs = Log.objects.filter(deleted=False)
    else:
        daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date
        logs = Log.objects.filter(deleted=False, added_on=daydate)
    return render(request, 'logbook/exportpage.html', {'logs': logs, 'currentday': dayname, })



# class GeneratePdf(View):
#     def get(self, request, *args, **kwargs):
#         pass