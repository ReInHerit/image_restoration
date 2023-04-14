import numpy as np
import os.path
import argparse
import os
import sys
import shutil
from subprocess import call
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from PIL import Image
import torch

print(f"Is CUDA supported by this system? {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")

port = int(os.environ.get('FLASK_PORT', 5000))
print(f'Flask server received port: {port}')

app = Flask(__name__)
CORS(app)

input_folder = './media/input_images'
input_scratched = './media/input_scratched_images'
input_hd = './media/input_hd_images'
media_folder = './media'
output_folder = './media/output_images'

@app.route('/upload-image', methods=['POST'])
@cross_origin()
def upload_image():
    global input_folder, input_scratched, input_hd, media_folder, output_folder
    user_id = request.headers.get('X-USER-ID')
    media_folder = './media/' + user_id
    input_folder = media_folder + '/input_images'
    input_scratched = media_folder + '/input_scratched_images'
    input_hd = media_folder + '/input_hd_images'
    output_folder = media_folder + '/output_images'
    folders = [media_folder, input_folder, input_scratched, input_hd, output_folder]
    processed_images = []
    app.logger.info('Resetting folders')
    for folder in folders:
        delete_and_make_folder(folder)
    app.logger.info('Receiving images...')
    files = request.files.getlist('base')
    app.logger.info('Received images')
    scratched = request.values.getlist('scratched')
    hd_files = request.values.getlist('hd')
    if not files:
        return jsonify({'error': 'No images found'})
    for i in range(len(files)):
        image = files[i]
        if image.content_type not in ['image/jpeg', 'image/png']:
            return jsonify({'error': 'Invalid image format'})
        img = Image.open(image)
        if scratched[i] == 'true' and hd_files[i] == 'true':
            input_filename = os.path.join(input_hd, image.filename)
        elif scratched[i] == 'true' and hd_files[i] == 'false':
            input_filename = os.path.join(input_scratched, image.filename)
        else:
            input_filename = os.path.join(input_folder, image.filename)
        img.save(input_filename)

    modify()
    for file in os.listdir(os.path.join(output_folder, 'stage_1_restore_output', 'input_image')):
        processed_images.append(file)
    differences(input_folder)
    differences(input_scratched)
    differences(input_hd)
    response = jsonify({'images': processed_images})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/write', methods=['GET'])
def write():
    return jsonify({'message': 'Hello World!'})

@app.route('/delete-temp-folder/<user>', methods=['DELETE'])
def delete_temp_folder(user):
    folder_path = f'./media/{user}'
    shutil.rmtree(folder_path, ignore_errors=True)
    return jsonify({'message': f'Temp folder for user {user} has been deleted.'})


def modify(image_filename=None, cv2_frame=None, scratched=None):
    def run_cmd(command):
        try:
            call(command, shell=True)
        except KeyboardInterrupt:
            print("Process interrupted")
            sys.exit(1)
    gpu = -1
    if torch.cuda.is_available():
        cuda_id = torch.cuda.current_device()
        gpu = cuda_id
    gpu = str(gpu)
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", type=str, default=input_folder, help="Test images")
    parser.add_argument("--input_scratched", type=str, default=input_scratched, help="Test images")
    parser.add_argument("--input_hd", type=str, default=input_hd, help="Test images")
    parser.add_argument("--output_folder", type=str, default=output_folder,
                        help="Restored images, please use the absolute path")
    parser.add_argument("--GPU", type=str, default=gpu, help="0,1,2")
    parser.add_argument("--checkpoint_name", type=str, default="Setting_9_epoch_100", help="choose which checkpoint")
    parser.add_argument("--with_scratch", default="--with_scratch", action="store_true")

    opts = parser.parse_args()

    gpu1 = opts.GPU

    # resolve relative paths before changing directory
    opts.input_folder = os.path.abspath(opts.input_folder)
    opts.input_scratched = os.path.abspath(opts.input_scratched)
    opts.input_hd = os.path.abspath(opts.input_hd)
    opts.output_folder = os.path.abspath(opts.output_folder)
    if not os.path.exists(opts.output_folder):
        os.makedirs(opts.output_folder)
    main_environment = os.getcwd()

    # Stage 1: Overall Quality Improve
    print("Running Stage 1: Overall restoration")
    print("current directory: ", os.getcwd())
    os.chdir(os.path.join(main_environment, "Global"))
    stage_1_input_dir = opts.input_folder
    stage_1_scratched_dir = opts.input_scratched
    stage_1_hd_dir = opts.input_hd
    stage_1_output_dir = os.path.join(opts.output_folder, "stage_1_restore_output")
    if not os.path.exists(stage_1_output_dir):
        os.makedirs(stage_1_output_dir)
    if not len(os.listdir(stage_1_scratched_dir)) == 0:
        mask_dir = os.path.join(stage_1_output_dir, "masks")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        stage_1_command_1 = ("python detection.py --test_path " + stage_1_scratched_dir + " --output_dir " + mask_dir
                             + " --input_size full_size" + " --GPU " + gpu1)
        stage_1_command_2 = ("python test.py --Scratch_and_Quality_restore --test_input " + new_input + " --test_mask "
                             + new_mask + " --outputs_dir " + stage_1_output_dir + " --gpu_ids " + gpu1)
        run_cmd(stage_1_command_1)
        run_cmd(stage_1_command_2)
    if not len(os.listdir(stage_1_hd_dir)) == 0:
        mask_dir = os.path.join(stage_1_output_dir, "masks_hd")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        stage_1_command_1 = ("python detection.py --test_path " + stage_1_hd_dir + " --output_dir " + mask_dir
                             + " --input_size full_size" + " --GPU " + gpu1)
        stage_1_command_2 = ("python test.py --Scratch_and_Quality_restore --test_input " + new_input + " --test_mask "
                             + new_mask + " --outputs_dir " + stage_1_output_dir + " --gpu_ids " + gpu1 + " --HR")
        run_cmd(stage_1_command_1)
        run_cmd(stage_1_command_2)
    if not len(os.listdir(stage_1_input_dir)) == 0:
        stage_1_command = (
            "python test.py --test_mode Full --Quality_restore --test_input "
            + stage_1_input_dir
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu1
        )
        run_cmd(stage_1_command)

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


def delete_and_make_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)


def differences(folder):
    check_folder = os.path.join(output_folder, 'stage_1_restore_output', 'input_image')
    check_files = os.listdir(check_folder)
    for file in os.listdir(folder):
        name, ext = os.path.splitext(file)
        for filename in check_files:
            if os.path.splitext(filename)[0] == name:
                ext = os.path.splitext(filename)[1]
                break

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


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.logger.info(f'Starting Flask server on port: {port}')
    app.run(debug=False, host='0.0.0.0', port=port)
