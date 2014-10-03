from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, Http404
from json import loads, dumps
from dl_data.models import Source, Show
from dl_data.views.handler import get_shows, get_episodes


def json_dump(ret):
    j = dumps(ret)
    return HttpResponse(j, content_type="text/plain")

def search(request):
    request_data = request.REQUEST
    content = request_data.get("search")
    source = request_data.get("source")
    ignore = request_data.getlist("ignore[]")
    
    result = {}
    
    if not content:
        return json_dump(result)
    
    source_obj = None
    if source:
        source_obj = Source.objects.filter(app_name=source)
        if source_obj:
            result = get_shows(content, source_obj[0], ignore=ignore)
    
    if not source_obj:
        for source_obj in Source.objects.all():
            result[source_obj.name] = get_shows(content, source_obj, ignore=ignore)
    
    return json_dump(result)

def add(request):
    request_data = request.REQUEST
    name = request_data.get("name")
    source_id = request_data.get("source")
    json = request_data.get("json")
    
    source_obj = Source.objects.filter(id=source_id)
    if not source_obj:
        raise Http404
    
    source_obj = source_obj[0]
    
    new_show = Show.objects.create(
        name=name,
        source=source_obj,
        json=json,
    )
    
    new_show.update_episodes()
    new_show.update_episodes_by_files()
    
    return json_dump({'url': reverse('dl_gui:detail', kwargs={"show_id": new_show.id})})

def update_show(request):
    request_data = request.REQUEST
    show_id = request_data.get("show")
    result = {}
    
    if show_id:
        show = Show.objects.filter(id=show_id)
        if show:
            show = show[0]
            new_episodes = show.update_episodes()
        for episode in new_episodes:
            result[episode.id] = {
                'airdate': episode.airdate.strftime('%d.%m.%Y'),
                'season': episode.season,
                'episode': episode.episode,
                'title': episode.title,
            }
    
    return json_dump(result)
