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
import fitz
import requests
import base64

config = r'--oem 3 --psm 6'
def auto_rotate(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # обнаруживаем края на изображении и ищем прямые линии
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is not None:
        angles = []
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi - 90)
            angles.append(angle)

        # вычисление среднего угла
        median_angle = np.median([angle for angle in angles if angle != 0])
        # поворот
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        m = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated
    else:
        return img


def query(q):
    API_URL = "https://api-inference.huggingface.co/models/Norm/nougat-latex-base"
    headers = {"Authorization": f"Bearer {'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'}"}
    response = requests.request("POST", API_URL, headers=headers, json=q)
    return response.json()


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


def convert_pdf_to_png(pdf_path, foldername):
    pdf_document = fitz.open(pdf_path)
    # os.makedirs(output_folder, exist_ok=True)
    page_count = pdf_document.page_count

    for page_number in range(page_count):
        page = pdf_document.load_page(page_number)
        image = page.get_pixmap()
        image_path = os.path.join(f"page_{page_number + 1}.png")
        image.save(foldername + "/" + image_path, "PNG")
    pdf_document.close()
    return page_count


def start(file_path, foldername):
    if file_path.lower().endswith('.pdf'):
        page_count = convert_pdf_to_png(file_path, foldername)
        # print(page_count)

        with open(foldername + "/output.tex", "w", encoding="utf-8") as f:

            f.write("\\documentclass[12pt]{article}\n"
                    "\\usepackage[utf8]{inputenc}\n"
                    "\\usepackage[russian]{babel}\n"
                    "\\usepackage[11]{calculus}\n"
                    "\\usepackage{amsmath}\n"
                    "\\usepackage{dsfont}\n"
                    "\\usepackage{graphicx}\n\n"
                    "\\begin{document}\n")

        for i in range(page_count):
            file_page_path = f"page_{i + 1}.png"

            print(f"rotate {file_page_path}")
            rotated_image = auto_rotate(f"{foldername}/{file_page_path}")
            cv2.imwrite(f"{file_page_path}", rotated_image)

            print(f"creating from {file_page_path}")
            create_tex(f"{foldername}/{file_page_path}", i, foldername)

        with open(foldername + "/output.tex", "a", encoding="utf-8") as f:
            f.write("\\end{document}")


    elif file_path.lower().endswith('.png') or file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
        with open(foldername + "/output.tex", "w", encoding="utf-8") as f:

            f.write("\\documentclass[12pt]{article}\n"
                    "\\usepackage[utf8]{inputenc}\n"
                    "\\usepackage[russian]{babel}\n"
                    "\\usepackage[11]{calculus}\n"
                    "\\usepackage{amsmath}\n"
                    "\\usepackage{dsfont}\n"
                    "\\usepackage{graphicx}\n\n"
                    "\\begin{document}\n")
        print(f"auto_rotate ({file_path})")
        rotated_image = auto_rotate(f"{file_path}")
        cv2.imwrite(f"{file_path}", rotated_image)
        create_tex(file_path, 0, foldername)
        with open(foldername + "/output.tex", "a", encoding="utf-8") as f:
            f.write("\\end{document}")


def create_tex(img_path, numper_of_page, foldername):
    img1 = cv2.imread(img_path)
    height, width, _ = img1.shape
    results = best_model(img1, imgsz=640, iou=0.4, conf=0.4, verbose=True)
    img = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)

    # получение классов и имен классов
    classes = results[0].boxes.cls.cpu().numpy()
    # class_names = results[0].names

    # получение координат ограничивающих рамок объектов
    boxes = results[0].boxes.xyxy.cpu().numpy()

    # Создаем список индексов, который будет содержать индексы отсортированных объектов
    indexes = list(range(len(boxes)))

    diff = 3000
    for i in range(len(indexes)):
        if classes[i] != 2:
            diff = min(diff, boxes[i][3] - boxes[i][1])

    # сортировка на основе сначала среднего y, затем среднего x
    # ..// 10 - учёт погрешности, чтобы небольшая разница в y не позволяла считать блоки разными строками
    indexes.sort(key=lambda u: ((boxes[u][1] + boxes[u][3]) / 2 // diff, (boxes[u][0] + boxes[u][2]) / 2))
    print(indexes)

    len_indexes = len(indexes)

    caption = False
    prev_text = ''  # для добавления пропащих точек и пробелов

    with open(foldername + "/output.tex", "a", encoding="utf-8") as f:
        # переход на новую страницу
        if numper_of_page != 0:
            f.write('\n\\newpage\n')

        hight_of_line = 1000
        left_x_line = 1000

        
        # удаление дубляжа сегментов, внутренних повторяющихся сегментов
        for i in range(len_indexes):
            box = boxes[indexes[i]]
            x_min_i, y_min_i, x_max_i, y_max_i = map(int, box)
            hight_of_line = min(hight_of_line, y_max_i - y_min_i)
            left_x_line = min(left_x_line, x_min_i)

            '''cropped_image_i = img[y_min_i:y_max_i, x_min_i:x_max_i]
            cropped_image_i = Image.fromarray(cropped_image_i)
            cropped_image_i.save("cropped_image_i.png")'''
            for j in range(i + 1, len_indexes):
                box = boxes[indexes[j]]
                x_min_j, y_min_j, x_max_j, y_max_j = map(int, box)

                '''cropped_image_j = img[y_min_j:y_max_j, x_min_j:x_max_j]
                cropped_image_j = Image.fromarray(cropped_image_j)
                cropped_image_j.save("cropped_image_j.png")'''

                if x_min_j >= x_min_i and y_min_j >= y_min_i and x_max_j <= x_max_i and y_max_j <= y_max_i:
                    classes[indexes[j]] = 4  # ничего не делаем с дубляжом, пропускаем далее
                elif x_min_j <= x_min_i and y_min_j <= y_min_i and x_max_j >= x_max_i and y_max_j >= y_max_i:
                    classes[indexes[i]] = 4  # ничего не делаем с дубляжом, пропускаем далее
                elif x_max_j - x_min_j >= x_max_i - x_min_i and y_max_j - y_min_j <= y_max_i - y_min_i \
                        and abs(y_max_j - y_min_j - (y_max_i - y_min_i)) <= hight_of_line / 4 \
                        and y_min_i <= ((y_max_j + y_min_j) / 2) <= y_max_i \
                        and x_min_i <= ((x_max_j + x_min_j) / 2) <= x_max_i:
                    classes[indexes[j]] = 4
                elif x_max_j - x_min_j <= x_max_i - x_min_i and y_max_j - y_min_j >= y_max_i - y_min_i \
                        and y_min_j <= ((y_max_i + y_min_i) / 2) <= y_max_j \
                        and x_min_j <= ((x_max_i + x_min_i) / 2) <= x_max_j:
                    classes[indexes[i]] = 4

        # тест
        '''for i in range(len_indexes):
            if classes[indexes[i]] != 4:
                box = boxes[indexes[i]]
                x_min_i, y_min_i, x_max_i, y_max_i = map(int, box)
                cropped_image_i = img[y_min_i:y_max_i, x_min_i:x_max_i]
                cropped_image_i = Image.fromarray(cropped_image_i)
                cropped_image_i.save(f"crop_{i}.png", format='PNG')
                print(i, ': ', x_min_i, y_min_i, x_max_i, y_max_i)'''

        for i in range(len_indexes):
            # если мы уже брали сегмент как подпись, то скип
            if caption:
                caption = False
                continue
            box = boxes[indexes[i]]
            x_min, y_min, x_max, y_max = map(int, box)
            # print('x: ', (x_min + x_max) / 2, 'y: ', (y_min + y_max) / 2)
            cropped_image = img[y_min:y_max, x_min:x_max]
            cropped_image = Image.fromarray(cropped_image)

            new_string = False

            # проверка на перенос строки
            if i != 0:
                box_prev = boxes[indexes[i - 1]]
                x_min_prev, y_min_prev, x_max_prev, y_max_prev = map(int, box_prev)
                # print('y_prev: ', (y_min_prev + y_max_prev) / 2)
                #if abs((y_min + y_max) / 2 - (y_min_prev + y_max_prev) / 2) >= 10:
                if abs((y_min + y_max) / 2 - (y_min_prev + y_max_prev) / 2) >= hight_of_line:
                    new_string = True

            if int(classes[indexes[i]]) == 0:
                # if new_string and prev_text.endswith('$'):
                if new_string:
                    f.write('\n\n')

                flag_error = False
                formula_nuga = ''
                formula_latex = ''
                try:
                    with io.BytesIO() as output:
                        cropped_image.save(output, format="PNG")
                        image_bytes = output.getvalue()

                    # это для использования с нугой
                    image_b64 = base64.b64encode(image_bytes)
                    formula = query({"inputs": image_b64.decode("utf-8"), "parameters": {"max_new_tokens": 800}})
                    # print(formula)
                    # print(type(formula))
                    # print(type(formula[0]))
                    # print(type(formula[0]['generated_text']))

                    formula_nuga = '$' + formula[0]['generated_text'] + '$'
                except Exception as e:
                    flag_error = True
                    formula_latex = '$' + model_latex(cropped_image) + '$'
                else:
                    formula_latex = '$' + model_latex(cropped_image) + '$'

                if flag_error:
                    formula = formula_latex
                elif 0 < len(formula_latex) < len(formula_nuga):
                    formula = formula_latex
                else:
                    formula = formula_nuga

                # это для использования с latex-ocr
                """formula = '$' + model_latex(cropped_image) + '$'"""

                if i != 0 and new_string is False:
                    if prev_text[-1] != ' ':
                        f.write(' ')

                # блок использовался для latex-ocr
                # f.write(formula)

                # formula = '$' + formula[0]['generated_text'] + '$'
                f.write(formula)
                f.write(' ')
                prev_text = formula
            elif int(classes[indexes[i]]) == 1:
                text = pytesseract.image_to_string(cropped_image, config=config, lang='rus+eng')
                if text == '':
                    continue
                # пустые символы мешают понять новый абзац или нет
                while text[0] == ' ' or text[0] == '`' or text[0] == '\"' or text[0] == "\'" or text[0] == '‘' or text[0] == '_':
                    text = text[1:]
                # удаление переносовcls
                prev_k = 0

                flag_delete_perenosy = 0
                text1 = text
                text = ''
                for k in range(len(text1) - 2):
                    if text1[k:k + 2] == '-\n': # or text1[k:k + 1] == '\n'
                        text += text1[prev_k:k]
                        prev_k = k + 2
                        flag_delete_perenosy = 1
                    if flag_delete_perenosy == 1:
                        text += text1[prev_k:len(text1)]
                        flag_delete_perenosy = 0
                    else:
                        text = text1
                    if text.endswith('-\n'):
                        text = text[:-2]
                # считаем, что в большинстве случаев если текст начинается с большой буквы, то это новый абзац
                # потому что если текст идёт после формулы, он начнётся с , или .
                '''if text[0].isupper() and new_string:
                    f.write('\n\n')'''
                if new_string and i != 0 and y_max - y_min_prev >= 50: # пример: колонтитулы и текст далее не сливаются в один абзац
                    if text[0].islower():
                        f.write('\n\n\\noindent\n')
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
                elif new_string and left_x_line -5 >= x_min >= left_x_line + 5:
                    f.write('\n\n\\noident\n')
                elif new_string and text[0].isupper():
                    f.write('\n\n')
                elif new_string and text[0].islower():
                    f.write('\n\n\\noident\n')

                

                # центрируем или нет
                if abs(width/2 - (y_min + y_max)/2) <= 20 and text[0].isupper() and (new_string or i == 0) and (text[-1] == '.' or text[-1] == '\n') and len(text) < 50:
                    f.write('\\begin{center}\n')
                    f.write(text)
                    f.write('\\end{center}')
                else: # тут может быть i = 1, если впереди поймался колонтитул. надо это обработать????
                    if text[0].islower() and i == 0 and text[-1] == '\n':
                        f.write('\n\n\\noindent\n')
                    f.write(text)
                prev_text = text
                y_min_prev = y_min
            elif int(classes[indexes[i]] == 2):
                i_safe = str(i)
                str_number_of_page = str(numper_of_page)
                cropped_image.save(foldername + "/" + 'page' + str_number_of_page + '_' + i_safe + '.png', format='PNG')
                
                if i == len_indexes - 1:
                    f.write(f"\n\n\\begin{{wrapfigure}}\n"
                            f"\\includegraphics[width=0.5\\textwidth]{{page{str_number_of_page}_{i_safe}.png}}\n"
                            f"\\end{{wrapfigure}}\n\n")
                # если одиночная картинка с подписью
                elif i + 1 != len_indexes - 1 and i + 2 != len_indexes - 1 and int(classes[indexes[i + 1]]) == 1:
                    box_next = boxes[indexes[i + 1]]
                    x_min_next, y_min_next, x_max_next, y_max_next = map(int, box_next[:4])
                    cropped_image = img[y_min_next:y_max_next, x_min_next:x_max_next]
                    cropped_image = Image.fromarray(cropped_image)

                    f.write(f"\n\n\\begin{{wrapfigure}}\n"
                            f"\\begin{{center}}\n"
                            f"\\includegraphics[width=0.5\\textwidth]{{page{str_number_of_page}_{i_safe}.png}}\n"
                            f"\\end{{center}}\n"
                            f"\\begin{{center}}\n"
                            f"\\caption{{{pytesseract.image_to_string(cropped_image, config=config, lang='rus+eng')}}}\n"
                            f"\\end{{center}}\n"
                            f"\\end{{wrapfigure}}\n\n")
                    caption = True
                else:
                    f.write(f"\n\n\\begin{{wrapfigure}}\n"
                            f"\\includegraphics[width=0.5\\textwidth]{{page{str_number_of_page}_{i_safe}.png}}\n"
                            f"\\end{{wrapfigure}}\n\n")

model_latex = LatexOCR()
best_model = YOLO('best15.04t.pt')