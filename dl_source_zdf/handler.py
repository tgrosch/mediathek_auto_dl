#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import requests, re, locale
from json import loads, dumps
from xml.dom.minidom import parseString
from dl_general.helper import html_to_text, parse_date

SOURCE_NAME = 'ZDF'

BASE_URL = 'http://www.zdf.de'
SEARCH_URL = BASE_URL + '/ZDFmediathek/suche?flash=off'
RSS_URL = BASE_URL + '/ZDFmediathek/rss/%s?view=rss'
XML_URL = BASE_URL + '/ZDFmediathek/xmlservice/web/beitragsDetails?id=%s'
SHOW_PREFIX = '/ZDFmediathek/kanaluebersicht/'
EPISODE_PREFIX = '/ZDFmediathek/beitrag/video/'
DOWNLOAD_PREFIX = 'http://rodl.zdf.de/none/zdf'


def get_available_shows(self, content):
    next_link = SEARCH_URL
    another_page = True
    show_list = []
    link_set = ()
    request_parameters = {
        'params': {'sucheText': content},
    }
    
    next_regex = re.compile(u'<a href=".*" class="forward">weiter</a>', re.IGNORECASE)
    show_regex = re.compile(u'<b><a href="%s.*">.*<br' % SHOW_PREFIX, re.IGNORECASE)
    id_regex = re.compile(u'/\d+\?', re.IGNORECASE)
    
    while (another_page):
        resp = requests.post(
            next_link,
            **request_parameters
        )
        parts = show_regex.findall(resp.text)

        for part in parts:
            link_split = part.split('">')
            current_link = BASE_URL + link_split[0].split('"')[1]
            if not current_link in link_set:
                link_id = id_regex.findall(current_link)[0][1:-1]
                rss_link = RSS_URL % link_id
                json = {
                    'channel_link': current_link,
                    'rss_link': rss_link,
                    'link_id': link_id
                }
                show_list.append({
                    'name': html_to_text(link_split[1].split('<')[0]),
                    'json': dumps(json),
                })
            link_set += (current_link,)
        
        parts = next_regex.findall(resp.text)
        if not parts:
            another_page = False
        else:
            next_link = BASE_URL + html_to_text(parts[0].split('"')[1])
            another_page = not next_link in link_set
            link_set += (next_link,)
            request_parameters = {}
    
    return show_list

def get_available_episodes(self, show):
    episode_list = []
    if not isinstance(show, dict):
        show = show.__dict__
    json = loads(show['json'])
    rss_link = json['rss_link']
    
    resp = requests.get(rss_link)
    rss_data = parseString(resp.text.encode("utf8"))

    for item in rss_data.getElementsByTagName("item"):
        title = item.getElementsByTagName("title")[0].childNodes[0].nodeValue
        pos = title.find(" vom ")
        if pos > 0:
            airdate = title[pos+5:]
            try:
                date = parse_date(airdate)
            except:
                date = parse_date(item.getElementsByTagName("dc:date")[0].childNodes[0].nodeValue[:-1])
            link = item.getElementsByTagName("link")[0].childNodes[0].nodeValue
            json = {
                'link': link,
            }
            show_id = show.get('id', -1)
            episode_list.append({
                'title': title[pos+1:],
                'airdate': date,
                'json': dumps(json),
                'show': show_id,
            })
    
    return episode_list
