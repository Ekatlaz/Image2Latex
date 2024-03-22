from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
from typing import Dict, Optional
from uuid import uuid4
import time
import threading 
import cv2 as cv
import numpy as np
import os
import pdf2image
import shutil
# from ocr import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Item(BaseModel):
	user_id: str
class texText(BaseModel):
	tex: str


@app.get("/", response_class=HTMLResponse)
async def get_site():
	html = open("app/site/index.html");
	result = html.read();
	html.close()
	return HTMLResponse(content=result)

@app.post("/uploadFile")
async def uploadPhoto(file: UploadFile):
	user_id = str(uuid4())
	foldername = "savedfiles_" + user_id;
	os.system("mkdir " + foldername)
	if file and "png" in file.content_type:
		print("file uploaded png")
		content = await file.read()
		nparr = np.fromstring(content, np.uint8)
		img = cv.imdecode(nparr, cv.IMREAD_COLOR)
		cv.imwrite(foldername + "/saved.png", img)

	elif file and ("jpg" in file.content_type or "jpeg" in file.content_type):
		print("file uploaded jpeg and saved png")
		content = await file.read()
		nparr = np.fromstring(content, np.uint8)
		img = cv.imdecode(nparr, cv.IMREAD_COLOR)
		cv.imwrite(foldername + "/saved.png", img)

	elif file and ("pdf" in file.content_type):
		print("file uploaded pdf to png")
		content = await file.read()
		img = pdf2image.pdf2image.convert_from_bytes(content)
		for i, pdf in enumerate(img):
			pdf.save(foldername + "/saved_" + str(i) + ".png", 'PNG')

	else:
		raise HTTPException(status_code=400, detail="Incorrect file")

		print(file)
	
	get_LaTex_from_image(foldername)
	zipfiles(foldername)
	response = FileResponse(path="zip_" + foldername + ".zip", filename="files.zip")
	
	return user_id

@app.get("/tex/{user_id}/")
async def get_tex(user_id: str):
	print("asdfasdf")
	response = "";
	with open("savedfiles_" + user_id + "/result.tex") as file:
		response = file.read();
	return response

@app.get("/pdf/{user_id}/")
async def get_pdf(user_id: str):
	response = FileResponse(path="savedfiles_" + user_id + "/result.pdf", filename="result.pdf")
	return response

@app.get("/zip/{user_id}")
async def get_zip(user_id: str):
	response = FileResponse(path="zip_savedfiles_" + user_id + ".zip", filename="files.zip")
	return response

@app.post("/renderTex/{user_id}")
async def get_renderTex(user_id: str, texText: texText):
	print(texText.tex)
	with open("savedfiles_" + user_id + "/result.tex", "w") as file:
		file.write(texText.tex)
	os.system("rm -rf " + "savedfiles_" + user_id + "/result.pdf ")
	os.system("pdflatex -output-directory=savedfiles_" + user_id + " " + "savedfiles_" + user_id + "/result.tex")

	if os.path.exists("savedfiles_" + user_id + "/result.pdf"):
		response = FileResponse(path="savedfiles_" + user_id + "/result.pdf", filename="result.pdf")
		os.system("rm -rf " + "savedfiles_" + user_id + "/result.log " + " savedfiles_" + user_id  + "/result.aux")
		return response
	else:
		raise HTTPException(status_code=400, detail="Incorrect file")
	

def zipfiles(foldername):
	shutil.make_archive('zip_' + foldername, format='zip', root_dir=foldername)
	os.system("ls")

def get_LaTex_from_image(foldername: str):
	for filename in os.scandir(foldername):
		if filename.is_file():
			print(filename)
			print(filename.path)
			print("-------")
	os.system("touch " + foldername + "/result.tex")
	latex = """\\documentclass{article}
\\usepackage{graphicx} % Required for inserting images

\\title{example}
\\author{Nick Seleznev}
\\date{March 2024}

\\begin{document}

\\maketitle

\\section{Introduction}
\\begin{figure}
    \\centering
    \\includegraphics[width=0.5\\linewidth]{saved_0.png}
    \\caption{Enter Caption}
    \\label{fig:enter-label}
\\end{figure}

\\end{document}
"""
	with open(foldername + "/result.tex", "w") as tex:
		tex.write(latex)
	os.system("pdflatex -output-directory=" + foldername + " " + foldername + "/result.tex")
	os.system("rm -rf " + foldername + "/result.log " + foldername + "/result.aux")

def check_for_unused_files():
	for filename in os.scandir("/"):
		if filename.is_file() and ".zip" in filename.path or not filename.is_file() and "savedfiles_" in filename.path:
			os.system("echo \"file =" + filename.path + "\"")
			os.system("rm -rf " + filename.path)


class RepeatedTimer(object):
	def __init__(self, interval, function, *args, **kwargs):
		self._timer = None
		self.interval = interval
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self.is_running = False
		self.next_call = time.time()
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		os.system("echo \"running func...\"")
		self.function(*self.args, **self.kwargs)

	def start(self):
		if not self.is_running:
			os.system("echo \"starting\"")
			self.next_call += self.interval
			self._timer = threading.Timer(self.next_call - time.time(), self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		self._timer.cancel()
		self.is_running = False


timer = RepeatedTimer(30 * 15, check_for_unused_files)
timer.start()