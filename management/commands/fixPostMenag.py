# -*- coding: utf-8 -*-
from woodcutter.models import *
from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404, render


class Command(BaseCommand):
    help = "fixes post-menagerie version mislabelled logs"

    def handle(self, *args, **options):
        for log in GameLog.objects.filter(version=0):
            if log.log[:5] == "0|130":
                log.version = 3
                log.save()
