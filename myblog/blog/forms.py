from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'banner', 'content']
        widgets = {
            "title": forms.TextInput(attrs={'placeholder': 'Enter the title here...'}),
            "banner": forms.FileInput(attrs={'accept': 'image/*'}),
            "content": forms.Textarea(attrs={"rows": 12, 'placeholder': 'Enter your text here...'}),
        }


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    # subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
