# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Config'
        db.create_table(u'dl_data_config', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('value', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('last_access', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('dl_data', ['Config'])

        # Adding model 'Source'
        db.create_table(u'dl_data_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('app_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('json', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('dl_data', ['Source'])

        # Adding model 'Show'
        db.create_table(u'dl_data_show', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='show_set', to=orm['dl_data.Source'])),
            ('available', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_episode', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('dl_data', ['Show'])

        # Adding model 'Episode'
        db.create_table(u'dl_data_episode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('season', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('episode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('airdate', self.gf('django.db.models.fields.DateTimeField')()),
            ('done', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('show', self.gf('django.db.models.fields.related.ForeignKey')(related_name='episode_set', to=orm['dl_data.Show'])),
        ))
        db.send_create_signal('dl_data', ['Episode'])


    def backwards(self, orm):
        # Deleting model 'Config'
        db.delete_table(u'dl_data_config')

        # Deleting model 'Source'
        db.delete_table(u'dl_data_source')

        # Deleting model 'Show'
        db.delete_table(u'dl_data_show')

        # Deleting model 'Episode'
        db.delete_table(u'dl_data_episode')


    models = {
        'dl_data.config': {
            'Meta': {'object_name': 'Config'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'last_access': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        'dl_data.episode': {
            'Meta': {'object_name': 'Episode'},
            'airdate': ('django.db.models.fields.DateTimeField', [], {}),
            'done': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'episode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'season': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'episode_set'", 'to': "orm['dl_data.Show']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dl_data.show': {
            'Meta': {'object_name': 'Show'},
            'available': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'last_episode': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'show_set'", 'to': "orm['dl_data.Source']"})
        },
        'dl_data.source': {
            'Meta': {'object_name': 'Source'},
            'app_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['dl_data']