from django import forms
from central.models import Planning, ShiftTime, ShiftDay
from central.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from datetime import datetime, date
from django.core.exceptions import ValidationError

class ModifyPlanningPlanner(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['user', 'post', 'date', 'starttime', 'endtime', 'comment']
        widgets = {
            'starttime': TimePickerInput(),
            'endtime': TimePickerInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        date = cleaned_data.get('date')
        endtime = cleaned_data.get('endtime')
        starttime = cleaned_data.get('starttime')

        # check if endtime > starttime
        if endtime < starttime:
            raise ValidationError('De eindtijd moet voorbij de begintijd liggen.')

        plan = Planning.objects.filter(user=user, starttime__lte=endtime, endtime__gte=starttime, date=date, removed=False)
        if plan:
            if plan[0].user.pk is not user.pk:  # one extra validation here, since user is already on a post, this one.
                # we specifically request [0], since there should only be 1 result! We cannot use .get since queryset might return empty
                raise ValidationError(
                    f'Overlap met bestaande planning. {plan[0].user} staat al ingepland op post {plan[0].post.postslug}.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].required = True
        self.fields['starttime'].required = True
        self.fields['endtime'].required = True
        self.fields['user'].required = True





class AddPlanningPlanner(forms.ModelForm):

    slider = forms.Field(label='')

    class Meta:
        model = Planning
        fields = ['post', 'date', 'slider', 'starttime', 'endtime', 'comment']

        options = ShiftDay.objects.filter(active=True)
        CHOICES = ((x.date, x.dayname) for x in options)

        widgets = {
            'starttime': TimePickerInput(),
            'endtime': TimePickerInput(),
            'date': forms.Select(choices=CHOICES),
        }

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        endtime = cleaned_data.get('endtime')
        starttime = cleaned_data.get('starttime')
        # check if endtime > starttime
        if endtime < starttime:
            raise ValidationError('De eindtijd moet voorbij de begintijd liggen.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datenow = date.today()
        if ShiftDay.objects.filter(date=datenow):
            self.fields['date'].initial = (ShiftDay.objects.filter(date=datenow)[0].date, ShiftDay.objects.filter(date=datenow)[0].dayname)

        self.fields['starttime'].required = True
        self.fields['endtime'].required = True
        self.fields['slider'].required = False
        self.fields['date'].required = True
        self.fields['starttime'].widget.attrs.update({
            'id': 'starttime',
        })
        self.fields['endtime'].widget.attrs.update({
            'id': 'endtime',
        })
        self.fields['slider'].widget.attrs.update({
            'id': 'shifts_range_slider',
            'onchange': "Update_Shifttimes_Double()",
            'type': "text",
            'name': "somename",
            'data-provide': "slider",
            'data-slider-ticks': "[1, 2, 3, 4, 5]",
            'data-slider-min': "1",
            'data-slider-max': "5",
            'data-slider-step': "1",
            'data-slider-value': "[1,5]",
            'data-slider-tooltip': "hide",
            'style': 'width:100%',
        })





class AddOccupationPlanner(forms.ModelForm):
    slider = forms.Field(label='')

    class Meta:
        model = Planning
        fields = ['user', 'post', 'date', 'slider', 'starttime', 'endtime', 'comment']

        options = ShiftDay.objects.filter(active=True)
        CHOICES = ((x.date, x.dayname) for x in options)

        widgets = {
            'starttime': TimePickerInput(),
            'endtime': TimePickerInput(),
            'date': forms.Select(choices=CHOICES),
        }

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        user = cleaned_data.get('user')
        date = cleaned_data.get('date')
        endtime = cleaned_data.get('endtime')
        starttime = cleaned_data.get('starttime')
        # check if endtime > starttime
        if endtime < starttime:
            raise ValidationError('De eindtijd moet voorbij de begintijd liggen.')

        plan = Planning.objects.filter(user=user, starttime__lte=endtime, endtime__gte=starttime, date=date,
                                       removed=False)
        if plan:
            raise ValidationError(
                f'Overlap met bestaande planning. {plan[0].user} staat al ingepland op post {plan[0].post.postslug}.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datenow = date.today()
        if ShiftDay.objects.filter(date=datenow):
            self.fields['date'].initial = (
            ShiftDay.objects.filter(date=datenow)[0].date, ShiftDay.objects.filter(date=datenow)[0].dayname)

        self.fields['starttime'].required = True
        self.fields['endtime'].required = True
        self.fields['slider'].required = False
        self.fields['date'].required = True
        self.fields['starttime'].widget.attrs.update({
            'id': 'starttime',
        })
        self.fields['endtime'].widget.attrs.update({
            'id': 'endtime',
        })
        self.fields['slider'].widget.attrs.update({
            'id': 'shifts_range_slider',
            'onchange': "Update_Shifttimes_Double()",
            'type': "text",
            'name': "somename",
            'data-provide': "slider",
            'data-slider-ticks': "[1, 2, 3, 4, 5]",
            'data-slider-min': "1",
            'data-slider-max': "5",
            'data-slider-step': "1",
            'data-slider-value': "[1,5]",
            'data-slider-tooltip': "hide",
            'style': 'width:100%',
        })