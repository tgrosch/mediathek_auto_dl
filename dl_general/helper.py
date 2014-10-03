#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import datetime, dateutil.parser

def html_to_text(text):
    text = text.replace(u"&auml;", u"ä")
    text = text.replace(u"&Auml;", u"Ä")
    text = text.replace(u"&ouml;", u"ö")
    text = text.replace(u"&Ouml;", u"Ö")
    text = text.replace(u"&uuml;", u"ü")
    text = text.replace(u"&Uuml;", u"Ü")
    text = text.replace(u"&szlig;", u"ß")
    text = text.replace(u"&amp;", u"&")
    return text

month_translation = (
    (u"Januar", u"January"),
    (u"Februar", u"February"),
    (u"März", u"March"),
    (u"Mai", u"May"),
    (u"Juni", u"June"),
    (u"Juli", u"July"),
    (u"Oktober", u"October"),
    (u"Dezember", u"December"),
)
ger_eng = dict(month_translation)
eng_ger = dict([[v,k] for k,v in ger_eng.items()])

def parse_date(date_string):
    date = None
    
    date_string = date_string.encode("utf8")
    
    for ger, eng in ger_eng.items():
        date_string = date_string.replace(ger, eng)
    
    try:
        date = datetime.datetime.strptime(date_string, "%d. %B %Y")
    except ValueError:
        try:
            date = datetime.datetime.strptime(date_string, "%d.%m.%Y")
        except ValueError:
            date = dateutil.parser.parse(date_string)
    return date
