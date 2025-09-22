from django import forms

from event.models import (
    EventCategory,
    Event
)

STATUS = [
    ("future", "Future"),
    ("active", "Active"),
    ("past", "Past"),
]

class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = ['name', 'description', 'priority', 'image'] #Fields that have to be filled

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        priority = cleaned_data.get('priority')

        if not (name and description and priority):
            raise forms.ValidationError("All fields should be filled.")



class CreateEventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        label='Start',
        widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    end_date = forms.DateTimeField(
        label='End',
        widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        status = cleaned_data.get('status')
        repeat = cleaned_data.get('repeat')
        end_repeat_date = cleaned_data.get('end_repeat_date')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not (name and description and status and repeat and start_date and end_date):
            raise forms.ValidationError("All fields should be filled.")
        
        if repeat != 'none' and not end_repeat_date:
            raise forms.ValidationError("End repeat date should be given when creating repeated event.")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("Start date should be before end date.")
        
        if end_repeat_date and end_repeat_date <= start_date.date():
            raise forms.ValidationError("End repeat date should be after start date.")
        
        return cleaned_data
    
    class Meta:
        model = Event
        fields = ['name', 'description', 'status', 'start_date', 'end_date', 'repeat', 'end_repeat_date']

class UpdateCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = ['name', 'description', 'priority', 'image'] #Fields that can be modified

    # Custom save method for the form (because I do not want to change the creator)
    def save(self, commit=True):
        #The function is called only if the commitment is TRUE
        category = self.instance
        category.name = self.cleaned_data['name']
        category.description = self.cleaned_data['description']
        category.priority = self.cleaned_data['priority']

        if self.cleaned_data['image']:
            # Ако има нова снимка ще я смени, в противен случай ще остави същата
            category.image = self.cleaned_data['image']
        
        if commit:
            category.save()
        return category
    
class UpdateEventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        label='Start',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end_date = forms.DateTimeField(
        label='End',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("Start date should be before end date.")
        return cleaned_data

    def save(self, commit=True):
        event = self.instance
        event.name = self.cleaned_data['name']
        event.description = self.cleaned_data['description']
        event.status = self.cleaned_data['status']
        event.start_date = self.cleaned_data['start_date']
        event.end_date = self.cleaned_data['end_date']

        if commit:
            event.save()
        return event
    
    class Meta:
        model = Event
        fields = ['name', 'description', 'status', 'start_date', 'end_date']