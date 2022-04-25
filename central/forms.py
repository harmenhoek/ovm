from django import forms
from .models import Planning, ShiftTime, ShiftDay
# from django.forms.models import inlineformset_factory
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from datetime import datetime, date
from django.core.exceptions import ValidationError

class AddPlanningMain(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['user', 'post']

    def get_context(self): # this even works?
        pass

class ModifyPlanningDashboard(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['user', 'post', 'endtime', 'comment']
        widgets = {
            'endtime': TimePickerInput(),
        }

    def clean_user(self):
        datetimenow = datetime.now()
        datenow = date.today()
        user = self.cleaned_data['user']
        # from django.db.models import Q
        # User.objects.filter(Q(income__gte=5000) | Q(income__isnull=True))

        from .models import Planning
        plan = Planning.objects.filter(user=user,
                                starttime__lt=datetimenow,
                                endtime__gt=datetimenow,
                                date=datenow)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['endtime'].required = True
        self.fields['user'].required = True




class AddPlanningDashboard(forms.ModelForm):

    # from users.models import CustomUser
    # from django.forms import ModelChoiceField
    # from datetime import datetime, date
    # datetimenow = datetime.now()
    # datenow = date.today()
    # user = ModelChoiceField(queryset=CustomUser.objects.exclude(planning__shift__shiftstart__lt=datetimenow,
    #                                                              planning__shift__shiftend__gt=datetimenow,
    #                                                              planning__shift__date__date=datenow), disabled=True)

    slider = forms.Field(label='')

    class Meta:
        model = Planning
        fields = ['user', 'post', 'slider', 'starttime', 'endtime', 'comment', 'confirmed']
        widgets = {
            'endtime': TimePickerInput(),
        }

    def clean_user(self):
        datetimenow = datetime.now()
        datenow = date.today()
        user = self.cleaned_data['user']
        # from django.db.models import Q
        # User.objects.filter(Q(income__gte=5000) | Q(income__isnull=True))

        from .models import Planning
        plan = Planning.objects.filter(user=user,
                                starttime__lt=datetimenow,
                                endtime__gt=datetimenow,
                                date=datenow, removed=False)
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


    # def __init__(self, *args, **kwargs):
    #     super(AddPlanningDashboard, self).__init__(*args, **kwargs)
    #
    #
    #     from datetime import datetime, timedelta, date
    #     datetimenow = datetime.now()
    #     datenow = date.today()
    #
    #     from users.models import CustomUser
    #     self.fields['user'].queryset = CustomUser.objects.exclude(planning__shift__shiftstart__lt=datetimenow,
    #                                                              planning__shift__shiftend__gt=datetimenow,
    #                                                              planning__shift__date__date=datenow)

