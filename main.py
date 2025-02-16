from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup

with urlopen('https://www.hak.hr/info/kamere/') as response:
    html = response.read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')
ul = soup.find('ul', class_='groups')

cam_groups = []
for li in ul.find_all('li'):
    a = li.find('a')
    name = a.get_text(strip=True)
    url = f'https://www.hak.hr/info/kamere/grupa/{a["data-id"]}'
    cam_groups.append({
        'name': name,
        'url': url,
        'cams': []
    })

for group in cam_groups:
    with urlopen(group['url']) as response:
        html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    imgs = soup.find_all('img', class_='cam lazyload')
    for img in imgs:
        name = img['alt']
        url = f'https://www.hak.hr/info/kamere/{img["data-id"]}'
        group['cams'].append({
            'name': name,
            'url': url
        })

from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F

# Load the model and processor
model_name = "ilsilfverskiold/traffic-levels-image-classification"
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

for group in cam_groups:
    print(f"Group: {group['name']}")
    for cam in group['cams']:
        url = cam['url']
        import requests
        from io import BytesIO
        response = requests.get(url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Perform inference
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        # Get predicted class
        predicted_class_idx = logits.argmax(-1).item()
        predicted_class = model.config.id2label[predicted_class_idx]

        print(f"  {cam['name']}, {cam['url']}, {predicted_class}")

        # Get probabilities
        #probabilities = F.softmax(logits, dim=-1)
        #for idx, prob in enumerate(probabilities[0]):
        #    class_label = model.config.id2label[idx]
        #    print(f"Probability for {class_label}: {prob.item():.4f}")
        #print()