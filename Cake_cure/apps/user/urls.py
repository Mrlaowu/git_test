from django.conf.urls import url
from .views import RegisterView,LoginView,ActiveView,UserinfoView,UserAddrView,UserOrderView

urlpatterns=[
    url(r"^register$",RegisterView.as_view(),name="register"),
    url(r"^login$",LoginView.as_view(),name="login"),
    url(r"^active/(?P<token>.*)$",ActiveView.as_view(),name="active"),
    url(r"^info$",UserinfoView.as_view(),name="info"),
    url(r"^addr$",UserAddrView.as_view(),name="addr"),
    url(r"^order/(?P<page>.*)$",UserOrderView.as_view(),name="order")
]