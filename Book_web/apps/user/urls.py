from django.conf.urls import url
from .views import RegisterView,ActiveView,LoginView,LogoutView,ProfileView
urlpatterns=[
    url(r'^/register$',RegisterView.as_view(),name="register"),
    url(r'^/active/(?P<token>.*)$',ActiveView.as_view(),name="active"),
    url(r'^/login$',LoginView.as_view(),name="login"),
    url(r'^/logout$',LogoutView.as_view(),name="logout"),
    url(r'^/profile$',ProfileView.as_view(),name="profile")
]