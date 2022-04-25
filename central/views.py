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
from .models import Post, Planning, ShiftTime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from users.forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from .forms import ModifyPlanningDashboard, AddPlanningDashboard
import json
from datetime import datetime, date


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
        # form.instance.username = unidecode.unidecode(f"{form.instance.first_name.lower()}{form.instance.last_name.lower()}").lower().replace(" ", "")
        form.instance.username = form.instance.email
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
    shiftstart = list(ShiftTime.objects.all().values_list('timestart'))
    shiftstart = [i[0].strftime("%H:%M") for i in shiftstart]

    shiftend = list(ShiftTime.objects.all().values_list('timeend'))
    shiftend = [i[0].strftime("%H:%M") for i in shiftend]


    return render(request, 'central/about.html', {'shiftstart': shiftstart, 'shiftend': shiftend})











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

        status_orange = Planning.objects.filter(removed=False, confirmed=True, date=datenow,
                                                starttime__lt=datetimenow, endtime__lt=datetimenow). \
            values('post').distinct()

        # now + not confirmed (planning)
        status_blue = Planning.objects.filter(removed=False, confirmed=False, date=datenow,
                                              starttime__lt=datetimenow, endtime__gt=datetimenow). \
            exclude(pk__in=status_orange).values('post').distinct()

        # now + confirmed
        status_green = Planning.objects.filter(removed=False, confirmed=True, date=datenow,
                                               starttime__lt=datetimenow, endtime__gt=datetimenow).\
            exclude(pk__in=status_orange | status_blue).values('post').distinct()


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
                                             starttime__lt=datetimenow, endtime__lt=datetimenow,
                                             date=datenow)
        occ_blue = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                           confirmed=False,
                                           starttime__lt=datetimenow, endtime__gt=datetimenow,
                                           date=datenow)
        occ_green = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                            confirmed=True,
                                            starttime__lt=datetimenow, endtime__gt=datetimenow,
                                           date=datenow)
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


@login_required
def planning_approve(request, pk):
    plan_item = Planning.objects.get(pk=pk)

    if request.method == "POST":
        plan_item.confirmed = True
        plan_item.confirmed_by = request.user
        plan_item.save()
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "planningUpdated": None,
                    "postmapUpdated": None,
                    "showMessage": f"Planning bevestigd."
                })
            })

    return render(request, 'central/planningapprove_form.html')

@login_required
def planning_remove(request, pk):
    plan_item = Planning.objects.get(pk=pk)

    if request.method == "POST":
        plan_item.removed = True
        plan_item.removed_by = request.user
        plan_item.save()
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "planningUpdated": None,
                    "postmapUpdated": None,
                    "showMessage": f"Planning verwijderd."
                })
            })

    return render(request, 'central/planningremove_form.html')

@login_required
def planning_add_dashboard(request, pk='None'):
    if request.method == "POST":
        form = AddPlanningDashboard(request.POST)
        if form.is_valid():
            new_planning = form.save()
            new_planning.date = date.today()
            new_planning.confirmed = True
            new_planning.created_by = request.user
            new_planning.confirmed_by = request.user
            new_planning.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "postmapUpdated": None,
                        "showMessage": f"Planning added."
                    })
                })
        return render(request, 'central/planningadd_form.html', {'form': form})
    else:
        # send extra context for slider
        shiftstart = list(ShiftTime.objects.all().values_list('timestart'))
        shiftstart = [i[0].strftime("%H:%M") for i in shiftstart]
        shiftend = list(ShiftTime.objects.all().values_list('timeend'))
        shiftend = [i[0].strftime("%H:%M") for i in shiftend]

        if pk:
            form = AddPlanningDashboard(initial={'post': str(pk)})
        else:
            form = AddPlanningDashboard()

        return render(request, 'central/planningadd_form.html', {'form': form, 'shiftstart': shiftstart, 'shiftend': shiftend})



@login_required
def planning_modify(request, pk):
    plan_item = get_object_or_404(Planning, pk=pk)

    if request.method == "POST":
        form = ModifyPlanningDashboard(request.POST, instance=plan_item)
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "postmapUpdated": None,
                        "showMessage": f"Planning modified."
                    })
                })

    else:
        form = ModifyPlanningDashboard(instance=plan_item)

    return render(request, 'central/planningmodify_form.html', {
        'form': form,
    })
