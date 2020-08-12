from django.conf.urls import url
from .views import OrderView,OrderPayView,CheckPayView

urlpatterns=[
    url(r'^/index/(\d+)$',OrderView.as_view(),name="index"),
    url(r'^/pay$',OrderPayView.as_view(),name="pay"),
    url(r'^/check$',CheckPayView.as_view(),name="check"),
]