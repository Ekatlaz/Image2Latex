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
from main import *
TIME_TO_DEL = 60 * 60

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

users_ids: [str, type(time.time())] = {}

@app.get("/", response_class=HTMLResponse)
async def get_site():
	html = open("app/site/index.html");
	result = html.read();
	html.close()
	return HTMLResponse(content=result)

@app.post("/uploadFile")
async def uploadPhoto(file: UploadFile):
	print("recieve request")
	user_id = str(uuid4())
	users_ids[user_id] = time.time()
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
		print("file uploaded pdf")
		with open(foldername + "/saved.pdf", "wb") as f:
			f.write(file.file.read())

	else:
		raise HTTPException(status_code=400, detail="Incorrect file")
	
	get_LaTex_from_image(foldername)
	
	
	return user_id

@app.get("/tex/{user_id}/")
async def get_tex(user_id: str):
	response = "";
	# if (time.time() - users_ids[user_id] > TIME_TO_DEL):
	# 	raise HTTPException(status_code=400, detail="Incorrect file")
	users_ids[user_id] = time.time()
	with open("savedfiles_" + user_id + "/output.tex") as file:
		response = file.read();
	return response

@app.get("/pdf/{user_id}/")
async def get_pdf(user_id: str):
	if (user_id in list(users_ids.keys()) and time.time() - users_ids[user_id] > TIME_TO_DEL) or time.time() - os.path.getmtime("/home/nikitin/server/savedfiles_" + user_id + "/output.pdf") > TIME_TO_DEL:
		raise HTTPException(status_code=400, detail="Incorrect file")
	users_ids[user_id] = time.time()
	response = FileResponse(path="savedfiles_" + user_id + "/output.pdf", filename="output.pdf")
	return response

@app.get("/zip/{user_id}")
async def get_zip(user_id: str):
	print(users_ids)
	if (time.time() - users_ids[user_id] > TIME_TO_DEL):
		raise HTTPException(status_code=400, detail="Incorrect file")
	users_ids[user_id] = time.time()
	zipfiles("savedfiles_" + user_id)
	response = FileResponse(path="zip_savedfiles_" + user_id + ".zip", filename="files.zip")
	return response

@app.post("/renderTex/{user_id}")
async def get_renderTex(user_id: str, texText: texText):
	if (user_id in list(users_ids.keys()) and time.time() - users_ids[user_id] > TIME_TO_DEL) or time.time() - os.path.getmtime("home/nikitin/server/savedfiles_" + user_id + "/output.pdf") > TIME_TO_DEL:
		raise HTTPException(status_code=400, detail="Incorrect file")
	users_ids[user_id] = time.time()
	with open("savedfiles_" + user_id + "/output.tex", "w") as file:
		file.write(texText.tex)
	os.system("rm -rf " + "savedfiles_" + user_id + "/output.pdf " + " zip_savedfiles_" + user_id + ".zip")
	os.system("pdflatex -interaction=nonstopmode -output-directory=savedfiles_" + user_id + " " + "savedfiles_" + user_id + "/output.tex")

	if os.path.exists("savedfiles_" + user_id + "/output.pdf"):
		response = FileResponse(path="savedfiles_" + user_id + "/output.pdf", filename="output.pdf")
		os.system("rm -rf " + "savedfiles_" + user_id + "/output.log " + " savedfiles_" + user_id  + "/output.aux")
		return response
	else:
		raise HTTPException(status_code=400, detail="Incorrect file")
	

def zipfiles(foldername):
	shutil.make_archive('zip_' + foldername, format='zip', root_dir=foldername)
	os.system("ls")

def get_LaTex_from_image(foldername: str):
	for filename in os.scandir(foldername):
		if filename.is_file() and ".png" in filename.path or ".pdf" in filename.path:
			print(filename)
			print(filename.path)
			start(filename.path, foldername)
			print("-------")
	os.system("pdflatex -interaction=nonstopmode -output-directory=" + foldername + " " + foldername + "/output.tex")
	os.system("rm -rf " + foldername + "/output.log " + foldername + "/output.aux")

def check_for_unused_files():
	print(users_ids)
	for filename in os.scandir("/home/nikitin/server"):
		if filename.is_file() and ".zip" in filename.path or not filename.is_file() and "savedfiles_" in filename.path:
			name = filename.path
			name = name.replace("zip_savedfiles_", "")
			name = name.replace(".zip", "")
			name = name.replace("savedfiles_", "")
			name = name.replace("/", "")
			if (name in list(users_ids.keys()) and time.time() - users_ids[name] > TIME_TO_DEL) or time.time() - os.path.getmtime(filename.path) > TIME_TO_DEL:
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

timer = RepeatedTimer(TIME_TO_DEL, check_for_unused_files)
timer.start()