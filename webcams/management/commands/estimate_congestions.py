from django.core.management.base import BaseCommand
from django.utils import timezone
from webcams.models import Webcam, CongestionEstimate
import urllib.request
import numpy as np
import cv2
import torch
from ultralytics import YOLO

device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("yolo11n.pt")
model.to(device)
class_ids = [k for k, v in model.names.items() if v in ["car", "bus", "truck"]]

class Command(BaseCommand):
    help = "Estimate Webcam congestions"
    def handle(self, *args, **options):
        webcams = Webcam.objects.all()
        self.stdout.write(f"Congestion estimation for {len(webcams)} cameras started.")
        self.stdout.write(f"Running {model.model_name} model on {device} device.")
        for i, webcam in enumerate(webcams, start=1):
            self.stdout.write(f"Analyzing image {i}/{len(webcams)} ", ending="")
            with urllib.request.urlopen(webcam.image_url) as response:
                image = response.read()
            image_array = np.frombuffer(image, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            results = model.predict(
                source=image,
                device=device,
                classes=class_ids,
                verbose=False,
                conf=0.60)
            num_vehicles = len(results[0].boxes)
            cest = CongestionEstimate.objects.create(
                webcam=webcam,
                datetime=timezone.now(),
                num_vehicles=num_vehicles,
                score=0)
            self.stdout.write(str(cest))
