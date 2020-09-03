from django.conf.urls import url
from .views import IndexView,ListView,DetailView

urlpatterns=[
    url(r"^$",IndexView.as_view(),name="index"), #首页
    url(r"^list/(?P<type_id>\d+)/(?P<page>\d+)$",ListView.as_view(),name="list"), #列表页
    url(r"^detail/(\d*)$",DetailView.as_view(),name="detail") ,#详情页

]
