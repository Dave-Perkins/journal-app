from django import forms
from .models import JournalEntry, Comment


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
