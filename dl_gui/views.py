from django.shortcuts import render, redirect, render_to_response
from json import loads, dumps
from dl_data.models import Show, Episode, Source

# Create your views here.
def index(request):
    render_dict = {
        
    }
    
    return render(request, 'dl_gui/index.html', render_dict)

def overview(request):
    render_dict = {
        'shows': Show.objects.prefetch_related('episodes').all().order_by('name'),
    }
    
    return render(request, 'dl_gui/overview.html', render_dict)

def detail(request, show_id, search_result=False):
    show = Show.objects.select_related('source').prefetch_related('episodes').filter(id=show_id)
    if show:
        show = show[0]
    else:
        return redirect('dl_gui:overview')
    
    episodes = show.episodes.all().order_by('-airdate')
    
    render_dict = {
        'show_name': show.name,
        'show': show,
        'episodes': episodes,
        'display_search': search_result,
    }
    
    return render(request, 'dl_gui/detail.html', render_dict)

def search(request):
    data = request.REQUEST
    content = data.get('search')
    
    render_dict = {
        'show_name': content,
    }
    
    if content:
        pattern = '.*%s.*' % content.replace(' ', '|')
        
        show_all = Show.objects.prefetch_related('episodes', 'source').all().order_by("name")
        
        filtered_shows = list(show_all.filter(name__iregex=pattern))
        
#        if qs.count() == 1:
#            return detail(request, qs[0].id, search_result=content)
        
        sources = Source.objects.all()
        
        ignore_dict = {}
        for sid, name in show_all.values_list('source__id', 'name'):
            temp = ignore_dict.get(sid, ())
            temp += (name,)
            ignore_dict[sid] = temp
        
        source_dict = {}
        for s in sources.values('id', 'app_name', 'name'):
            sid = s['id']
            del s['id']
            source_dict[sid] = s
        
        content_dict = {
            'download_shows': filtered_shows,
            'sources': sources,
            'sources_dict': dumps(source_dict),
            'ignore_dict': dumps(ignore_dict),
        }
        
        render_dict.update(content_dict)
    
    return render(request, 'dl_gui/search.html', render_dict)

def manage(request):
    return index(request)
