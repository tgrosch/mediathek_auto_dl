from django.conf.urls import patterns, include, url

urlpatterns = patterns('dl_gui.views',
    url(r'^$', 'index', name="index"),
                       
    url(r'^manage/$', 'manage', name="manage"),
                       
    url(r'^overview/$', 'overview', name="overview"),
        url(r'^overview/detail/(?P<show_id>\d+)/$', 'detail', name="detail"),
        url(r'^overview/search/$', 'search', name="search"),
)
