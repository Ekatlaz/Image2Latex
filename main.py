import os
import yaml
import io
from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pix2tex.cli import LatexOCR
from urllib.parse import quote
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'

## Это один раз надо запустить перед работой ##
'''# ROOT = 'datasets'
IMAGES_ROOT = 'images'
LABELS_ROOT = 'labels'
data_config = {
    # 'path': ROOT,
    'train': os.path.join(IMAGES_ROOT, 'train'),
    'val': os.path.join(IMAGES_ROOT, 'validation'),
    'nc': 3,
    'names': {0: "formula", 1: "text", 2: "picture"}
}

with open('data.yaml', 'w+') as outfile:
    yaml.dump(data_config, outfile, default_flow_style=False)'''

model_latex = LatexOCR()
best_model = YOLO('best.pt')
# metrics = best_model.val()
# print(metrics)

img1 = cv2.imread('Михалёв - Начала алгебры,часть 1-140.png')
results = best_model(img1, imgsz=640, iou=0.4, conf=0.4, verbose=True)
img = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)

# получение классов и имен классов
classes = results[0].boxes.cls.cpu().numpy()
class_names = results[0].names

# получение координат ограничивающих рамок объектов
boxes = results[0].boxes.xyxy.cpu().numpy()

# определение цветов для каждого класса
########## это место надо переделать
class_colors = {}
for i, class_index in enumerate(set(classes)):  # используем уникальные индексы классов
    class_name = class_names[class_index]
    color = tuple(np.random.randint(0, 256, 3).tolist())
    class_colors[class_index] = color

# создание изображения для отображения масок
labeled_image = img.copy()

# Создаем список индексов, который будет содержать индексы отсортированных объектов
indexes = list(range(len(boxes)))

# сортировка на основе сначала среднего y, затем среднего x
# ..// 10 - учёт погрешности, чтобы небольшая разница в y не позволяла считать блоки разными строками
indexes.sort(key=lambda j: ((boxes[j][1] + boxes[j][3]) / 2 // 10, (boxes[j][0] + boxes[j][2]) / 2))

#latex_output = ""
latex_output = "\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage[russian]{babel}\n\\usepackage{amsmath}\n\n\\begin{document}\n"
# вывод данных в консоль

for i in indexes:
    box = boxes[i]
    x_min, y_min, x_max, y_max = map(int, box[:4])
    print('x: ', (x_min + x_max)/2, 'y: ', (y_min + y_max)/2)
    cropped_image = img[y_min:y_max, x_min:x_max]
    cropped_image = Image.fromarray(cropped_image)
    if int(classes[i]) == 0:
        #latex_output += "$" + latex_escape(model_latex(cropped_image)) + "$\n"
        latex_output += "$" + model_latex(cropped_image) + "$\n"
    elif int(classes[i]) == 1:
        #latex_output += "$" + latex_escape(pytesseract.image_to_string(cropped_image,  config=config, lang='rus+eng')) + "$\n"
        latex_output += pytesseract.image_to_string(cropped_image, config=config, lang='rus+eng') + "\n"
    else:
        # Эта часть пока не опробована
        img_bytes = io.BytesIO()
        cropped_image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        i_safe = quote(str(i))
        latex_output += f"\\begin{{figure}}\n\\includegraphics{{{i_safe}.png}}\n\\end{{figure}}\n"
        with open(f"{i_safe}.png", "wb") as f:
            f.write(img_bytes)

latex_output += "\\end{document}"

with open("output.tex", "w", encoding="utf-8") as f:
    f.write(latex_output)


# добавление подписей к рамкам
'''for i, box in enumerate(boxes):
    x_min, y_min, x_max, y_max = map(int, box[:4])
    class_index = int(classes[i])
    if class_index in class_colors:  # проверка, что класс имеет соответствующий цвет
        color = class_colors[class_index]
    else:
        color = (0, 255, 0)  # используем зеленый цвет по умолчанию

    # прямоугольники и подписи
    cv2.rectangle(labeled_image, (x_min, y_min), (x_max, y_max), color, 2)
    cv2.putText(labeled_image, class_names[class_index], (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# отображение результатов
plt.figure(figsize=(8, 8), dpi=150)
labeled_image = cv2.cvtColor(labeled_image, cv2.COLOR_BGR2RGB)
plt.imshow(labeled_image)
plt.axis('off')
#plt.savefig('labeled_image_3(vers15.03.24).png', bbox_inches='tight', pad_inches=0)
plt.show()'''
