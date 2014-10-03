from django.conf.urls import patterns, include, url

urlpatterns = patterns('dl_data.views',
    url(r'^ajax/search/$', 'search', name='search'),
    url(r'^ajax/add/$', 'add', name='add'),
    url(r'^ajax/update/show$', 'update_show', name='update_show'),
)
