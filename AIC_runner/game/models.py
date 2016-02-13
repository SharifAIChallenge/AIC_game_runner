# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Competition(models.Model):
    timestamp = models.DateTimeField(verbose_name=_('timestamp'), auto_now=True)
    title = models.CharField(verbose_name=_('title'), max_length=200)
    site = models.OneToOneField(Site, verbose_name=_('site'), null=True)
    max_members = models.PositiveSmallIntegerField(verbose_name=_("max team members count"), default=3)
    min_members = models.PositiveSmallIntegerField(verbose_name=_("min team members count"), default=3)

    registration_start_date = models.DateTimeField(verbose_name=_("registration start date"), null=True)
    registration_finish_date = models.DateTimeField(verbose_name=_("registration finish date"), null=True)

    players_per_game = models.PositiveIntegerField(verbose_name=_("number of players per game"), default=2, blank=True)
    supported_langs = models.ManyToManyField('base.ProgrammingLanguage', verbose_name=_("supported languages"), blank=True)
    composer = models.FileField(verbose_name=_("docker composer"), null=True, blank=True)
    server = models.ForeignKey('base.DockerContainer', verbose_name=_("server container"), null=True, blank=True)
    additional_containers = models.ManyToManyField('base.DockerContainer', verbose_name=_("additional containers"), related_name='+', blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('competition')
        verbose_name_plural = _('competitions')


class Game(models.Model):
    timestamp = models.DateTimeField(verbose_name=_('timestamp'), auto_now=True)
    competition = models.ForeignKey('game.Competition', verbose_name=_('competition'))
    title = models.CharField(verbose_name=_('title'), max_length=200)
    players = models.ManyToManyField('base.Submit', verbose_name=_('players'), through='game.GameTeamSubmit')
    config = models.FileField(verbose_name=_('config'))

    pre_games = models.ManyToManyField('game.Game', verbose_name=_('pre games'), blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('game')
        verbose_name_plural = _('games')


class GameTeamSubmit(models.Model):
    submit = models.ForeignKey('base.Submit', verbose_name=_('team submit'))
    game = models.ForeignKey('game.Game', verbose_name=_('game'))

    score = models.IntegerField(verbose_name=_('score'), default=0)

    class Meta:
        ordering = ('score',)
