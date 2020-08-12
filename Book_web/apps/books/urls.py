from django.conf.urls import url
from .views import IndexView,DetailView,ListView

urlpatterns=[
    url(r'^/index$',IndexView.as_view(),name="index"),
    url(r'^/detail/(\d+)$',DetailView.as_view(),name="detail"),
    url(r'^/list/(?P<btype_id>\d+)/(?P<page>\d+)$',ListView.as_view(),name="list"),
]