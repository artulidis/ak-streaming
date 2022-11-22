from django.contrib import admin
from django import forms
from .models import MyUser, UserFollowingCount, WatchList, Video, Comment, Topic
from django.contrib.auth.admin import UserAdmin

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ( 'username', 
                   'password',
                   'email',
                   'full_name',
                   'profile_image',
                   'followers',
                   'bio' )

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class MyUserAdmin(UserAdmin):

    add_form = UserCreationForm
    list_display = ("username", "id")
    ordering = ("username",)
    list_filter = ("username", )

    fieldsets = (
        (None, {'fields': ( 'username',
                            'password',
                            'email',
                            'full_name',
                            'profile_image',
                            'followers',
                            'bio')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'username',
                        'password',
                        'email',
                        'full_name',
                        'profile_image',
                        'followers',
                        'bio' )}
            ),
        )

    filter_horizontal = ()

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(UserFollowingCount)
admin.site.register(WatchList)
admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(Topic)
