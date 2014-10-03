from dl_data.models import Episode


def get_shows_by_source(content, ignore=False):
    shows_by_source = []
    for source_obj in Source.objects.all():
        show_list = get_shows(content, source_obj, ignore.get(source_obj.id, ()))
        available_shows = []
        for show_dict in show_list:
            available_shows.append(Show(source=source_obj, **show_dict))
        shows_by_source.append((source_obj, available_shows))
    
    return shows_by_source

def get_shows(content, source_obj, ignore=False):
    show_list = source_obj.get_available_shows(content)
    if ignore:
        show_list = [s for s in show_list if not s.get('name', '') in ignore]
    
    for show in show_list:
        show['available'] = len(get_episodes(show, source_obj))
    
    return show_list

def get_episodes(show, source_obj=None):
    source = source_obj
    if not source:
        source = show.source
    
    episode_list = source.get_available_episodes(show)
    return episode_list
