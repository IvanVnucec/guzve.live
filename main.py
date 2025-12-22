
from urllib.request import urlopen
import os

DEBUG = os.environ.get("DEBUG", 0)
os.makedirs("build", exist_ok=True)

print("Fetching cams metadata...")
import json
with urlopen("https://api.hak.hr/rest/2.8/webcams/?token=9ba354b85afbd2") as response:
    ctgs = json.loads(response.read().decode())
cams = [{
    "title": cam["Title"],
    "url": f"https://m.hak.hr/cam.asp?id={cam["CamID"]}",
    "nveh": 0} for ctg in ctgs for wgs in ctg["WebcamGroups"] for cam in wgs["Cams"]]
cams = list({cam["url"]: cam for cam in cams}.values())

print("Counting vehicles...")
import numpy as np
import cv2
import torch
print("Loading model...")
import ultralytics as ul
model = ul.YOLO("yolo11n.pt")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device...")
model.to(device)
class_ids = [k for k, v in model.names.items() if v in ["car", "bus", "truck"]]
for i, cam in enumerate(cams, start=1):
    with urlopen(cam["url"]) as response:
        image = response.read()
    image_array = np.frombuffer(image, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    results = model.predict(
        source=image,
        device=device,
        classes=class_ids,
        verbose=False,
        conf=0.3)
    cam["nveh"] = len(results[0].boxes)
    print(f"{i}/{len(cams)} {cam["title"]}: {cam["nveh"]}")
    if DEBUG:
        import uuid
        annotated_image = results[0].plot()
        os.makedirs("build/images", exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        cv2.imwrite(f"build/images/{filename}", annotated_image)
        cam["url"] = f"images/{filename}"

print("Writing HTML")
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
with open("build/index.html", "w", encoding="utf-8") as f:
    f.write(env.get_template("index.html").render({"cams": sorted(cams, key=lambda c: (-c["nveh"], c["url"]))}))
print("Done")
