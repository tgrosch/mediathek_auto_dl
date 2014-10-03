#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import requests, re, locale, datetime, dateutil.parser
from json import loads, dumps
from xml.dom.minidom import parseString
from dl_general.helper import html_to_text, parse_date

SOURCE_NAME = 'ARD'

BASE_URL = 'http://www.ardmediathek.de'
SEARCH_URL = BASE_URL + '/tv/suche'
XML_URL = ''
SHOW_PREFIX = '/tv/'
SHOW_LINK = BASE_URL + SHOW_PREFIX + '%s/Sendung?documentId=%s'
RSS_URL = SHOW_LINK + '&rss=true'
EPISODE_PREFIX = ''
DOWNLOAD_PREFIX = ''


def get_available_shows(self, content):
    next_link = SEARCH_URL
    another_page = True
    show_list = []
    link_set = ()
    request_parameters = {
        'params': {'searchText': content},
    }  
    
    next_regex = re.compile(u'<a href=".*=page.\d+">\s+&gt;\s+</a>', re.IGNORECASE)
    show_regex = re.compile(u'<a href=".*" class="textLink">\s+.*\s+.*\s+.*\s+.*\s+</a>', re.IGNORECASE)
    link_regex = re.compile(u'<a href="%s[%%\-\w]+/' % SHOW_PREFIX, re.IGNORECASE)
    name_regex = re.compile(u'<p class="dachzeile">.*</p>', re.IGNORECASE)
    id_regex = re.compile(u'bcastId=\d+"', re.IGNORECASE)
    
    while (another_page):
        resp = requests.post(
            next_link,
            **request_parameters
        )
        parts = show_regex.findall(resp.text)

        for part in parts:
            link_split = part.split('">')
            link_id = id_regex.findall(part)[0][8:-1]
            link_name = link_regex.findall(part)[0].split('/')[-2]
            rss_link = RSS_URL % (link_name, link_id)
            names_found = name_regex.findall(part)
            if not rss_link in link_set and names_found:
                show_name = html_to_text(names_found[0].split(">")[1].split("<")[0])
                channel_link = SHOW_LINK % (link_name, link_id)
                json = {
                    'channel_link': channel_link,
                    'rss_link': rss_link,
                    'link_id': link_id,
                }
                show_list.append({
                    'name': show_name,
                    'json': dumps(json),
                })
            link_set += (rss_link,)
        
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
        name = show['name'].lower()
        airdate = ""
        if name == "tagesschau" and "20:00 Uhr" in title:
            episode_title = "20:00 Uhr"
            airdate = "x"
        elif name == "tatort" and "(Video tgl. ab 20 Uhr)" in title and not u" - Hörfassung" in title:
            text = "Tatort - "
            offset = len(text)
            endpos = title.find("(Video tgl. ab 20 Uhr)") - 1
            episode_title = title[len(text):endpos]
            airdate = "x"
        else:
            text = " vom "
            pos = title.find(text)
            if pos > 0:
                episode_title = title[pos+1:]
                airdate = title[pos+len(text):]
        if airdate and not u'(mit Gebärdensprache)' in title:
            pos2 = airdate.find(" ")
            if pos2 > 0:
                airdate = airdate[:pos2]
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
                'title': episode_title,
                'airdate': date,
                'json': dumps(json),
                'show': show_id,
            })
    
    return episode_list
