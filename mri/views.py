from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.files.base import ContentFile
from PIL import Image
import io
import cv2
import numpy as np
import keras
from tensorflow.keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import base64
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

def home(request):
    if request.user.is_authenticated:
        return render(request,'home.html')
    else:
        return redirect('login')

def about(request):
    return render(request,'about.html')

def credits(request):
    return render(request,'credits.html')

def result(request):
    description = {
        'Glioma Tumor': 'Glioma is a growth of cells that starts in the brain or spinal cord. The cells in a glioma look similar to healthy brain cells called glial cells. Glial cells surround nerve cells and help them function.',
        'Meningioma Tumor': 'A meningioma is a tumor that grows from the membranes that surround the brain and spinal cord, called the meninges. A meningioma is not a brain tumor, but it may press on the nearby brain, nerves and vessels. Meningioma is the most common type of tumor that forms in the head.',
        'No Tumor': 'Congratulations!!! You have got no tumor.',
        'Pituitary Tumor': "Pituitary tumors are unusual growths that develop in the pituitary gland. This gland is an organ about the size of a pea. It's located behind the nose at the base of the brain. Some of these tumors cause the pituitary gland to make too much of certain hormones that control important body functions. Others can cause the pituitary gland to make too little of those hormones."
    }
    error = 0
    result = None
    img_byte_arr = None
    res = None
    if request.method == 'POST':
        try:
            model = keras.models.load_model(BASE_DIR / 'mri/model.h5')
            img = request.FILES.get('image')
            img = Image.open(img)
            realimg = img
            img_byte_arr = io.BytesIO()
            # define quality of saved array
            realimg.save(img_byte_arr, format='JPEG', subsampling=0, quality=100)
            # converts image array to bytesarray
            img_byte_arr = base64.b64encode(img_byte_arr.getvalue()).decode('UTF-8')
            img = np.asarray(img)
            cpyimg = img
            dim = (224,224)
            img = cv2.resize(img, dim,interpolation = cv2.INTER_AREA)
            X = image.img_to_array(img)
            X = np.expand_dims(X, axis=0)
            if X.shape[3] == 1:
                img = cpyimg
                img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
                img = cv2.resize(img, dim,interpolation = cv2.INTER_AREA)
                X = image.img_to_array(img)
                X = np.expand_dims(X, axis=0)
            X = preprocess_input(X)
            result = model.predict(X)
            for r in result.tolist()[0]:
                print(r*100)
            result = result.argmax()
            category = ['Glioma Tumor', 'Meningioma Tumor', 'No Tumor', 'Pituitary Tumor']
            result = category[int(result)]
            error = 1
        except:
            error = 2
        return render(request, 'result.html', {'result': result, 'img':img_byte_arr, 'error':error, 'description':description[result]})
    else:
        return redirect('home')



def logout(request):
    auth_logout(request)
    return redirect ('/')

def login(request):
    message = {'success': '', 'error': ''}
    if request.user.is_authenticated:
            return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                user = authenticate(username = username, password = password)
            except:
                user = None
            if user:
                auth_login(request, user)
                return redirect('home')
            else:
                message['error'] = 'Invalid Username or Password.'
        return render(request, 'registration/login.html', {'message':message})
        
def register(request):
    message = {'success': '', 'error': ''}
    if request.user.is_authenticated:
            return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm-password')
            if username and password and password == confirmPassword:
                try:
                    user = User.objects.create(username = username)
                    user.set_password(password)
                    user.save()
                    message['success'] = 'User Created Successfully.'
                except:
                    message['error'] = 'Username Already Exists.'
            else:
                message['error'] = 'Passwords donot match.'
            
        return render(request, 'registration/register.html', {'message':message})