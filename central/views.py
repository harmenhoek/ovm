from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
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
from django.http import HttpResponse
from .forms import ModifyPlanningDashboard, AddPlanningDashboard, ImportData
import json
from datetime import date
import csv

@method_decorator(staff_member_required, name='dispatch')
class UsersView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'central/user_list.html'

    def get_queryset(self):
        return get_user_model().objects.filter(is_superuser=False, is_active=True)

@method_decorator(staff_member_required, name='dispatch')
class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'central/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datenow = date.today()
        context['planning'] = Planning.objects.filter(user=self.object.pk, removed=False, date__gte=datenow)

        return context


@method_decorator(staff_member_required, name='dispatch')
class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    success_message = "User <b>%(first_name)s %(last_name)s (%(email)s)</b> was updated successfully."
    form_class = UserUpdateForm
    template_name = 'central/user_form.html'

    def get_success_url(self):
        return reverse("user-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button'] = 'Opslaan'
        return context

@method_decorator(staff_member_required, name='dispatch')
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
        form.instance.is_active = False
        response = super(UserCreateView, self).form_valid(form)
        self.object = form.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button'] = 'Toevoegen'
        return context

@method_decorator(staff_member_required(login_url='login'), name='dispatch')
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

@staff_member_required
def about(request):
    shiftstart = list(ShiftTime.objects.all().values_list('timestart'))
    shiftstart = [i[0].strftime("%H:%M") for i in shiftstart]

    shiftend = list(ShiftTime.objects.all().values_list('timeend'))
    shiftend = [i[0].strftime("%H:%M") for i in shiftend]


    return render(request, 'central/about.html', {'shiftstart': shiftstart, 'shiftend': shiftend})


# https://blog.benoitblanchon.fr/django-htmx-modal-form/

@method_decorator(staff_member_required, name='dispatch')
class PostMapView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'central/post_map.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-postslug']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # load status for map
        from datetime import date, datetime
        datetimenow = datetime.now()
        datenow = date.today()

        # now + overdue
        status_orange = Planning.objects.filter(removed=False, signed_off=False, confirmed=True, date=datenow,
                                                endtime__lt=datetimenow)\
            .exclude(user=None).values('post').distinct()

        # now + not confirmed (planned)
        status_blue = Planning.objects.filter(removed=False, signed_off=False, confirmed=False, date=datenow,
                                              starttime__lt=datetimenow, endtime__gt=datetimenow). \
            exclude(post__pk__in=status_orange).exclude(user=None).values('post').distinct()

        # now + confirmed
        status_green = Planning.objects.filter(removed=False, signed_off=False, confirmed=True, date=datenow,
                                               starttime__lt=datetimenow, endtime__gt=datetimenow).\
            exclude(post__pk__in=status_orange).exclude(post__pk__in=status_blue).exclude(user=None).values('post').distinct()

        # now + external
        status_white = Planning.objects.filter(removed=False, signed_off=False, user=None, external=True, starttime__lt=datetimenow,
                                               endtime__gt=datetimenow, date=datenow).values('post').distinct()


        status_orange_2 = [{i['post']: 'warning'} for i in status_orange]
        status_blue_2 = [{i['post']: 'info'} for i in status_blue]
        status_green_2 = [{i['post']: 'success'} for i in status_green]
        status_white_2 = [{i['post']: 'white'} for i in status_white]
        context['status'] = {k: v for element in status_orange_2 + status_blue_2 + status_green_2 + status_white_2 for k, v in element.items()}

        context['status_green'] = status_green
        context['status_orange'] = status_orange
        context['status_blue'] = status_blue
        context['status_white'] = status_white

        return context

@method_decorator(staff_member_required, name='dispatch')
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
                                             confirmed=True, signed_off=False, endtime__lt=datetimenow,
                                             date=datenow).exclude(user=None)
        occ_blue = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                           confirmed=False, signed_off=False, starttime__lt=datetimenow, endtime__gt=datetimenow,
                                           date=datenow).exclude(user=None)
        occ_green = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False,
                                            confirmed=True, signed_off=False, starttime__lt=datetimenow, endtime__gt=datetimenow,
                                           date=datenow).exclude(user=None)
        occ_white = Planning.objects.filter(post__postslug=self.kwargs.get('postslug'), removed=False, signed_off=False, user=None, external=True,
                                            starttime__lt=datetimenow, endtime__gt=datetimenow, date=datenow)

        from itertools import chain
        occ = list(chain(occ_orange, occ_blue, occ_green))
        # occ = occ_orange | occ_blue | occ_green
        occ_color = [("warning", "dark") for i in range(occ_orange.count())] + \
                    [("info", "dark") for i in range(occ_blue.count())] + \
                    [("success", "white") for i in range(occ_green.count())] + \
                    [("white", "dark") for i in range(occ_white.count())]
        context['current_occupation'] = zip(occ, occ_color)

        return context

@method_decorator(staff_member_required, name='dispatch')
class PostInfoView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'central/post_info.html'  # <app>/<model>_<viewtype>.html
    slug_url_kwarg = 'postslug'
    slug_field = 'postslug'
    context_object_name = 'current_post'

@staff_member_required
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
                    "showMessage": f"<b>{plan_item.user}</b> bevestigd op post <b>{plan_item.post}</b>."
                })
            })

    return render(request, 'central/planningapprove_form.html')

@staff_member_required
def planning_signoff(request, pk):
    plan_item = Planning.objects.get(pk=pk)

    if request.method == "POST":
        plan_item.signed_off = True
        plan_item.signed_off_by = request.user
        from datetime import datetime
        plan_item.signed_off_time = datetime.now()
        plan_item.save()

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "planningUpdated": None,
                    "postmapUpdated": None,
                    "showMessage": f"<b>{plan_item.user if plan_item.user else 'Planning'}</b> afgemeld van post <b>{plan_item.post}</b>."
                })
            })

    return render(request, f"central/planningsignoff_form.html",)

@staff_member_required
def planning_remove(request, pk):
    plan_item = Planning.objects.get(pk=pk)
    starttime_form = request.GET.get('start')
    endtime_form = request.GET.get('end')


    import logging
    logging.warning(f"starttime_form: {starttime_form}")
    logging.warning(f"endtime_form: {endtime_form}")

    if request.method == "POST":
        if not plan_item.user and request.POST['start'] and request.POST['end']:  # for planning we want to change times, not remove everything
            start = int(request.POST['start'])
            end = int(request.POST['end'])
            logging.warning(f"start: {start}")
            logging.warning(f"end: {end}")
            from datetime import datetime, timedelta, date
            import datetime
            starttime_form = datetime.datetime.combine(date.today(), datetime.time(0, 0)) + datetime.timedelta(seconds=start)
            endtime_form = datetime.datetime.combine(date.today(), datetime.time(0, 0)) + datetime.timedelta(seconds=end)
            starttime_form = starttime_form.time()
            endtime_form = endtime_form.time()
            logging.warning(f"starttime_form: {starttime_form}")
            logging.warning(f"endtime_form: {endtime_form}")
            logging.warning(f"plan_item.starttime: {plan_item.starttime}")
            logging.warning(f"plan_item.endtime: {plan_item.endtime}")
            logging.warning(f"starttime_form == plan_item.starttime: {starttime_form == plan_item.starttime}")
            logging.warning(f"endtime_form == plan_item.endtime: {endtime_form == plan_item.endtime}")

            if starttime_form is not plan_item.starttime or endtime_form is not plan_item.endtime:
                # this means not all the planning should be deleted
                # now 2 situations: start or end is removed (cut off from planning). Or inbetween is removed.
                if starttime_form == plan_item.starttime:  # start is trimmed of
                    logging.warning(f"START TRIMMED OFF")
                    plan_item.starttime = endtime_form
                    plan_item.save()
                elif endtime_form == plan_item.endtime:  # end is trimmed of
                    plan_item.endtime = starttime_form
                    logging.warning(f"END TRIMMED OFF")
                    plan_item.save()
                else:  # inbetween is cut cut off: make 2 copies of new one, delete old one
                    logging.warning(f"I moved to the ELSE clause")
                    plan_item.removed = True
                    plan_item.save()

                    plan_item.pk = None  # makes a copy
                    plan_item.endtime = starttime_form
                    plan_item.copy_of = pk
                    plan_item.removed = False
                    plan_item.save()

                    # get original again and make a second copy
                    plan_item = Planning.objects.get(pk=pk)
                    plan_item.pk = None  # makes a copy
                    plan_item.starttime = endtime_form
                    plan_item.copy_of = pk
                    plan_item.removed = False
                    plan_item.save()
            else:
                plan_item.removed = True
                plan_item.save()
        else:
            plan_item.removed = True
            plan_item.removed_by = request.user
            plan_item.save()

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "planningUpdated": None,
                    "postmapUpdated": None,
                    "showMessage": f"<b>{plan_item.user if plan_item.user else 'Planning'}</b> verwijderd van post <b>{plan_item.post}</b>."
                })
            })

    return render(request, f"central/planningremove_form.html", {'start': starttime_form, 'end': endtime_form, } )

@staff_member_required
def planning_add_dashboard(request, pk='None'):
    if request.method == "POST":
        form = AddPlanningDashboard(request.POST)
        if form.is_valid():
            new_planning = form.save()
            new_planning.date = date.today()
            new_planning.created_by = request.user
            new_planning.confirmed_by = request.user
            new_planning.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "postmapUpdated": None,
                        "showMessage": f"<b>{new_planning.user}</b> toegevoegd op post <b>{new_planning.post}</b>."
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

@staff_member_required
def planning_modify(request, pk):
    plan_item = get_object_or_404(Planning, pk=pk)

    if request.method == "POST":
        form = ModifyPlanningDashboard(request.POST, instance=plan_item)
        if form.is_valid():
            plan_item = form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "postmapUpdated": None,
                        "showMessage": f"<b>{plan_item.user}</b> aangepast op post <b>{plan_item.post}</b>."
                    })
                })

    else:
        form = ModifyPlanningDashboard(instance=plan_item)

    return render(request, 'central/planningmodify_form.html', {
        'form': form, 'plan_pk': plan_item.pk,
    })



@staff_member_required
def importer(request):
    if request.method == "POST":
        form = ImportData(request.POST, request.FILES)
        if form.is_valid():
            datatype = form.cleaned_data['datatype']
            csvfile = form.cleaned_data['csvfile']

            # TODO: first get_or_create with firstname-lastname or email, then add rest of data.

            from io import TextIOWrapper
            f = TextIOWrapper(csvfile, encoding='utf-8-sig') # encoding=request.encoding
            reader = csv.reader(f)
            counter = 0
            for row in reader:
                counter += 1
                if datatype == "posts":
                    _, created = Post.objects.get_or_create(
                        post_fullname=row[0],
                        postslug=row[1],
                        maplocation_x=row[2],
                        maplocation_y=row[3],
                        description=row[4],
                        verkeersregelaar=row[5],
                    )
                elif datatype == "users":
                    # TODO: django.db.utils.IntegrityError: UNIQUE constraint failed: users_customuser.phonenumber
                    object, created = get_user_model().objects.get_or_create(
                        first_name=row[0],
                        last_name=row[1],
                        email=row[2],
                        phonenumber=row[4],
                        description=row[5],
                        username=row[2],
                    )
                    specalisms = [int(x) for x in row[6].replace('"', '').split(',')]
                    object.specialism.set(specalisms)
                    if row[3]:
                        object.dateofbirth.set(row[3])

                elif datatype == "planning":
                    # TODO: add error messages! If user not found ...
                    import logging
                    logging.warning(f"post: --{int(float(row[0]))}--")
                    _, created = Planning.objects.get_or_create(
                        post=Post.objects.get(postslug=row[0]),
                        user=get_user_model().objects.get(first_name=row[1], last_name=row[2]),
                        starttime=row[3],
                        endtime=row[4],
                        date=row[5],
                        comment=row[6],
                    )


            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "postmapUpdated": None,
                        "showMessage": f"Successfully imported {counter} rows."
                    })
                })

    else:
        form = ImportData()

    return render(request, 'central/import_form.html', {'form': form, })

# if not csv_file.name.endswith('.csv'):
#         messages.error(request, 'THIS IS NOT A CSV FILE')