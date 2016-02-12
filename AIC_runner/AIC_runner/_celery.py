# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings

import celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AIC_runner.settings')

app = celery.Celery('AIC')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
