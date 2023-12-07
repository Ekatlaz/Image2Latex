import argparse
import cv2
from get_text import *

    
def main():
    json_file = open('../model_words_v05.12.23.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = keras.models.model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("../model_words_v05.12.23.h5")

    img = cv2.imread('2.png', cv2.IMREAD_GRAYSCALE)
    img = img / 255
    img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
    plt.imshow(img)
    plt.show()
    img = np.array(img)
    img = np.expand_dims(img, axis=0)
    print(img.shape)
    res = loaded_model.predict(img)
    print(chr(int(np.argmax(res)) + ord("А")))
#     print("begin")
#     parser = argparse.ArgumentParser(description="Generate a .tex file from a .pdf file.")
#     parser.add_argument('--filepath', type=str, help="")
#     parser.add_argument('--folderpath', type=str, help="")
    
#     args = parser.parse_args()

#     filepath = args.filepath
#     folderpath = args.folderpath
    
#     print(filepath)
#     img = cv2.imread(filepath)
#     get_text(img)
    

if __name__ == "__main__":
    main()
    
    
    