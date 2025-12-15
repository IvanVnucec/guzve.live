from django.core.management.base import BaseCommand
from django.utils import timezone
from webcams.models import Category, Group, Webcam
import urllib.request
import json
from datetime import datetime

class Command(BaseCommand):
    help = "Fetches Webcams metadata"
    def handle(self, *args, **options):
        with urllib.request.urlopen("https://api.hak.hr/rest/2.8/webcams/?token=9ba354b85afbd2") as response:
            categories = json.loads(response.read().decode())
            for cat in categories:
                category, _ = Category.objects.update_or_create(key=cat["Key"],
                                                                defaults={"seokey": cat["SeoKey"], "name": cat["Name"], "icon_url": cat["IconUrl"]})
                for g in cat["WebcamGroups"]:
                    group, _ = Group.objects.update_or_create(key=g["Key"],
                                                            defaults={"title": g["Title"], "lat": g["Lat"], "lon": g["Lon"], "category": category})
                    for cam in g["Cams"]:
                        last_update = datetime.fromisoformat(cam["LastUpdate"]).replace(tzinfo=timezone.get_current_timezone())
                        Webcam.objects.update_or_create(id=cam["CamID"],
                                                        defaults={
                                                            "title": cam["Title"],
                                                            "last_update": last_update,
                                                            "heading": cam["Heading"],
                                                            "refresh_delay": cam["RefreshDelay"],
                                                            "map_radius": cam["MapRadius"],
                                                            "lat": cam["Lat"],
                                                            "lon": cam["Lon"],
                                                            "image_width": cam["ImageWidth"],
                                                            "image_height": cam["ImageHeight"],
                                                            "group": group
                                                        })
