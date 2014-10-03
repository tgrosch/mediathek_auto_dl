from django.db import models
from django.utils.timezone import now as django_now
from json import loads, dumps


class Config(models.Model):
    class Meta:
        app_label = "dl_data"
    key = models.CharField(max_length=200, default="", unique=True)
    value = models.TextField(blank=True, default="")
    last_access = models.DateTimeField()

def set_config(key, value):
    conf = Config.objects.filter(key=key)
    if conf.count() == 0:
        Config.objects.create(key=key, value=dumps(value), last_access=django_now())
    else:
        conf = conf[0]
        if not value is None:
            conf.value = dumps(value)
            conf.last_access = django_now()
            conf.save()
        else:
            conf.delete()

def get_config(key):
    conf = Config.objects.filter(key=key)
    if conf.exists():
        conf = conf[0]
        return loads(conf.value)
    else:
        return None

def get_config_dict(contains=False):
    conf = Config.objects.all()
    if contains:
        conf = conf.filter(key__contains=contains)
    conf_dict = dict(conf.values_list('key', 'value'))
    for key in conf_dict.keys():
        conf_dict[key] = loads(conf_dict[key])
    
    return conf_dict
