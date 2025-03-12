import urllib.request
import json
import os
import re

IMAGES_DIR = "webcam_images"

os.makedirs(IMAGES_DIR, exist_ok=True)

url = 'https://api.hak.hr/rest/2.8/webcams/?token=9ba354b85afbd2'
with urllib.request.urlopen(url) as response:
    groups = json.loads(response.read().decode())

for group in groups:
    group_name = group['Name']
    print(group_name)
    webcam_groups = group['WebcamGroups']
    for webcam_group in webcam_groups:
        webcam_group_title = webcam_group['Title']
        print(f'  {webcam_group_title}')
        cams = webcam_group['Cams']
        for cam in cams:
            cam_title = cam['Title']
            id = cam['CamID']
            last_update = cam['LastUpdate']
            print(last_update)
            print(f'    {cam_title}')
            url = f"https://api.hak.hr/rest/2.8/webcams/{id}/?token=9ba354b85afbd2"
            title = f"{group_name}_{webcam_group_title}_{cam_title}_{id}_{last_update}"
            clean_title = "".join(c if c.isalnum() else "_" for c in title)
            clean_title = re.sub('_+', '_', clean_title)
            filename = os.path.join(IMAGES_DIR, f"{clean_title}.jpeg")
            urllib.request.urlretrieve(url, filename)
