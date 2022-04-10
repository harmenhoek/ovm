from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, Planning
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from users.forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse


class UsersView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'central/user_list.html'

class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'central/user_detail.html'


@method_decorator(staff_member_required, name='dispatch') #only staff can add new
class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    success_message = "User <b>%(first_name)s %(last_name)s (%(email)s)</b> was updated successfully."
    form_class = UserUpdateForm
    template_name = 'central/user_form.html'

    def get_success_url(self):
        return reverse("user-detail", kwargs={"pk": self.object.pk})


@method_decorator(staff_member_required, name='dispatch') #only staff can add new
class UserCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'central/user_form.html'

    def get_success_url(self):
        return reverse("user-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        import unidecode
        form.instance.username = unidecode.unidecode(f"{form.instance.first_name.lower()}{form.instance.last_name.lower()}").lower().replace(" ", "")
        response = super(UserCreateView, self).form_valid(form)
        self.object = form.save()

        return response

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'central/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-postslug']

    def get_context_data(self, **kwargs): # get info of currently selected post
        context = super().get_context_data(**kwargs)

        context['current_post'] = Post.objects.filter(
            postslug=self.kwargs.get('postslug')).first()  # must first since no pk is used

        return context

def about(request):
    return render(request, 'central/about.html', {'title': 'About'})

@login_required
def planning_approve(request, pk, confirmed):
    try:
        plan_item = Planning.objects.get(pk=pk)
    except:
        return render(request, 'central/planning_approve.html', {'pk': 'unknown!'})

    if confirmed:
        plan_item.confirmed = True
        plan_item.save()
        messages.success(request, f'{plan_item.user.first_name} {plan_item.user.last_name} bevestigd op post {plan_item.post.postslug}.')
        return HttpResponseRedirect(reverse("post-detail", kwargs={"postslug": plan_item.post.postslug}))
    else:

        return render(request, 'central/planning_approve.html', {'plan_item': plan_item})

@login_required
def planning_remove(request, pk, confirmed):
    try:
        plan_item = Planning.objects.get(pk=pk)
    except:
        return render(request, 'central/planning_remove.html', {'pk': 'unknown!'})

    if confirmed:
        plan_item.removed = True
        plan_item.save()
        messages.success(request, f'{plan_item.user.first_name} {plan_item.user.last_name} verwijderd op post {plan_item.post.postslug}.')
        return HttpResponseRedirect(reverse("post-detail", kwargs={"postslug": plan_item.post.postslug}))
    else:

        return render(request, 'central/planning_remove.html', {'plan_item': plan_item})

#
# @staff_member_required
# def planning_modify(request, pk):
#     try:
#         plan_item = Planning.objects.get(pk=pk)
#     except:
#         return render(request, 'central/planning_form.html', {'pk': 'unknown!'})
#
#     # if confirmed:
#     #     messages.success(request, f'Planning voor {plan_item.user.first_name} {plan_item.user.last_name} op post {plan_item.post.postslug} aangepast.')
#     #     return HttpResponseRedirect(reverse("post-detail", kwargs={"postslug": plan_item.post.postslug}))
#     # else:
#
#     from central.forms import ModifyPlanningDashboard
#     if request.method == 'POST':
#         form = ModifyPlanningDashboard(request.POST)
#         if form.is_valid():
#             plan_item.post = form.cleaned_data['post']
#             plan_item.customstart = form.cleaned_data['customstart']
#             plan_item.customend = form.cleaned_data['customend']
#
#             messages.success(request, f'Planning voor {plan_item.user.first_name} {plan_item.user.last_name} op post {plan_item.post.postslug} aangepast.')
#             return HttpResponseRedirect(reverse("post-detail", kwargs={"postslug": plan_item.post.postslug}))
#     else:
#         form = ModifyPlanningDashboard()
#         return render(request, 'central/planning_form.html', {'form': form})
#
#     # return render(request, 'central/planning_form.html', {'plan_item': plan_item})

# @method_decorator(staff_member_required, name='dispatch')
# class PlanningModify(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
#     model = Planning
#     success_message = "Aangepast."
#     # success_url =  reverse_lazy("post-detail", kwargs={"postslug": plan_item.post.postslug})
#     fields = ['post', 'customstart', 'customend', 'shift']
#     template_name = 'central/planning_form.html'
#
#     def get_success_url(self):
#         return reverse("post-detail", kwargs={"postslug": self.post.postslug})

# @method_decorator(staff_member_required, name='dispatch')
# class CabinetUpdateView(PermissionRequiredMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
#     permission_required = 'users.is_itemmoderator'
#     model = Cabinet
#     success_message = "Cabinet <b>%(number)s</b> in lab %(lab)s was updated successfully."
#     success_url = reverse_lazy('manage-cabinets')
#     fields = ['lab', 'number', 'nickname', 'main_content', 'owner', 'image']
#     template_name = 'ems_manage/cabinet_form.html'


# @permission_required('users.is_itemmoderator')
# def check_assignremove(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#
#     if item.storage_location is None:  # no storage location set, this must be done first before item can be stored.
#         from ems.forms import AddStorageLocationForm
#         if request.method == 'POST':
#             form = AddStorageLocationForm(request.POST)
#             if form.is_valid():
#                 item.storage_location = form.cleaned_data['storage_location']
#         else:
#             form = AddStorageLocationForm()
#             return render(request, 'ems/storagelocation_form.html', {'form': form})
#
#     messages.success(request,
#                      f'Item <b>{item.brand} {item.model}</b> (assigned to {item.user} at {item.location}) was <b>unassigned.</b> Make sure it is in storage cabinet <b>{item.storage_location}</b>.')
#     item.status = True
#     item.user = None
#     item.date_return = timezone.now()
#     item.last_scanned = timezone.now()
#     item.save()
#
#     return HttpResponseRedirect(reverse('manage-check'))

from .forms import ModifyPlanningDashboard

import json
def planning_modify(request, pk):
    if request.method == "POST":
        form = ModifyPlanningDashboard(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204)
    else:
        form = ModifyPlanningDashboard()
    return render(request, 'central/planning_form.html', {
        'form': form,
    })

from .forms import ModifyPlanningDashboard, AddDay



def planning_add(request):
    if request.method == "POST":
        form = AddDay(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "showMessage": f"Day added."
                    })
                })
    else:
        form = AddDay()
    return render(request, 'central/planning_form.html', {'form': form})


# https://blog.benoitblanchon.fr/django-htmx-modal-form/



class PostMapView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'central/post_map.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-postslug']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # load status for map
        from datetime import datetime, timedelta, date
        from django.db.models import Count, F
        datetimenow = datetime.now()
        datenow = date.today()

        # created_on__contains=date

        # now + overdue

        status_orange = Planning.objects.filter(removed=False, confirmed=True, shift__date__date=datenow,
                                                shift__shiftstart__lt=datetimenow, shift__shiftend__lt=datetimenow). \
            values('post').distinct()
            # values('post', 'post__postslug', 'shift').annotate(dcount=Count('post')).order_by()

        # now + not confirmed (planning)
        status_blue = Planning.objects.filter(removed=False, confirmed=False, shift__date__date=datenow,
                                              shift__shiftstart__lt=datetimenow, shift__shiftend__gt=datetimenow). \
            exclude(pk__in=status_orange).values('post').distinct()

        # now + confirmed
        status_green = Planning.objects.filter(removed=False, confirmed=True, shift__date__date=datenow,
                                               shift__shiftstart__lt=datetimenow, shift__shiftend__gt=datetimenow).\
            exclude(pk__in=status_orange | status_blue).values('post').distinct()

        # TODO in near future
        # TODO include extra time from shift

        status_orange_2 = [{i['post']: 'warning'} for i in status_orange]
        status_blue_2 = [{i['post']: 'primary'} for i in status_blue]
        status_green_2 = [{i['post']: 'success'} for i in status_green]
        context['status'] = {k: v for element in status_orange_2 + status_blue_2 + status_green_2 for k, v in element.items()}

        context['status_green'] = status_green
        context['status_orange'] = status_orange
        context['status_blue'] = status_blue


        return context

class PostOccupationView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'central/post_occupation.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-postslug']

    # def get_queryset(self):
    #     from datetime import datetime, timedelta
    #     from django.db.models import Count, F
    #     datetimenow = datetime.now()
    #     return Planning.objects.filter(shift__shiftstart__lt=datetimenow, shift__shiftend__lt=datetimenow).values('post').annotate(dcount=Count('post'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from datetime import datetime, timedelta, date
        datetimenow = datetime.now()
        datenow = date.today()

        # get occupation information.
        context['current_post'] = Post.objects.filter(
            postslug=self.kwargs.get('postslug')).first()  # must first since no pk is used

        occ_orange = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                             confirmed=True,
                                             shift__shiftstart__lt=datetimenow, shift__shiftend__lt=datetimenow,
                                             shift__date__date=datenow)
        occ_blue = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                           confirmed=False,
                                           shift__shiftstart__lt=datetimenow, shift__shiftend__gt=datetimenow,
                                           shift__date__date=datenow)
        occ_green = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                            confirmed=True,
                                            shift__shiftstart__lt=datetimenow, shift__shiftend__gt=datetimenow,
                                            shift__date__date=datenow)
        occ = occ_orange | occ_blue | occ_green
        occ_color = ["warning" for i in range(occ_orange.count())] + \
                    ["primary" for i in range(occ_blue.count())] + \
                    ["success" for i in range(occ_green.count())]
        context['current_occupation'] = zip(occ, occ_color)

        return context

class PostInfoView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'central/post_info.html'  # <app>/<model>_<viewtype>.html
    slug_url_kwarg = 'postslug'
    slug_field = 'postslug'
    context_object_name = 'current_post'