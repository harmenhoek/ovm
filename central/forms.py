from django import forms
from .models import Planning, ShiftTime, ShiftDay, Porto
# from django.forms.models import inlineformset_factory
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from datetime import datetime, date, timedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

IMPORT_CHOICES = (
    ("posts", "Posts"),
    ("users", "Users"),
    ("planning", "Planning"),
)

class ImportData(forms.Form):
    datatype = forms.ChoiceField(choices=IMPORT_CHOICES, )
    csvfile = forms.FileField()


class ModifyPlanningDashboard(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['user', 'post', 'endtime', 'comment', 'porto', 'bike']
        widgets = {
            'endtime': TimePickerInput(),
        }

    def clean_user(self):
        datetimenow = datetime.now()
        datenow = date.today()
        user = self.cleaned_data['user']

        plan = Planning.objects.filter(user=user,
                                starttime__lt=datetimenow,
                                endtime__gt=datetimenow,
                                date=datenow, removed=False)
        if plan:
            if plan[0].user.pk is not user.pk: #one extra validation here, since user is already on a post, this one.
                # we specifically request [0], since there should only be 1 result! We cannot use .get since queryset might return empty
                raise ValidationError(f'{plan[0].user} staat momenteel al op post {plan[0].post.postslug}')
        return user

    def clean_endtime(self):
        endtime = self.cleaned_data['endtime']
        currenttime = datetime.now().time()
        if endtime < currenttime:
            raise ValidationError('Geselecteerde tijd ligt niet in de toekomst.')
        return endtime

    def clean_porto(self):
        porto = self.cleaned_data['porto']
        import logging
        logging.warning(f"{porto=}")

        if porto is not None:
            primary_user = Porto.objects.filter(primary_user__isnull=False)
            if not primary_user:
                raise ValidationError(f"Porto {porto.number} is de vaste porto van {porto.primary_user}.")

            from datetime import date
            datenow = date.today()
            plan = Planning.objects.filter(porto=porto, date=datenow, signed_off=False)
            import logging
            logging.warning(f"{plan=}")
            if plan:
                raise ValidationError(f"Porto {porto.number} is al in gebruik door {plan[0].user.first_name} {plan[0].user.last_name} op post {plan[0].post.postslug}.")
        return porto

    def clean(self):
        cleaned_data = super().clean()
        endtime = cleaned_data.get('endtime')
        starttime = cleaned_data.get('starttime')
        if starttime:  # if modified no starttime is given in the form
            # check if endtime > starttime
            if endtime < starttime:
                raise ValidationError('De eindtijd moet voorbij de begintijd liggen.')

        # check whether user is primary_user of a porto
        user_field = cleaned_data.get('user')
        porto_field = cleaned_data.get('porto')
        try:
            porto = Porto.objects.get(primary_user=user_field)
        except Porto.DoesNotExist:
            porto = None
        if porto_field and porto:
            self.add_error('porto',
                           ValidationError(
                               f"{user_field} heeft een eigen porto. Je kunt niet nog een porto toevoegen."))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['endtime'].required = True
        self.fields['user'].required = True

        # modify the porto dropdowns to include current user / primary_user
        porto_field = self.fields['porto']
        porto_field.label_from_instance = self.get_porto_label

    def get_porto_label(self, porto):
        planning = porto.planning_set.first()
        if porto.primary_user:
            return f'{porto.number} - {porto.primary_user} (vaste porto)'
        elif planning:
            return f'{porto.number} - {planning.user} (post {planning.post})'
        return porto.number




class AddPlanningDashboard(forms.ModelForm):
    # its actually just occupation that is added, not planning

    slider = forms.Field(label='')

    class Meta:
        model = Planning
        fields = ['user', 'post', 'slider', 'starttime', 'endtime', 'comment', 'porto', 'bike', 'confirmed']
        widgets = {
            'endtime': TimePickerInput(),
        }

    def clean_user(self):
        datetimenow = datetime.now()
        datenow = date.today()
        user = self.cleaned_data['user']

        from .models import Planning
        plan = Planning.objects.filter(user=user,
                                starttime__lt=datetimenow,
                                endtime__gt=datetimenow,
                                date=datenow, removed=False, signed_off=False).exclude(external=True)
        if plan:
            # we specifically request [0], since there should only be 1 result! We cannot use .get since queryset might return empty
            raise ValidationError(f'{plan[0].user} staat momenteel al op post {plan[0].post.postslug}')
        return user

    def clean_endtime(self):
        endtime = self.cleaned_data['endtime']
        currenttime = datetime.now().time()
        if endtime < currenttime:
            raise ValidationError('Geselecteerde tijd ligt niet in de toekomst.')
        return endtime

    def clean_porto(self):
        porto = self.cleaned_data['porto']
        import logging
        logging.warning(f"{porto=}")

        if porto is not None:
            primary_user = Porto.objects.filter(primary_user__isnull=False)
            if not primary_user:
                raise ValidationError(f"Porto {porto.number} is de vaste porto van {porto.primary_user}.")

            from datetime import date
            datenow = date.today()
            plan = Planning.objects.filter(porto=porto, date=datenow, signed_off=False)
            import logging
            logging.warning(f"{plan=}")
            if plan:
                raise ValidationError(f"Porto {porto.number} is al in gebruik door {plan[0].user.first_name} {plan[0].user.last_name} op post {plan[0].post.postslug}.")
        return porto

    def clean(self):
        cleaned_data = super().clean()
        endtime = cleaned_data.get('endtime')
        starttime = cleaned_data.get('starttime')
        # check if endtime > starttime
        if endtime < starttime:
            raise ValidationError('De eindtijd moet voorbij de begintijd liggen.')

        # check whether user is primary_user of a porto
        user_field = cleaned_data.get('user')
        porto_field = cleaned_data.get('porto')
        try:
            porto = Porto.objects.get(primary_user=user_field)
        except Porto.DoesNotExist:
            porto = None
        if porto_field and porto:
            self.add_error('porto',
                           ValidationError(f"{user_field} heeft een eigen porto. Je kunt niet nog een porto toevoegen."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['starttime'].disabled = True
        self.fields['starttime'].initial = datetime.now().time().strftime("%H:%M")
        self.fields['confirmed'].initial = True
        self.fields['endtime'].required = True
        self.fields['endtime'].widget.attrs.update({
            'id': 'endtime',
        })
        self.fields['user'].required = True
        self.fields['slider'].required = False
        self.fields['slider'].widget.attrs.update({
            'id': 'shifts_range_slider',
            'onchange': "Update_Shifttimes()",
            'type': "text",
            'name': "somename",
            'data-provide': "slider",
            'data-slider-ticks': "[1, 2, 3, 4, 5]",
            'data-slider-min': "1",
            'data-slider-max': "5",
            'data-slider-step': "1",
            'data-slider-value': "5",
            'data-slider-tooltip': "hide",
            'style': 'width:100%',
        })

        porto_field = self.fields['porto']
        porto_field.label_from_instance = self.get_porto_label

    def get_porto_label(self, porto):
        planning = porto.planning_set.first()
        if porto.primary_user:
            return f'{porto.number} - {porto.primary_user} (vaste porto)'
        elif planning:
            return f'{porto.number} - {planning.user} (post {planning.post})'
        return porto.number
