import cv2
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

class Block():
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

def segment(img):
    MIN_TEXT_SIZE = 10
    HORIZONTAL_POOLING = 25
    img_width = img.shape[1]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
    
    blur = cv2.GaussianBlur(img_bw, (7,7), 0) 
    
#     plt.imshow(blur, cmap='gray')
#     plt.show()

    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    m1 = cv2.morphologyEx(blur, cv2.MORPH_GRADIENT, k1)
    
#     plt.imshow(m1, cmap='gray')
#     plt.show()
    
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (HORIZONTAL_POOLING, 5))
    m2 = cv2.morphologyEx(m1, cv2.MORPH_CLOSE, k2)

#     plt.imshow(m2, cmap='gray')
#     plt.show()   

    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    m3 = cv2.dilate(m2, k3, iterations=3)
    
#     plt.imshow(m3, cmap='gray')
#     plt.show()

    contours, hierarchy = cv2.findContours(m3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    
    output = img.copy()
    blocks = []
    for idx, c in enumerate(contours):
        if hierarchy[0][idx][3] == -1:
            bx,by,bw,bh = cv2.boundingRect(c)
            cv2.rectangle(output, (bx, by), (bx + bw, by + bh), (255, 0, 0), 1)

            crop = img[by:by+bh, 0:img_width]

            blocks.append(Block(0, by, img_width, bh, crop))
        
#     plt.imshow(output)
#     plt.show()
    
    return sorted(blocks, key=lambda x: x.y)

def image2sentences(img):
    print("image2sentences")
    output = img.copy()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ret, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
#     Image.fromarray(thresh).save('0.png')
#     plt.imshow(thresh, cmap='gray')
#     plt.show()
    
    blur = cv2.GaussianBlur(thresh, (1,7), 0) 
    
    kernel = np.ones((3, 30), np.uint8)
    img_erode = cv2.erode(blur, kernel, 2)
#     Image.fromarray(img_erode).save('1.png')
#     plt.imshow(img_erode, cmap='gray')
#     plt.show()
    
    ret, thresh = cv2.threshold(img_erode, 200, 255, cv2.THRESH_BINARY)
#     Image.fromarray(thresh).save('2.png')
#     plt.imshow(thresh, cmap='gray')
#     plt.show()
    
    
    blur = cv2.GaussianBlur(thresh, (1,7), 0) 
#     Image.fromarray(blur).save('3.png')
#     plt.imshow(blur, cmap='gray')
#     plt.show()
    
    
    img_erode = cv2.erode(blur, kernel, 2)
#     Image.fromarray(img_erode).save('4.png')
#     plt.imshow(img_erode, cmap='gray')
#     plt.show()
    
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    sentences = []
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        if hierarchy[0][idx][3] == 0:
            cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 0), 1)
            sentences.append((x, y, w, h, img[y:y+h, x:x+w]))
    sentences.sort(key=lambda x: x[1])
#     Image.fromarray(output).save('5.png')
#     plt.imshow(output)
#     plt.show()
    return sentences

def image2words(img):
    print("image2words")
    img = cv2.copyMakeBorder(img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    output = img.copy()
    
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     Image.fromarray(gray).save('0.png')
#     plt.imshow(gray, cmap='gray')
#     plt.show()
    
    ret, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY) 
#     Image.fromarray(thresh).save('1.png')
#     plt.imshow(thresh, cmap='gray')
#     plt.show()
    
    kernel = np.ones((3, 10), np.uint8)
    
    img_erode = cv2.erode(thresh, kernel, 1)
#     Image.fromarray(img_erode).save('2.png')
#     plt.imshow(img_erode, cmap='gray')
#     plt.show()
    
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    words = []
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        
        if hierarchy[0][idx][3] == 0:
            cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 0), 1)
            words.append((x, y, w, h, img[y:y+h, x:x+w]))
    words.sort(key=lambda x: x[0])
#     Image.fromarray(output).save('3.png')
#     plt.imshow(output)
#     plt.show()
    return words

def word2letters(word):
    print("word2letters")
    word = cv2.copyMakeBorder(word, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    output = word.copy()
    
    gray = cv2.cvtColor(word, cv2.COLOR_BGR2GRAY)
#     plt.imshow(gray, cmap='gray')
#     plt.show()
    
    blur = cv2.GaussianBlur(gray, (1,7), 0)
#     plt.imshow(blur, cmap='gray')
#     plt.show()
    
    ret, thresh = cv2.threshold(blur, 220, 255, cv2.THRESH_BINARY)
#     plt.imshow(thresh, cmap='gray')
#     plt.show()
    
    kernel = np.ones((4, 1), np.uint8)
    img_erode = cv2.erode(thresh, kernel, 1)
#     plt.imshow(img_erode, cmap='gray')
#     plt.show()
    
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    letters = []
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
#         print(hierarchy[0][idx])
        if hierarchy[0][idx][3] == 0:
            cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0 , 0), 1)
            letter_crop = gray[y:y+h, x:x+w]
            _, letter_crop = cv2.threshold(letter_crop, 200, 255, cv2.THRESH_BINARY)
            letter_crop = cv2.bitwise_not(letter_crop)

            resized = cv2.resize(letter_crop, (28, 28), interpolation=cv2.INTER_AREA)
            letters.append((x, y, w, h, resized))
            
    letters.sort(key=lambda x: x[0])
    plt.imshow(output)
    ax = plt.gca()
    ax.get_xaxis ().set_visible ( False )
    ax.get_yaxis ().set_visible ( False )
    plt.show()
    return letters