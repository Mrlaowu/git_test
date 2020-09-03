from django.conf.urls import url
from .views import CartAddView,CartInfoView,CartDelView

urlpatterns=[
    url(r"^add$",CartAddView.as_view(),name="add"), #加入购物车页面
    url(r"^info$",CartInfoView.as_view(),name="info"),
    url(r"^delete$",CartDelView.as_view(),name="delete"),
]