from django import forms
from .models import JournalEntry, Comment, Event


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['text_content', 'image']
        widgets = {
            'text_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write about your riding session...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add your comment...'
            })
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'date', 'time']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event title'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Details about the event (optional)'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            })
        }

