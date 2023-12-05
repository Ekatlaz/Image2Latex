from seg_img import *
from matplotlib import pyplot as plt
import pytesseract
# import keras
# import tensorflow

# json_file = open('../model_words.json', 'r')
# loaded_model_json = json_file.read()
# json_file.close()
# loaded_model = keras.models.model_from_json(loaded_model_json)
# # load weights into new model
# loaded_model.load_weights("../model_words.h5")
# print("Loaded model from disk")


def get_text(img):
    print("start get_text")
    for block in segment(img):
        for sentence in image2sentences(block.image):
                print(pytesseract.image_to_string(sentence[4], lang= 'rus'))
#             for word in image2words(sentence[4]):
#                 letters = word2letters(words[4])
#                 string = ""
#                 for letter in letters:
#                     let = np.expand_dims(letter[4], axis=0)
# #                     plt.imshow(letter[4], cmap='gray')
# #                     plt.show()
#                     res = loaded_model.predict(let)
#                     print( res )
#                     string += chr(int(np.argmax(res)) + ord("А"))
#                     print(f'Распознанная буква: {chr(int(np.argmax(res)) + ord("А"))}')
#                 print(string)