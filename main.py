import urllib.request
import json
import os

class Camera:
    def __init__(self, id:int, title:str, timestamp:str) -> None:
        self.id:str = str(id)
        self.title:str = title
        self.timestamp:str = timestamp
        self.url:str = f"https://api.hak.hr/rest/2.8/webcams/{self.id}/?token=9ba354b85afbd2"

    def __str__(self) -> str:
        return f"{self.title}, {self.url}"

def fetch_cameras() -> list[Camera]:
    cameras:list[Camera] = []

    url = "https://api.hak.hr/rest/2.8/webcams/?token=9ba354b85afbd2"
    with urllib.request.urlopen(url) as response:
        groups = json.loads(response.read().decode())

    for group in groups:
        webcam_groups = group["WebcamGroups"]
        for webcam_group in webcam_groups:
            cams = webcam_group["Cams"]
            for cam in cams:
                id = cam["CamID"]
                title = cam["Title"]
                timestamp = cam["LastUpdate"]
                cameras.append(Camera(id, title, timestamp))

    return cameras

def get_number_of_vehicles(img_data) -> int:
    from ultralytics import YOLO
    import cv2
    import numpy as np

    model = YOLO("yolo11n.pt")

    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    class_names = model.names
    target_classes = ["car", "bus", "truck"]
    class_ids = [k for k, v in class_names.items() if v in target_classes]

    results = model.predict(source=img, device="cuda", classes=class_ids, verbose=False)
    num_vehicles = len(results[0].boxes)

    return num_vehicles

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {}

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)

def main():
    while True:
        db = load_json("db.json")

        cameras = fetch_cameras()
        for i,cam in enumerate(cameras, start=1):
            with urllib.request.urlopen(cam.url) as response:
                img_data = response.read()
            vehicles_num = get_number_of_vehicles(img_data)

            if cam.id not in db:
                db[cam.id] = {"title": cam.title, "vehicles_history": []}
            db[cam.id]["vehicles_history"].append([cam.timestamp, vehicles_num])

            print(f"{i}/{len(cameras)}", cam, vehicles_num)

        save_json("db.json", db)

if __name__ == "__main__":
    main()
