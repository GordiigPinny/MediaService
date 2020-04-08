from django.conf.urls import url
from Mediafiles import views


urlpatterns = [
    url(r'^images/$', views.AddImageView.as_view()),
    url(r'^images/(?P<pk>\d+)/$', views.ImageView.as_view()),
    url(r'^images/(?P<pk>\d+)/meta/$', views.ImageMetaView.as_view()),
    url(r'^images/(?P<object_type>\w+)/(?P<object_id>\d+)/$', views.TypedImagesView.as_view()),
]
