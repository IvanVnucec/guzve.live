
from urllib.request import urlopen, Request
import os

DEBUG = int(os.environ.get("DEBUG", 0))
COUNT = int(os.environ.get("COUNT", 1))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
os.makedirs("build", exist_ok=True)

print("Fetching cams metadata...")
import json
req = Request("https://api.hak.hr/rest/2.8/webcams/?token=9ba354b85afbd2", headers={"User-Agent": UA})
with urlopen(req) as response:
    ctgs = json.loads(response.read().decode())
cams = []
for ctg in ctgs:
    for wgs in ctg["WebcamGroups"]:
        for cam in wgs["Cams"]:
            cams.append({
                "title": cam["Title"],
                "url": f'https://m.hak.hr/cam.asp?id={cam["CamID"]}',
                "nveh": 0,
                "ctg": ctg["Key"],
            })
cams = list({cam["url"]: cam for cam in cams}.values())

if COUNT > 0:
    print("Counting vehicles...")
    import numpy as np
    import cv2
    import torch
    print("Loading model...")
    import ultralytics as ul
    model = ul.YOLO("yolo11n.pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f'Using {device} device...')
    model.to(device)
    class_ids = [k for k, v in model.names.items() if v in ["car", "bus", "truck"]]
    for i, cam in enumerate(cams, start=1):
        req = Request(cam["url"], headers={"User-Agent": UA})
        with urlopen(req) as response:
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
        print(f'{i}/{len(cams)} {cam["title"]}: {cam["nveh"]}')
        if DEBUG > 0:
            import uuid
            annotated_image = results[0].plot()
            os.makedirs("build/images", exist_ok=True)
            filename = f'{uuid.uuid4()}.jpg'
            cv2.imwrite(f'build/images/{filename}', annotated_image)
            cam["url"] = f'images/{filename}'

print("Writing HTML")
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
def write_template(filename, cams, lexpr=None, title=None):
    with open(f'build/{filename}', "w", encoding="utf-8") as f:
        cams = filter(lexpr, cams)
        cams = sorted(cams, key=lambda c: (-c["nveh"], c["title"], c["url"]))
        f.write(env.get_template("base.html").render({"template_name": filename, "cams": cams, "title": title}))
write_template("index.html", cams)
write_template("autoceste.html", cams, lambda c: c["ctg"].startswith('A'), "Autoceste")
write_template("drzavne_ceste.html", cams, lambda c: c["ctg"] in ["D8", "HC", "MJ"], "Državne ceste")
write_template("granicni_prijelazi.html", cams, lambda c: c["ctg"]=="GP", "Granični prijelazi")
write_template("mostovi.html", cams, lambda c: c["ctg"]=="MT", "Mostovi")
write_template("trajekti.html", cams, lambda c: c["ctg"]=="TP", "Trajekti")
import shutil
shutil.copy2("templates/og-image.jpg", "build/og-image.jpg")
print("Done")
