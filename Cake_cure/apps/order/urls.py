from django.conf.urls import url
from .views import OrderCommit,CreateOrderView

urlpatterns=[
    url(r"^commit$",OrderCommit.as_view(),name="commit"),
    url(r"^create$",CreateOrderView.as_view(),name="create")
]