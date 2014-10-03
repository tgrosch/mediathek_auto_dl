#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from django.db import models
from source import Source
from config import get_config_dict, get_config
import requests, datetime, parse, os, re
from json import loads, dumps
from dl_general.helper import eng_ger

INFO_URL = 'http://www.fernsehserien.de/%s/episodenguide'


class Show(models.Model):
    class Meta:
        app_label = "dl_data"
    
    name = models.CharField("Name", max_length=100)
    source = models.ForeignKey(
        Source,
        verbose_name = "Quelle",
        related_name = "show_set",
        blank=False,
        null=False,
    )
    available = models.IntegerField("verfügbar", default=0)
    last_episode = models.DateTimeField("letzte Folge", null=True, blank=True)
    json = models.TextField("Daten")
    episodes = property(lambda s:s.episode_set)
    
    def update_episodes(self, episodes=None):
        episodes_list = episodes
        new_episodes = []
        if not episodes_list:
            episodes_list = self.source.get_available_episodes(self)
        for episode in episodes_list:
            episode.update(get_episode_data(episode))
            del episode['show']
            if self.episodes.filter(season=episode['season'], episode=episode['episode']).count() == 0:
                new_episode = Episode.objects.create(show=self, **episode)
                new_episodes.append(new_episode)
        return new_episodes
    
    def update_episodes_by_files(self, config_dict=None):
        episodes_list = get_episodes_by_files(self, config_dict)
        new_episodes = []
        for episode in episodes_list:
            episode.update(get_episode_data(episode))
            del episode['show']
            filtered_episodes = self.episodes.filter(season=episode['season'], episode=episode['episode'])
            if filtered_episodes.count() == 0:
                new_episode = Episode.objects.create(show=self, **episode)
                new_episodes.append(new_episode)
            elif episode.get('done', None) != None:
                e = filtered_episodes[0]
                e.done = episode['done']
                json = loads(e.json)
                json.update(loads(episode['json']))
                e.json = dumps(json)
                e.save()
        return new_episodes

class Episode(models.Model):
    class Meta:
        app_label = "dl_data"
        unique_together = ('season', 'episode')
    title = models.CharField("Titel", max_length=100)
    season = models.CharField("Staffel", max_length=10)
    episode = models.CharField("Folge", max_length=10)
    airdate = models.DateTimeField("letzte Folge")
    done = models.NullBooleanField("Abgeschlossen", null=True, blank=True)
    link = models.CharField("Link", max_length=200)
    json = models.TextField("Daten")
    show = models.ForeignKey(
        Show,
        verbose_name="Sendung",
        related_name="episode_set",
        blank=False,
        null=False
    )


def unicode_to_string(text):
    text = text.replace(u"ä", u"ae")
    text = text.replace(u"Ä", u"Ae")
    text = text.replace(u"ö", u"oe")
    text = text.replace(u"Ö", u"Oe")
    text = text.replace(u"ü", u"ue")
    text = text.replace(u"Ü", u"Ue")
    text = text.replace(u"ß", u"ss")
    return text.encode("ascii", "ignore")
    
def get_episode_data(episode_dict):
    if not isinstance(episode_dict, dict):
        episode_dict = episode_dict.__dict__
    
    date = episode_dict['airdate']
    if not isinstance(date, datetime.datetime):
        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    show = episode_dict['show']
    if not isinstance(show, Show):
        if show >= 0:
            show = Show.objects.get(id=show)
    
    fallback_data = {
        "season": "0",
        "episode": date.strftime("%Y%m%d"),
    }
    
    if isinstance(show, Show):
        resp = requests.get(
            INFO_URL % unicode_to_string(show.name).lower().replace(" ", "-")
        )
        parts = resp.text.split(date.strftime("%d.%m.%Y"))
        if len(parts) > 1:
            try:
                results = {
                    "season": parts[0].split("episodenliste-episodennummer")[-2].split("</span>")[0].split(">")[-1][:-1],
                    "episode": parts[0].split("episodenliste-episodennummer")[-1].split("</span>")[0].split(">")[-1],
                }
                if results['season'] == "":
                    results = {
                        "season": "0",
                        "episode": parts[0].split("episodenliste-episodennummer")[-3].split("</td>")[0].split(">")[-1],
                    }
                if int(results['episode']) > 0:
                    return results
            except:
                pass
    
    return fallback_data

def get_episodes_by_files(show, configs=None):
    episodes_list = []
    config_dict = configs
    if not config_dict:
        config_dict = get_config_dict()
    
    media_dir = config_dict.get('media_dir', False)
    episode_format = config_dict.get('episode_format', False)
    if not media_dir or not episode_format or not isinstance(show, Show):
        return episodes_list
    p = parse.compile(episode_format)
    path = os.path.join(media_dir, show.name)
    if not os.path.exists(path):
        return episodes_list
    
    date_regex = re.compile('\d{2}.\d{2}.\d{4}')
    
    for f in os.listdir(path):
        parsed = p.parse(f)
        if parsed:
            season = parsed['season'].lstrip('0')
            if not season:
                season = '0'
            episode = parsed['episode'].lstrip('0')
            if not episode:
                episode = '0'
            resp = requests.get(
                INFO_URL % unicode_to_string(show.name).lower().replace(" ", "-")
            )
            result = resp.text
            if season != '0':
                result = result.split('>Staffel %s</a>' % season)[1]
            parts = re.split('itemprop="episodeNumber">0*%s</td>' % episode, result, flags=re.IGNORECASE)
            airdate = None
            if len(parts) > 1:
                result = parts[1]
            else:
                parts = re.split('color:#808080">0*%s</span>' % episode, result, flags=re.IGNORECASE)
                if len(parts) > 1:
                    result = parts[1]
                else:
                    airdate = datetime.datetime.strptime(episode, '%Y%m%d')
            if not airdate:
                airdate = datetime.datetime.strptime(date_regex.findall(result)[0], '%d.%m.%Y')
            title = 'vom %s' % airdate.strftime("%d. %B %Y")
            for eng, ger in eng_ger.items():
                title = title.replace(eng, ger)
            parts = resp.text.split(airdate.strftime("%d.%m.%Y"))
            episodes_list.append({
                'season': season,
                'episode': episode,
                'airdate': airdate,
                'title': title,
                'done': True,
                'show': show,
                'json': dumps({
                    'file': os.path.join(path, f),
                }),
            })
    
    return episodes_list
