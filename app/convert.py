import argparse
import cv2
from get_text import *
    
def main():
    print("begin")
    parser = argparse.ArgumentParser(description="Generate a .tex file from a .pdf file.")
    parser.add_argument('--filepath', type=str, help="")
    parser.add_argument('--folderpath', type=str, help="")
    
    args = parser.parse_args()

    filepath = args.filepath
    folderpath = args.folderpath
    
    print(filepath)
    img = cv2.imread(filepath)
    get_text(img)
    

if __name__ == "__main__":
    main()
    
    
    