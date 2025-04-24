import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template,session,flash,redirect, url_for, session,flash
from werkzeug.utils import secure_filename
#from gevent.pywsgi import WSGIServer
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from bs4 import BeautifulSoup

MODEL_PATH ='crop.h5'
MODEL_PATH1 ='pest.h5'
# Load your trained model
cropmodel = load_model(MODEL_PATH)
pestmodel = load_model(MODEL_PATH1)
class_names=['jute', 'maize', 'rice', 'sugarcane', 'wheat']



def model_predict(img_path, pestmodel):
    image=cv2.imread(img_path)
    example = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #plt.imshow(example)
    image_resized= cv2.resize(image, (224,224))
    image=np.expand_dims(image_resized,axis=0)
    pred=pestmodel.predict(image)
    preds=np.argmax(pred)#output=class_names[np.argmax(pred)]
    print(preds)
    trt = pred[0][preds] * 100
    
    if preds==0:
        preds="Ants"       
    elif preds==1:
        
        preds="Bees"
        
    elif preds==2:
        
        preds="Beetle"
        
    elif preds==3:
        
        preds="Catterpillar"
    elif preds==4:
        
        preds="Earthworms"
    elif preds==5:
        
        preds="Earwig"
    elif preds==6:
        
        preds="Grasshopper"
    elif preds==7:
        
        preds="Moth"
    elif preds==8:
        
        preds="Slug"
    elif preds==9:
        
        preds="Snail"
    elif preds==10:
        
        preds="Wasp"
    elif preds==11:
        
        preds="Weevil"
        
    
    
    
    
    return (preds,trt)


pred,trt = model_predict("bees (40).jpg", pestmodel)
print(pred)
pest=pred
