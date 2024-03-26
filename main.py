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
import fitz

# import magic
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'


# Это один раз надо запустить перед работой
def create_yaml():
    data_config = {
        'train': os.path.join('images', 'train'),
        'val': os.path.join('images', 'validation'),
        'nc': 3,
        'names': {0: "formula", 1: "text", 2: "picture"}
    }

    with open('data.yaml', 'w+') as outfile:
        yaml.dump(data_config, outfile, default_flow_style=False)


def convert_pdf_to_png(pdf_path):
    pdf_document = fitz.open(pdf_path)
    # os.makedirs(output_folder, exist_ok=True)
    page_count = pdf_document.page_count

    for page_number in range(page_count):
        page = pdf_document.load_page(page_number)
        image = page.get_pixmap()
        image_path = os.path.join(f"page_{page_number + 1}.png")
        image.save(image_path, "PNG")
    pdf_document.close()
    return page_count


def start(file_path):
    if file_path.lower().endswith('.pdf'):
        page_count = convert_pdf_to_png(file_path)
        # print(page_count)

        with open("output.tex", "w", encoding="utf-8") as f:

            f.write("\\documentclass[12pt]{article}\n"
                    "\\usepackage[utf8]{inputenc}\n"
                    "\\usepackage[russian]{babel}\n"
                    "\\usepackage[11]{calculus}\n"
                    "\\usepackage{amsmath}\n"
                    "\\usepackage{dsfont}\n"
                    "\\usepackage{graphicx}\n\n"
                    "\\begin{document}\n")

        for i in range(page_count):
            create_tex(f"page_{i + 1}.png", i)

        with open("output.tex", "a", encoding="utf-8") as f:
            f.write("\\end{document}")


    elif file_path.lower().endswith('.png') or file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
        with open("output.tex", "w", encoding="utf-8") as f:

            f.write("\\documentclass[12pt]{article}\n"
                    "\\usepackage[utf8]{inputenc}\n"
                    "\\usepackage[russian]{babel}\n"
                    "\\usepackage[11]{calculus}\n"
                    "\\usepackage{amsmath}\n"
                    "\\usepackage{dsfont}\n"
                    "\\usepackage{graphicx}\n\n"
                    "\\begin{document}\n")
        create_tex(file_path, 0)
        with open("output.tex", "a", encoding="utf-8") as f:
            f.write("\\end{document}")


def create_tex(img_path, numper_of_page):
    img1 = cv2.imread(img_path)
    height, width, _ = img1.shape
    results = best_model(img1, imgsz=640, iou=0.4, conf=0.4, verbose=True)
    img = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)

    # получение классов и имен классов
    classes = results[0].boxes.cls.cpu().numpy()
    class_names = results[0].names

    # получение координат ограничивающих рамок объектов
    boxes = results[0].boxes.xyxy.cpu().numpy()

    # Создаем список индексов, который будет содержать индексы отсортированных объектов
    indexes = list(range(len(boxes)))

    # сортировка на основе сначала среднего y, затем среднего x
    # ..// 10 - учёт погрешности, чтобы небольшая разница в y не позволяла считать блоки разными строками
    indexes.sort(key=lambda j: ((boxes[j][1] + boxes[j][3]) / 2 // 10, (boxes[j][0] + boxes[j][2]) / 2))

    len_indexes = len(indexes)

    caption = False
    prev_text = ''  # для добавления пропащих точек и пробелов

    with open("output.tex", "a", encoding="utf-8") as f:
        # переход на новую страницу
        if numper_of_page != 0:
            f.write('\n\\newpage\n')

        for i in range(len_indexes):
            # если мы уже брали сегмент как подпись, то скип
            if caption:
                caption = False
                continue
            box = boxes[indexes[i]]
            x_min, y_min, x_max, y_max = map(int, box[:4])
            # print('x: ', (x_min + x_max) / 2, 'y: ', (y_min + y_max) / 2)
            cropped_image = img[y_min:y_max, x_min:x_max]
            cropped_image = Image.fromarray(cropped_image)

            new_string = False

            # проверка на перенос строки
            if i != 0:
                box_prev = boxes[indexes[i - 1]]
                x_min_prev, y_min_prev, x_max_prev, y_max_prev = map(int, box_prev[:4])
                # print('y_prev: ', (y_min_prev + y_max_prev) / 2)
                if abs((y_min + y_max) / 2 - (y_min_prev + y_max_prev) / 2) >= 10:
                    new_string = True

            if int(classes[indexes[i]]) == 0:
                formula = '$' + model_latex(cropped_image) + '$'

                if i != 0 and new_string is False:
                    if prev_text[-1] != ' ':
                        f.write(' ')

                f.write(formula)
                f.write(' ')
                prev_text = formula
            elif int(classes[indexes[i]]) == 1:
                text = pytesseract.image_to_string(cropped_image, config=config, lang='rus+eng')
                if text == '':
                    continue
                # исправление странного глюка pytesseract'a. Удаление _ вначале
                elif text[0] == '_':
                    text = text[1:]
                # пустые символы мешают понять новый абзац или нет
                while text[0] == ' ' or text[0] == '`' or text[0] == '\"' or text[0] == "\'" or text[0] == '‘':
                    text = text[1:]
                # удаление переносов
                if text.endswith('-\n'): # 'это быстрее, но не обрабатывает внутри больших абзацев
                    text = text[:-2]
                '''for j in range(1, len(text)):  # а это долго, но красивее
                    if text[j - 1] == '-' and text[j] == '\n':
                        text = text[:(j - 1)] + text ..... дописать, если надо'''
                # считаем, что в большинстве случаев если текст начинается с большой буквы, то это новый абзац
                # потому что если текст идёт после формулы, он начнётся с , или .
                if text[0].isupper() and new_string:
                    f.write('\n\n')
                if new_string and i != 0 and y_max - y_min_prev >= 50: # пример: колонтитулы и текст далее не сливаются в один абзац
                    if text[0].islower():
                        f.write('\n\\noindent\n')
                    else:
                        f.write('\n\n')
                elif new_string and (text[0].isdigit() and text[1] == ')'
                                     or text[0].isdigit() and text[1].isdigit() and text[2] == ')'
                                     or text[0].isdigit() and text[1].isdigit() and text[2].isdigit() and text[3] == ')'):
                    f.write('\n\n')
                elif new_string and (text[0].islower() and text[1] == ')'
                                     or text[0].islower() and text[1].islower() and text[2] == ')'
                                     or text[0].islower() and text[1].islower() and text[2].islower() and text[3] == ')'):
                    f.write('\n\n')

                ######## какая-то муть. надо переписать. неверно срабатывают условия
                '''if i != 0 and new_string is False and text[0].isupper() and prev_text[-1] != ' ':
                    f.write(' ')
                elif i != 0 and (text[0] == ' ' or text[0] == ',' or text[0] == '.'):
                    pass
                elif i != 0:
                    f.write(' ')'''
                '''if i != 0 and new_string is False and (text[0] != ' ' or text[0] != ',' or text[0] != '.' or text[0].isupper()):
                    if text[0].isupper():
                        f.write('. ')
                    if prev_text[-1] != ' ' and not (text[0] == ',' or text[0] == '.' or text[0] == ' '):
                        f.write(' ')'''

                # центрируем или нет
                if abs(width/2 - (y_min + y_max)/2) <= 20 and text[0].isupper() and (new_string or i == 0) and (text[-1] == '.' or text[-1] == '\n') and len(text) < 50:
                    f.write('\\begin{center}\n')
                    f.write(text)
                    f.write('\\end{center}')
                else: # тут может быть i = 1, если впереди поймался колонтитул. надо это обработать????
                    if text[0].islower() and (i == 0 or text[-2] == '\\' and text[-1] == 'n'):
                        f.write('\\noindent\n')
                    f.write(text)
                prev_text = text
                y_min_prev = y_min
            else:
                img_bytes = io.BytesIO()
                cropped_image.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()  # байтовое представление png
                i_safe = quote(str(i))

                # если одиночная картинка с подписью
                if i + 1 != len_indexes - 1 and i + 2 != len_indexes - 1 and int(classes[indexes[i + 1]]) == 1:
                    box_next = boxes[indexes[i + 1]]
                    x_min_next, y_min_next, x_max_next, y_max_next = map(int, box_next[:4])
                    cropped_image = img[y_min_next:y_max_next, x_min_next:x_max_next]
                    cropped_image = Image.fromarray(cropped_image)

                    f.write(f"\n\n\\begin{{wrapfigure}}\n"
                            f"\\begin{{center}}\n"
                            f"\\includegraphics[width=0.5\\textwidth]{{{i_safe}.png}}\n"
                            f"\\end{{center}}\n"
                            f"\\begin{{center}}\n"
                            f"\\caption{{{pytesseract.image_to_string(cropped_image, config=config, lang='rus+eng')}}}\n"
                            f"\\end{{center}}\n"
                            f"\\end{{wrapfigure}}\n\n")
                    caption = True
                else:
                    f.write(f"\n\n\\begin{{wrapfigure}}\n"
                            f"\\includegraphics[width=0.5\\textwidth]{{{i_safe}.png}}\n"
                            f"\\end{{wrapfigure}}\n\n")


model_latex = LatexOCR()
best_model = YOLO('best.pt')
# это посмотреть метрики модели
# metrics = best_model.val()
# print(metrics)

start('png2pdf.pdf')
# test_visualization('page_2.png')
