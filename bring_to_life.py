import numpy as np
import cv2
import PySimpleGUI as sg
import os.path
import argparse
import os
import sys
import shutil
from subprocess import call
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from PIL import Image
app = Flask(__name__)
CORS(app)
input_folder = './media/input_images'
media_folder = './media'
output_folder = './media/output_images'

@app.route('/upload-image', methods=['POST'])
@cross_origin()
def upload_image():
    if os.path.exists(media_folder):
        shutil.rmtree(media_folder)
    os.makedirs(media_folder)
    if os.path.exists(input_folder):
        shutil.rmtree(input_folder)
    os.makedirs(input_folder)
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    files = request.files.getlist('image')
    if not files:
        return jsonify({'error': 'No images found'})
    processed_images = []
    for image in files:
        if image.content_type not in ['image/jpeg', 'image/png']:
            return jsonify({'error': 'Invalid image format'})
        img = Image.open(image)  # .imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
        # Perform image processing here
        # Save input image
        input_filename = os.path.join(input_folder, image.filename)

        print(image.filename.split('.')[0], image.filename.split('.')[1])
        # Example image processing: resize to 300x300
        img.save(input_filename)
        # img.save(input_f)
        # Save processed image
        output_filename = os.path.join(output_folder, 'final_output', image.filename)
        # cv2.imwrite(output_filename, img)
        processed_images.append(output_filename)
    modify()

    for file in os.listdir(input_folder):
        print(file)
        name, ext = file.split('.')
        input_src = os.path.join(input_folder, file)
        output_src = os.path.join(output_folder, 'final_output', file)
        input_f = os.path.join(media_folder, name + '_input.' + ext)
        output_f = os.path.join(media_folder, name + '_output.' + ext)
        paragon_f = os.path.join(media_folder, name + '_paragon.' + ext)
        shutil.copy(input_src, input_f)
        shutil.copy(output_src, output_f)
        differences(input_f, output_f,  paragon_f)

    return jsonify({'images': processed_images})



print('ce so')
def modify(image_filename=None, cv2_frame=None):

    def run_cmd(command):
        try:
            call(command, shell=True)
        except KeyboardInterrupt:
            print("Process interrupted")
            sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", type=str, default=input_folder, help="Test images")
    parser.add_argument("--output_folder", type=str, default=output_folder,
                        help="Restored images, please use the absolute path")
    parser.add_argument("--GPU", type=str, default="-1", help="0,1,2")
    parser.add_argument("--checkpoint_name", type=str, default="Setting_9_epoch_100", help="choose which checkpoint")
    parser.add_argument("--with_scratch", default="--with_scratch", action="store_true")

    opts = parser.parse_args()

    gpu1 = opts.GPU

    # resolve relative paths before changing directory
    opts.input_folder = os.path.abspath(opts.input_folder)
    opts.output_folder = os.path.abspath(opts.output_folder)
    if not os.path.exists(opts.output_folder):
        os.makedirs(opts.output_folder)
    print("Input folder: ", opts.input_folder)
    print("Output folder: ", opts.output_folder)
    main_environment = os.getcwd()

    # Stage 1: Overall Quality Improve
    print("Running Stage 1: Overall restoration")
    print("current directory: ", os.getcwd())
    os.chdir(os.path.join(main_environment, "Global"))
    stage_1_input_dir = opts.input_folder
    stage_1_output_dir = os.path.join(opts.output_folder, "stage_1_restore_output")
    if not os.path.exists(stage_1_output_dir):
        os.makedirs(stage_1_output_dir)

    if not opts.with_scratch:
        stage_1_command = (
            "python test.py --test_mode Full --Quality_restore --test_input "
            + stage_1_input_dir
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu1
        )
        run_cmd(stage_1_command)
    else:
        mask_dir = os.path.join(stage_1_output_dir, "masks")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        stage_1_command_1 = ("python detection.py --test_path " + stage_1_input_dir + " --output_dir " + mask_dir
            + " --input_size full_size" + " --GPU " + gpu1)
        stage_1_command_2 = ("python test.py --Scratch_and_Quality_restore --test_input " + new_input + " --test_mask "
            + new_mask + " --outputs_dir " + stage_1_output_dir + " --gpu_ids " + gpu1 )
        run_cmd(stage_1_command_1)
        run_cmd(stage_1_command_2)

    # Solve the case when there is no face in the old photo
    stage_1_results = os.path.join(stage_1_output_dir, "restored_image")
    stage_4_output_dir = os.path.join(opts.output_folder, "final_output")
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
    stage_2_input_dir = os.path.join(stage_1_output_dir, "restored_image")
    stage_2_output_dir = os.path.join(opts.output_folder, "stage_2_detection_output")
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
    stage_3_input_mask = "./"
    stage_3_input_face = stage_2_output_dir
    stage_3_output_dir = os.path.join(opts.output_folder, "stage_3_face_output")
    if not os.path.exists(stage_3_output_dir):
        os.makedirs(stage_3_output_dir)
    stage_3_command = ("python test_face.py --old_face_folder " + stage_3_input_face + " --old_face_label_folder "
        + stage_3_input_mask + " --tensorboard_log --name " + opts.checkpoint_name + " --gpu_ids " + gpu1
        + " --load_size 256 --label_nc 18 --no_instance --preprocess_mode resize --batchSize 4 --results_dir "
        + stage_3_output_dir + " --no_parsing_map")
    run_cmd(stage_3_command)
    print("Finish Stage 3 ...")
    print("\n")

    # Stage 4: Warp back
    print("Running Stage 4: Blending")
    os.chdir(os.path.join(main_environment, "Face_Detection"))
    # os.chdir(".././Face_Detection")
    stage_4_input_image_dir = os.path.join(stage_1_output_dir, "restored_image")
    stage_4_input_face_dir = os.path.join(stage_3_output_dir, "each_img")
    stage_4_output_dir = os.path.join(opts.output_folder, "final_output")
    if not os.path.exists(stage_4_output_dir):
        os.makedirs(stage_4_output_dir)
    stage_4_command = ("python align_warp_back_multiple_dlib.py --origin_url " + stage_4_input_image_dir
        + " --replace_url " + stage_4_input_face_dir + " --save_url " + stage_4_output_dir )
    run_cmd(stage_4_command)
    print("Finish Stage 4 ...")
    print("\n")

    print("All the processing is done. Please check the results.")
    os.chdir(".././")

def differences(input_image_path, output_image_path, paragon_path):
    input_image = Image.open(input_image_path)
    output_image = Image.open(output_image_path)
    size_input = input_image.size
    size_output = output_image.size
    if size_input != size_output:
        output_image = output_image.resize(size_input)
        output_image.save(output_image_path)

    # convert to numpy arrays and subtract
    input_array = np.array(input_image)
    output_array = np.array(output_image)
    input_gray = np.dot(input_array[..., :3], [0.2989, 0.5870, 0.1140])
    output_gray = np.dot(output_array[..., :3], [0.2989, 0.5870, 0.1140])

    result = (input_gray - output_gray)

    # set negative values to zero
    result[result < 0] = 0

    # convert back to PIL image and save
    result_image = Image.fromarray(result.astype('uint8'))
    result_image.save(paragon_path)

if __name__ == '__main__':
    app.run(debug=True)