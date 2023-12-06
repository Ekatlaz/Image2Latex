from seg_img import *
from matplotlib import pyplot as plt
# import pytesseract
import keras
import tensorflow

json_file = open('../model_words_v05.12.23.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = keras.models.model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("../model_words_v05.12.23.h5")
print("Loaded model from disk")


def get_text(img):
    print("start get_text")
    for block in segment(img):
        for sentence in image2sentences(block.image):
#                 print(pytesseract.image_to_string(sentence[4], lang= 'rus'))
            for word in image2words(sentence[4]):
                letters = word2letters(word[4])
#                 plt.imshow(word[4])
                string = ""
                for letter in letters:
                    let = np.array(letter[4] / 255)
                    let = np.expand_dims(let, axis=0)
#                     print(let)
                    print(let.shape)
                    plt.imshow(letter[4] / 255, cmap='gray')
                    plt.show()
#                     print(let)
#                     print(let.shape)
                    res = loaded_model.predict(let)
#                     print( res )
                    string += chr(int(np.argmax(res)) + ord("А"))
#                     print(f'Распознанная буква: {chr(int(np.argmax(res)) + ord("А"))}')
                print(string)