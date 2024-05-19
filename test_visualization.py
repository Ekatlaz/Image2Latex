from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image


def test_visualization(image_path):
    img1 = cv2.imread(image_path)
    results = best_model(img1, imgsz=640, iou=0.8, conf=0.4, verbose=True)
    img = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)

    # получение классов и имен классов
    # вообще их 3, но вдруг в будущем будет больше
    classes = results[0].boxes.cls.cpu().numpy()
    class_names = results[0].names

    # получение координат прямоугольников
    boxes = results[0].boxes.xyxy.cpu().numpy()

    # определение цветов для каждого класса
    class_colors = {
        0: (255, 0, 0),   # синий для класса формул 0
        1: (0, 0, 255),   # красный для класса текста 1
        2: (0, 255, 255)  # желтый для класса картинок 2
    }

    # создание изображения для отображения масок
    labeled_image = img.copy()

    # добавление подписей к рамкам
    for i, box in enumerate(boxes):
        x_min, y_min, x_max, y_max = map(int, box[:4])
        class_index = int(classes[i])
        color = class_colors.get(class_index, (0, 255, 0))  # использование зеленого по умолчанию на случай изменения структуры модели

        # прямоугольники и подписи
        cv2.rectangle(labeled_image, (x_min, y_min), (x_max, y_max), color, 2)
        cv2.putText(labeled_image, class_names[class_index], (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # отображение результатов
    plt.figure(figsize=(8, 8), dpi=150)
    labeled_image = cv2.cvtColor(labeled_image, cv2.COLOR_BGR2RGB)
    plt.imshow(labeled_image)
    plt.axis('off')
    plt.savefig('test(vers15.04.24).png', bbox_inches='tight', pad_inches=0)
    plt.show()

# имя модели надо заменить на актуальное
best_model = YOLO('best.pt')
test_visualization('КАРТИНКА ДЛЯ ТЕСТА.png')
