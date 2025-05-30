import streamlit as st
from PIL import Image
import numpy as np
import cv2
import os
from ultralytics import YOLO
import yaml
import tempfile
import time
import requests
import glob

BOT_TOKEN = '8040229917:AAGSVVbPpGol1E-ImXAdLkm2t71Pwf-Zi7A'
CHAT_ID = '1843576106'

folder_path = "content/images/test"

import glob

# Путь к папке с изображениями
folder_path = "content/images/test"

# Получаем все изображения
image_paths = glob.glob(os.path.join(folder_path, "*.jpg")) + \
              glob.glob(os.path.join(folder_path, "*.jpeg")) + \
              glob.glob(os.path.join(folder_path, "*.png"))


# Отправка сообщения в телеграм
def send_telegram_photo(photo_path, caption):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': CHAT_ID, 'caption': caption}
        response = requests.post(url, files=files, data=data)
    return response

# Загрузка и кэширование модели YOLO
@st.cache_resource
def load_model():
    model = YOLO('best.pt')
    return model

import yaml
dict_file = {
    'train': '/content/images/val',
    'val': '/content/images/test',
    'nc': 3,
    'names': ['helmet', 'vest', 'head',]}
with open('hard_head.yaml', 'w+') as file:
    documents = yaml.dump(dict_file, file)

model = load_model()

# Function to draw bounding boxes and labels on image
def box_label(image, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
    lw = max(round(sum(image.shape) / 2 * 0.003), 2)
    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    cv2.rectangle(image, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)
    if label:
        tf = max(lw - 1, 1)  # font thickness
        w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
        outside = p1[1] - h >= 3
        p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
        cv2.rectangle(image, p1, p2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image,
                    label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                    0,
                    lw / 3,
                    txt_color,
                    thickness=tf,
                    lineType=cv2.LINE_AA)

# Function to plot bounding boxes on image
def plot_bboxes(image, boxes, labels=[], colors=[], score=True, conf=None):
    # Define COCO labels
    if labels == []:
        labels = {0: u'__background__', 1: u'person', 2: u'bicycle',3: u'car', 4: u'motorcycle', 5: u'airplane', 6: u'bus', 7: u'train', 8: u'truck', 9: u'boat', 10: u'traffic light', 11: u'fire hydrant', 12: u'stop sign', 13: u'parking meter', 14: u'bench', 15: u'bird', 16: u'cat', 17: u'dog', 18: u'horse', 19: u'sheep', 20: u'cow', 21: u'elephant', 22: u'bear', 23: u'zebra', 24: u'giraffe', 25: u'backpack', 26: u'umbrella', 27: u'handbag', 28: u'tie', 29: u'suitcase', 30: u'frisbee', 31: u'skis', 32: u'snowboard', 33: u'sports ball', 34: u'kite', 35: u'baseball bat', 36: u'baseball glove', 37: u'skateboard', 38: u'surfboard', 39: u'tennis racket', 40: u'bottle', 41: u'wine glass', 42: u'cup', 43: u'fork', 44: u'knife', 45: u'spoon', 46: u'bowl', 47: u'banana', 48: u'apple', 49: u'sandwich', 50: u'orange', 51: u'broccoli', 52: u'carrot', 53: u'hot dog', 54: u'pizza', 55: u'donut', 56: u'cake', 57: u'chair', 58: u'couch', 59: u'potted plant', 60: u'bed', 61: u'dining table', 62: u'toilet', 63: u'tv', 64: u'laptop', 65: u'mouse', 66: u'remote', 67: u'keyboard', 68: u'cell phone', 69: u'microwave', 70: u'oven', 71: u'toaster', 72: u'sink', 73: u'refrigerator', 74: u'book', 75: u'clock', 76: u'vase', 77: u'scissors', 78: u'teddy bear', 79: u'hair drier', 80: u'toothbrush'}
    # Define colors
    if colors == []:
        colors = [(89, 161, 197),(67, 161, 255),(19, 222, 24),(186, 55, 2),(167, 146, 11),(190, 76, 98),(130, 172, 179),(115, 209, 128),(204, 79, 135),(136, 126, 185),(209, 213, 45),(44, 52, 10),(101, 158, 121),(179, 124, 12),(25, 33, 189),(45, 115, 11),(73, 197, 184),(62, 225, 221),(32, 46, 52),(20, 165, 16),(54, 15, 57),(12, 150, 9),(10, 46, 99),(94, 89, 46),(48, 37, 106),(42, 10, 96),(7, 164, 128),(98, 213, 120),(40, 5, 219),(54, 25, 150),(251, 74, 172),(0, 236, 196),(21, 104, 190),(226, 74, 232),(120, 67, 25),(191, 106, 197),(8, 15, 134),(21, 2, 1),(142, 63, 109),(133, 148, 146),(187, 77, 253),(155, 22, 122),(218, 130, 77),(164, 102, 79),(43, 152, 125),(185, 124, 151),(95, 159, 238),(128, 89, 85),(228, 6, 60),(6, 41, 210),(11, 1, 133),(30, 96, 58),(230, 136, 109),(126, 45, 174),(164, 63, 165),(32, 111, 29),(232, 40, 70),(55, 31, 198),(148, 211, 129),(10, 186, 211),(181, 201, 94),(55, 35, 92),(129, 140, 233),(70, 250, 116),(61, 209, 152),(216, 21, 138),(100, 0, 176),(3, 42, 70),(151, 13, 44),(216, 102, 88),(125, 216, 93),(171, 236, 47),(253, 127, 103),(205, 137, 244),(193, 137, 224),(36, 152, 214),(17, 50, 238),(154, 165, 67),(114, 129, 60),(119, 24, 48),(73, 8, 110)]

    # Plot each box
    image = image.copy()
    for box in boxes:
        # Add score in label if score=True
        if score:
            label = labels[int(box[-1])+1] + " " + str(round(100 * float(box[-2]),1)) + "%"
        else:
            label = labels[int(box[-1])+1]
        # Filter every box under conf threshold if conf threshold setted
        if conf:
            if box[-2] > conf:
                color = colors[int(box[-1]) % len(colors)]
                box_label(image, box, label, color)
        else:
            color = colors[int(box[-1]) % len(colors)]
            box_label(image, box, label, color)

    # Show image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    

    return image

def plot_results(results, image_path=None, image_data=None, result_name=None, box_type=False, labels=[]):
    for idx, result in enumerate(results):
        image = None
        if image_path:
            image = Image.open(image_path)
        else:
            image = image_data
        image = np.asarray(image)
        img = None
        if not box_type:
            boxes = result.boxes.data
            img = plot_bboxes(image, boxes, labels=labels, score=True)
        else:
            img = plot_bboxes(image, result, score=True)
        result_image_name = result_name if result_name else image_path.split('/')[-1]
        cv2.imwrite(f'content/results/{result_image_name}', img)
    return img

# Load image
st.title('Детекция индивидуальных средств защиты на стройплощадке')
# Загрузите изображение
image = Image.open('Frame 48099524.jpg')

# Function to predict the name of the image
def predict_name(test_image):
    labels = {0: u'__background__', 1: u'helmet', 2: u'vest', 3: u'head'}
    path = f"content/images/test/{test_image}"

    results = model.predict(path)
    print("-----------")
    print(results[0].boxes)
    print("-----------")

    conf = results[0].boxes.conf  
    cls = results[0].boxes.cls  

    result_name = 'hardhat_pred_' + test_image
    print(result_name)
    result_image = plot_results(results, image_path=path, labels=labels, result_name=result_name)
    time.sleep(1)

    send_photo = False
    has_vest = False

    labels = {0: u'helmet', 1: u'vest', 2: u'head', 3: u'__background__'}
    
    for i, (confidence, class_id) in enumerate(zip(conf, cls)):
        label = labels[int(class_id)] 
        confidence_val = float(confidence)
        print(f"Объект {i+1}: {label} - Уверенность: {confidence:.2f} - Номер: {int(class_id)}")
        if label == 'vest':
            has_vest = True
            if confidence_val < 0.6:
                send_photo = True
        elif label == 'helmet':
            if confidence_val < 0.6:
                send_photo = True
        elif label == 'head':
            send_photo = True

    if not has_vest:
        send_photo = True

    if send_photo:
        send_telegram_photo(path, caption="Нарушение СИЗ обнаружено")
    else:
        print("СИЗ в порядке, отправка в телеграм не требуется.")
    return result_image

# Загрузите изображение
image = Image.open('Frame 48099524.jpg')

# Отобразите изображение на странице Streamlit
st.image(image, caption='Изображение для детекции', use_container_width=True)
uploaded_file = st.file_uploader("Выберите изображение для детекции", type=["jpg", "jpeg", "png"])

if image_paths:
    st.info(f"Анализирую {len(image_paths)} изображений в папке...")
    for path in image_paths:
        try:
            st.markdown(f"Обработка: {os.path.basename(path)}")
            result_image = predict_name(os.path.basename(path))
            st.image(result_image, caption=f'Результат: {os.path.basename(path)}', use_container_width=True)
            time.sleep(0.5)  # Не обязательно, но может помочь
        except Exception as e:
            st.error(f"Ошибка при обработке {path}: {e}")
else:
    st.warning("В папке нет изображений для анализа.")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Оригинальное изображение', use_container_width=True)

    # Detect objects in image
    results = model.predict(image)

    # Define labels for detected objects
    labels = {0: u'__background__', 1: u'helmet', 2: u'vest', 3: u'head'}

    # Plot bounding boxes on image
    image_np = np.array(image)
    image_np = plot_bboxes(image_np, results[0].boxes.data, labels=labels, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    st.image(image_np, caption='Результаты детекции', use_container_width=True)

    # Predict the name of the image
    result_image = predict_name(uploaded_file.name)
    st.image(result_image, caption='Результаты детекции', use_container_width=True)
st.markdown("""
    <script>
        setTimeout(function(){
           window.location.reload(1);
        }, 10000);
    </script>
""", unsafe_allow_html=True)
