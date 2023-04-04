# Old Photo Restoration (Official PyTorch Implementation)

<img src='imgs/0001.jpg'/>

### [Project Page](http://raywzy.com/Old_Photo/) | [Paper (CVPR version)](https://arxiv.org/abs/2004.09484) | [Paper (Journal version)](https://arxiv.org/pdf/2009.07047v1.pdf) | [Pretrained Model](https://hkustconnect-my.sharepoint.com/:f:/g/personal/bzhangai_connect_ust_hk/Em0KnYOeSSxFtp4g_dhWdf0BdeT3tY12jIYJ6qvSf300cA?e=nXkJH2) | [Colab Demo](https://colab.research.google.com/drive/1NEm6AsybIiC5TwTU_4DqDkQO0nFRB-uA?usp=sharing)  | [Replicate Demo & Docker Image](https://replicate.ai/zhangmozhe/bringing-old-photos-back-to-life) :fire:

**Bringing Old Photos Back to Life, CVPR2020 (Oral)**


<img src='imgs/HR_result.png'>

Training code is available and welcome to have a try and learn the training details. 


## Requirement
The code is tested on Ubuntu with Nvidia GPUs and CUDA installed. Python>=3.6 is required to run the code.

## Installation

Clone the Synchronized-BatchNorm-PyTorch repository for

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

Download the landmark detection pretrained model

```
cd Face_Detection/
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
cd ../
```

Download the pretrained model, put the file `Face_Enhancement/checkpoints.zip` under `./Face_Enhancement`, and put the file `Global/checkpoints.zip` under `./Global`. Then unzip them respectively.

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

Install dependencies:

```
pip install -r requirements.txt
```


### Docker

#### build the Dockerfile:

1. In a terminal goto the root of the repository
2. Run 
```
docker build -t oldphoto
```
3. This will take a while. Wait till the build is finished
4. If the build stops with an error, try to run ```docker build --no-cache -t oldphoto```. instead

#### run the Docker container:
1. In a terminal goto the root of the repository
2. Run 
```
docker run --env-file=.env -p 8000:8000 -p 5000:5000 oldphoto
```
3. Wait till the container is running
4. Open a browser and go to 
```
http://localhost:8000/`
```
5. You should see the demo page

## How it works

### 1) LANDING PAGE
Click or '**Start to restore**' button to start the demo

### 2) INPUT PAGE
- Click on **BROWSE button** to select the images to upload. You can upload multiple images at the same time. After uploading, you can click on the image to see the original image and the restored image. 
- Select the image or images you want to restore and click Open.
- The selected images will be shown in the browser with 2 checkbox buttons. 
  - If a photo has scratches or damage that needs to be repaired, select the '**with scratches**' checkbox. 
  - And if the image with scratches has a DPI (dots per inch) of 300 or higher, select the checkbox labeled '**is HD**'.
- If you need, you can select again on  **BROWSE button** to upload more images from the same folder.
- When you are ok with the selection, click on the '**PROCESS**' button to start the restoration process.<br>

Note: The processing time depends on the number of images you upload. The more images you upload, the longer it will take to process.

### 3) OUTPUT PAGE
- The restored images will be shown in the browser.
- For every image, will be shown the original image, the restored image, and, between them, a comparison on the areas most affected by the process.
- Clicking on **DOWNLOAD** button the browser will download the restored images and bring you back to the landing page.
- Clicking on **RESTART** button will bring you back to the landing. ATTENTION YOU will loose all your processed images



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
