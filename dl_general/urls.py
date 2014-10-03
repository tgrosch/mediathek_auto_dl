from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
)

for app in settings.ACTIVE_APPS:
    pattern = r'^%s/' % app
    if app in settings.INITIAL_APPS:
        pattern = r'^'
    try:
        urls = __import__('%s.urls' % app)
        urlpatterns += patterns('',
            (pattern, include('%s.urls' % app, namespace=app)),
        )
    except ImportError:
        continue

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
