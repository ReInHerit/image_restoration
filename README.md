# Reinherit Toolkits: Old Photos' Restorer


**Based on Bringing Old Photos Back to Life, CVPR2020 (Oral)**


<img src='imgs/HR_result.png'>

## How to run the app
You can choose to test the app in two ways:
- creating a python virtual environment
- using docker

Follow above prerequisites and instructions paying attention to the parts relating to the chosen method.

### Prerequisites
- **Python 3.10** installed on your machine. If you don't have it, you can download it from the official website: https://www.python.org/downloads/ or follow this online guide: https://realpython.com/installing-python/ to install Python on your machine.
- **Javascript** enabled on your browser. If not, you can follow this online guide: https://www.enable-javascript.com/

## Requirements
Depending on which method you have chosen to test the app you must:
  - **Python Virtual Environment**: we recommend using Conda to manage virtual environments, so check in your terminal or command prompt if you have Conda installed by running the command 
    ```
    conda --version 
    ``` 
    If Conda is not installed, follow the installation instructions from the official Anaconda website: https://docs.anaconda.com/anaconda/install/
  - **Docker**: you'll need to set up and run Docker on your operating system. If you are not familiar with Docker, please refer to the official documentation [here](https://docs.docker.com/). 


## Clone this repository and install models and checkpoints
### 1. Clone this repository on your PC. 
### 2. Clone the Synchronized-BatchNorm-PyTorch repository 
In a terminal go to the project folder and run the following code:
```
cd Face_Enhancement/models/networks/
git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .
cd ../../../
```

```
cd Global/detection_models
git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .
cd ../../
```

### 3. Download the landmark detection pretrained model
In a terminal go to the project folder and run the following code:
```
cd Face_Detection/
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
cd ../
```

### 4. Download the pretrained model
Put the file _**Face_Enhancement/checkpoints.zip**_ under **_./Face_Enhancement,_** and put the file **_Global/checkpoints.zip_** under **_./Global_**. Then unzip them respectively.
Use this code:
```
cd Face_Enhancement/
wget https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/face_checkpoints.zip
unzip face_checkpoints.zip
cd ../
cd Global/
wget https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/global_checkpoints.zip
unzip global_checkpoints.zip
cd ../
```
### 5. Manage secret keys
A **Django secret key** is required, **Google Analytics** is optional. \
Edit the .env_template file with your own settings and rename it to .env. 
#### ___Django secret key___: 
1. You can generate one by typing in a terminal: <br> 
   ```
   python getYourDjangoKey.py
   ```
2. copy and paste the generated key in the DJANGO_KEY field of the .env file. 

     <br>
#### ___Google Analytics key___
1. Go to https://analytics.google.com/analytics/web/ and click on the "Get Started for Free" button.
2. Sign in with your Google account.
3. Follow the instructions to create a new account.
4. Once you have created your account, you will be redirected to the dashboard. Click on the "Admin" button in the top left corner.
5. Click on the "Create Property" button.
6. Select "Web" as the property type and click on the "Continue" button.
7. Enter a name for your property and click on the "Create" button.
8. Click on the "Tracking Info" button.
9. Click on the "Tracking Code" button.
10. Copy the "Tracking ID" and paste it in the GA_KEY field of the .env file.


## How to manage python virtual environment
- ### Create a virtual environment and install the requirements
  Open a terminal and navigate to the folder containing the requirements.txt file. \
  Create a virtual environment by typing: 
  ```
  conda create --name my_env_name python=3.10
  ```
  Activate the environment by typing:
  ``` 
  conda activate my_env_name
  ```
  <p>Notice: Replace my_env_name with a relevant name for your environment.
  <p>You have successfully activated your virtual environment. To install the Python libraries required for your project, run the following command while inside the virtual environment: 
  
  ``` 
  pip install -r requirements.txt
  ``` 
- ### How to run the servers
  Open a terminal and navigate to the folder containing the manage.py file. It should be the same as requirements.txt\
  Type:
  ```
  python manage.py runserver
  ```
  Open another terminal and navigate to the folder containing the bring_to_life.py file. It should be the same as requirements.txt\
  Type:
  ```
  python bring_to_life.py
  ```
- ### Open the home page
  Now open a browser and go to the address:  
  ```
  http://localhost:8000
  ```


## Docker

### Build the Dockerfile:

1. In a terminal goto the root of the repository
2. Run this line of code:
```
docker build -t oldphoto
```
3. This will take a while. Wait till the build is finished
4. If the build stops with an error, try to run it again.

### Run the Docker container:
1. In a terminal goto the root of the repository
2. Run 
```
docker run --env-file=.env -e HOST=localhost -p 8000:8000 -p 5000:5000 oldphoto
```
3. Wait till the container is running
4. Open a browser and go to 
```
http://localhost:8000
```
5. You should see the demo page

## How it works

### LANDING PAGE
Click or '**Start to restore**' button to start the demo

### INPUT PAGE
- Click on **BROWSE** button to select the images to upload. You can upload multiple images at the same time. After uploading, you can click on the image to see the original image and the restored image. 
- Select the image or images you want to restore and click Open.
- The selected images will be shown in the browser with 2 checkbox buttons. 
  - If a photo has scratches or damage that needs to be repaired, select the '**with scratches**' checkbox. 
  - And if the image with scratches has a DPI (dots per inch) of 300 or higher, select the checkbox labeled '**is HD**'.
- If you need, you can select again on  **BROWSE** button to upload more images from the same folder.
- When you are ok with the selection, click on the **PROCESS** button to start the restoration process.<br>

Note: The processing time depends on the number of images you upload. The more images you upload, the longer it will take to process.

### OUTPUT PAGE
- The restored images will be shown in the browser.
- For every image, will be shown the original image, the restored image, and, between them, a comparison on the areas most affected by the process.
- Clicking on **DOWNLOAD** button the browser will download the restored images and bring you back to the landing page.
- Clicking on **RESTART** button will bring you back to the landing. **ATTENTION**- You will loose all your processed images!!!



## Citation

If you find our work useful for your research, please consider citing the following papers :)

```bibtex
@inproceedings{wan2020bringing,
title={Bringing Old Photos Back to Life},
author={Wan, Ziyu and Zhang, Bo and Chen, Dongdong and Zhang, Pan and Chen, Dong and Liao, Jing and Wen, Fang},
booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
pages={2747--2757},
year={2020}
}
```

```bibtex
@article{wan2020old,
  title={Old Photo Restoration via Deep Latent Space Translation},
  author={Wan, Ziyu and Zhang, Bo and Chen, Dongdong and Zhang, Pan and Chen, Dong and Liao, Jing and Wen, Fang},
  journal={arXiv preprint arXiv:2009.07047},
  year={2020}
}
```


## License

The codes and the pretrained model in this repository are under the MIT license as specified by the LICENSE file. We use our labeled dataset to train the scratch detection model.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
