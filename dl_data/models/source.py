#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from django.db import models
from django.conf import settings

class Source(models.Model):
    class Meta:
        app_label = 'dl_data'
    name = models.CharField('Name', max_length=100)
    app_name = models.CharField('interner Name', unique=True, max_length=100)
    json = models.TextField('Daten')
    
    shows = property(lambda s:s.show_set)
    
    __handler = None
    
    def get_available_shows(self, content):
        if not self.__handler:
            self.__handler = __import__('%s.handler' % self.app_name).handler
        return self.__handler.get_available_shows(self, content)
    
    def get_available_episodes(self, show):
        if not self.__handler:
            self.__handler = __import__('%s.handler' % self.app_name).handler
        return self.__handler.get_available_episodes(self, show)

if not settings.DENY_DB_ACCESS:
    for source_app in settings.SOURCE_APPS:
        handler = __import__('%s.handler' % source_app).handler
        this_source, created = Source.objects.get_or_create(name=handler.SOURCE_NAME, app_name=source_app)
        if settings.DEBUG:
            print u'%s als Qulle unter dem Namen "%s" geladen' % (this_source.app_name, this_source.name)
