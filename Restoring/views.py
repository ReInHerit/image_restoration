
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import uuid
from django.conf import settings
import os.path
import argparse
import sys
from PIL import Image
import torch
import shutil
import numpy as np
from subprocess import call
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt
input_folder = './media/input_images'
input_scratched = './media/input_scratched_images'
input_hd = './media/input_hd_images'
media_folder = './media'
output_folder = './media/output_images'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:256, garbage_collection_threshold:0.5"


def index(response):
    return HttpResponse("This message is from Restoring App")


def landing(request):
    user_id = str(uuid.uuid4())[:8]  # Generate a unique user ID
    protocol = settings.PROTOCOL
    host = settings.HOST
    port = settings.PORT
    GA_MEASUREMENT_ID = settings.GA_MEASUREMENT_ID
    print(f'GA_MEASUREMENT_ID_VIEWS: {GA_MEASUREMENT_ID}')
    request.session['user_id'] = user_id  # Store the user ID in the session
    # request.session['temp_dir'] = temp_dir  # Store the path to the temporary directory in the session
    return render(request, 'landing.html', {'user_id': user_id, 'protocol': protocol, 'host': host, 'port': port, 'GA_MEASUREMENT_ID': GA_MEASUREMENT_ID})

@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([])
def delete_temp_folder(request):
    user_id = request.headers.get('X-USER-ID')
    folder_path = f'./media/{user_id}'
    shutil.rmtree(folder_path, ignore_errors=True)
    return JsonResponse({'message': f'Temp folder for user {user_id} has been deleted.'})

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def upload_image(request):
    global input_folder, input_scratched, input_hd, media_folder, output_folder
    user_id = request.headers.get('X-USER-ID')
    media_folder = './media/' + user_id
    input_folder = media_folder + '/input_images'
    input_scratched = media_folder + '/input_scratched_images'
    input_hd = media_folder + '/input_hd_images'
    output_folder = media_folder + '/output_images'
    folders = [media_folder, input_folder, input_scratched, input_hd, output_folder]
    processed_images = []
    for folder in folders:
        delete_and_make_folder(folder)
    print(request.FILES)
    files = request.FILES.getlist('base')
    scratched = request.POST.getlist('scratched')
    hd_files = request.POST.getlist('hd')

    if not files:
        return JsonResponse({'error': 'No images found'})

    for i in range(len(files)):
        image = files[i]
        print(type(str(image)), str(image))
        if image.content_type not in ['image/jpeg', 'image/png']:
            return JsonResponse({'error': 'Invalid image format'})
        img = Image.open(image)
        if scratched[i] == 'true' and hd_files[i] == 'true':
            input_filename = os.path.join(input_hd, str(image))
        elif scratched[i] == 'true' and hd_files[i] == 'false':
            input_filename = os.path.join(input_scratched, str(image))
        else:
            input_filename = os.path.join(input_folder, str(image))
        img.save(input_filename)

    modify()
    for file in os.listdir(os.path.join(output_folder, 'stage_1_restore_output', 'input_image')):
        processed_images.append(file)
    differences(input_folder)
    differences(input_scratched)
    differences(input_hd)
    return JsonResponse({'images': processed_images})


def modify(image_filename=None, cv2_frame=None, scratched=None):

    def run_cmd(command):
        try:
            call(command, shell=True)
        except KeyboardInterrupt:
            print("Process interrupted")
            sys.exit(1)

    gpu = -1
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        print('Number of GPUs available:', num_gpus)
        for i in range(num_gpus):
            cuda_properties = torch.cuda.get_device_properties(i)
            gpu_memory = cuda_properties.total_memory / 1024 ** 3  # Convert bytes to gigabytes

            if gpu_memory > 4:
                gpu = i
                print('GPU with more than 4 GB of RAM:', i, torch.cuda.mem_get_info(i))
                break

    if gpu == -1:
        print('No suitable GPU found. Setting gpu = -1')
    else:
        print('Selected GPU:', gpu)
    gpu = str(gpu)
    checkpoint_name = "Setting_9_epoch_100"

    # resolve relative paths before changing directory

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    main_environment = os.getcwd()
    media_environment = os.path.join(main_environment, "media")
    # Stage 1: Overall Quality Improve
    print("Running Stage 1: Overall restoration")
    os.chdir(os.path.join(main_environment, "Global"))
    print("current directory: ", os.getcwd())
    print("output folder: ", output_folder)
    stage_1_input_dir = os.path.join("..", input_folder)
    stage_1_scratched_dir = os.path.join("..", input_scratched)
    stage_1_hd_dir = os.path.join("..", input_hd)
    stage_1_output_dir = os.path.join("..", output_folder, "stage_1_restore_output")
    print("stage 1 output folder: ", stage_1_output_dir)
    if not os.path.exists(stage_1_output_dir):
        os.makedirs(stage_1_output_dir)
    if not len(os.listdir(stage_1_scratched_dir)) == 0:
        mask_dir = os.path.join(stage_1_output_dir, "masks")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        stage_1_command_1 = ("python detection.py --test_path " + stage_1_scratched_dir + " --output_dir " + mask_dir
                             + " --input_size full_size" + " --GPU " + gpu)
        stage_1_command_2 = ("python test.py --Scratch_and_Quality_restore --test_input " + new_input + " --test_mask "
                             + new_mask + " --outputs_dir " + stage_1_output_dir + " --gpu_ids " + gpu)
        run_cmd(stage_1_command_1)
        run_cmd(stage_1_command_2)
    if not len(os.listdir(stage_1_hd_dir)) == 0:
        mask_dir = os.path.join(stage_1_output_dir, "masks_hd")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        stage_1_command_1 = ("python detection.py --test_path " + stage_1_hd_dir + " --output_dir " + mask_dir
                             + " --input_size full_size" + " --GPU " + gpu)
        stage_1_command_2 = ("python test.py --Scratch_and_Quality_restore --test_input " + new_input + " --test_mask "
                             + new_mask + " --outputs_dir " + stage_1_output_dir + " --gpu_ids " + gpu + " --HR")
        run_cmd(stage_1_command_1)
        run_cmd(stage_1_command_2)
    if not len(os.listdir(stage_1_input_dir)) == 0:
        stage_1_command = (
            "python test.py --test_mode Full --Quality_restore --test_input "
            + stage_1_input_dir
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu
        )
        run_cmd(stage_1_command)

    # Solve the case when there is no face in the old photo
    stage_1_results = os.path.join(stage_1_output_dir, "restored_image")
    stage_4_output_dir = os.path.join("..", output_folder, "final_output")
    print("current directory: ", os.getcwd())
    if not os.path.exists(stage_4_output_dir):
        os.makedirs(stage_4_output_dir)
    for x in os.listdir(stage_1_results):
        img_dir = os.path.join(stage_1_results, x)
        shutil.copy(img_dir, stage_4_output_dir)

    print("Finish Stage 1 ...")
    print("\n")

    # Stage 2: Face Detection

    print("Running Stage 2: Face Detection")
    os.chdir(".././Face_Detection")
    print("stage 2 current dir: ", os.getcwd())
    stage_2_input_dir = os.path.join(stage_1_output_dir, "restored_image")
    stage_2_output_dir = os.path.join("..", output_folder, "stage_2_detection_output")
    print("stage 2 input folder: ", stage_2_input_dir)
    print("stage 2 output folder: ", stage_2_output_dir)
    if not os.path.exists(stage_2_output_dir):
        os.makedirs(stage_2_output_dir)
    stage_2_command = ("python detect_all_dlib.py --url " + stage_2_input_dir + " --save_url " + stage_2_output_dir)
    run_cmd(stage_2_command)
    print("Finish Stage 2 ...")
    print("\n")

    # Stage 3: Face Restore
    print("Running Stage 3: Face Enhancement")
    os.chdir(os.path.join(main_environment, "Face_Enhancement"))
    # os.chdir(".././Face_Enhancement")
    print("stage 3 current dir: ", os.getcwd())
    stage_3_input_mask = "./"
    stage_3_input_face = stage_2_output_dir
    stage_3_output_dir = os.path.join("..", output_folder, "stage_3_face_output")
    print("stage 3 input face folder: ", stage_3_input_face)
    print("stage 3 input mask folder: ", stage_3_input_mask)
    print("stage 3 output folder: ", stage_3_output_dir)
    if not os.path.exists(stage_3_output_dir):
        os.makedirs(stage_3_output_dir)
    stage_3_command = ("python test_face.py --dataroot ./ --old_face_folder " + stage_3_input_face + " --old_face_label_folder "
        + stage_3_input_mask + " --tensorboard_log --name " + checkpoint_name + " --gpu_ids " + gpu
        + " --load_size 256 --label_nc 18 --no_instance --preprocess_mode resize --batchSize 4 --results_dir "
        + stage_3_output_dir + " --no_parsing_map")
    run_cmd(stage_3_command)
    print("Finish Stage 3 ...")
    print("\n")

    # Stage 4: Warp back
    print("Running Stage 4: Blending")
    os.chdir(os.path.join(main_environment, "Face_Detection"))
    print("stage 4 current dir: ", os.getcwd())
    stage_4_input_image_dir = os.path.join(stage_1_output_dir, "restored_image")
    stage_4_input_face_dir = os.path.join(stage_3_output_dir, "each_img")
    stage_4_output_dir = os.path.join("..", output_folder, "final_output")
    print("stage 4 input image folder: ", stage_4_input_image_dir)
    print("stage 4 input face folder: ", stage_4_input_face_dir)
    print("stage 4 output folder: ", stage_4_output_dir)
    if not os.path.exists(stage_4_output_dir):
        os.makedirs(stage_4_output_dir)
    stage_4_command = ("python align_warp_back_multiple_dlib.py --origin_url " + stage_4_input_image_dir
        + " --replace_url " + stage_4_input_face_dir + " --save_url " + stage_4_output_dir )
    run_cmd(stage_4_command)
    print("Finish Stage 4 ...")
    print("\n")

    print("All the processing is done. Please check the results.")
    os.chdir(".././")


def delete_and_make_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)


def differences(folder):
    check_folder = os.path.join(output_folder, 'stage_1_restore_output', 'input_image')
    print("current dir: ", os.getcwd())
    print("differences stage - check folder: ", check_folder)
    check_files = os.listdir(check_folder)
    for file in os.listdir(folder):
        name, ext = os.path.splitext(file)
        found = False
        for filename in check_files:
            if os.path.splitext(filename)[0] == name:
                ext = os.path.splitext(filename)[1]
                found = True
                break

        if not found:
            print(f"Skipping {file} - corresponding file not found in check folder")
            continue
        input_src = os.path.join(folder, file)
        output_src = os.path.join(output_folder, 'final_output', name + ext)
        input_f = os.path.join(media_folder, name + '_input' + ext)
        output_f = os.path.join(media_folder, name + '_output' + ext)
        paragon_f = os.path.join(media_folder, name + '_paragon' + ext)

        shutil.copy(input_src, input_f)
        shutil.copy(output_src, output_f)

        input_image = Image.open(input_f)
        output_image = Image.open(output_f)

        if input_image.size != output_image.size:
            output_image = output_image.resize(input_image.size)
            output_image.save(output_f)

        input_gray = np.dot(np.array(input_image)[..., :3], [0.2989, 0.5870, 0.1140])
        output_gray = np.dot(np.array(output_image)[..., :3], [0.2989, 0.5870, 0.1140])

        result = np.maximum(input_gray - output_gray, 0)

        result_image = Image.fromarray(result.astype('uint8'))
        result_image.save(paragon_f)