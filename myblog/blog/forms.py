from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'banner', 'content', 'category', 'tags']
        widgets = {
            "title": forms.TextInput(attrs={'placeholder': 'Enter the title here...'}),
            "banner": forms.FileInput(attrs={'accept': 'image/*'}),
            "content": forms.Textarea(attrs={"rows": 12, 'placeholder': 'Enter your text here...'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a comment...',
            }),
        }


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    # subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
