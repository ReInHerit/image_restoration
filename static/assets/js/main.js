let selected_images = [];
let scratched_images = [];
let hd_images = [];


$(document).ready(function () {
    const user_id = window.user_id;
    const port = window.port;
    const host = window.host;
    const protocol = window.protocol;
    console.log('protocol: ', protocol, 'host: ', host, 'port: ', port, 'user_id: ', user_id)
    const landing_section = "<div id='landing'>\n" +
        "            <h1>Welcome to ReInHerit's Old Photos' Restorer!</h1> <p>Our virtual toolkit has been designed to assist museum owners and enthusiasts in effortlessly restoring old photos. " +
        "       <p>By simply uploading your photo, whether it has scratches or not, our advanced processing algorithms will work their magic. Once the image processing is complete, you will have a fully restored photo to cherish and share with future generations.<br>" +
        "Try it out today and rediscover the beauty of your old photographs!</p>\n" +
        "            <img id='cover_image' alt='landing image' src='static/assets/images/scratch_detection.png'>\n" +
        "            <a id='start_button'  class='square_btn'>START TO RESTORE</a>\n" +
        "        </div>"
    const input_section = "<div id='input-section'>\n" +
        "  <div id='input-description'>\n" +
        "  <h1>INPUT</h1>\n" +
        "  <p class='vertical'>To load images from your hard disk, browse to the folder where they're stored and select the ones you want. You can load as many images as you'd like from the same folder. However, keep in mind that the more files you choose and the larger their size, the longer it will take to process and load them. So, please be patient while the files are being processed. \n" +
        "      <br>\n" +
        "      If a photo has scratches or damage that needs to be repaired, select the 'with scratches' checkbox. And if the image with scratches has a DPI (dots per inch) of 300 or higher, select the checkbox labeled 'is HD'.</p>\n" +
        "  </div>\n" +
        "  <form id='image-form'>\n" +
        "      <a class='square_btn' type='button' onclick=\"document.getElementById('image-input').click(); return false;\"> BROWSE </a>\n" +
        "      <input type='file' id='image-input' name='image' class='hidden_tag' accept='image/*' multiple>\n" +
        "      <div id='selected-images' ></div>\n" +
        "      <br>\n" +
        "      <a id='submit_label' class='square_btn' type='button' onclick=\"document.getElementById('submit-button').click(); return false;\"> PROCESS </a>\n" +
        "      <button id='submit-button' type='submit' class='hidden_tag'></button>\n" +
        "      <br>\n" +
        "  </form>\n" +
        "  <div id='enlarged' class='hidden_tag'> </div>\n" +
        "  </div>"

    const loading_div = "<div id='loader'>\n" +
        "  <p id='shadow'></p>\n" +
        "  <div id='shadow'></div>\n" +
        "  <div id='box'></div>\n" +
        "  <input type='text' id='loading-text' value='Starting process...' />\n" +
        "</div>"

    const output_section = "<div id='output-section'>\n" +
        "  <div id='output-description'>\n" +
        "       <h1>OUTPUT</h1>\n" +
        "       <div class='vertical'><p>Here you can see the results of the processing:</p>" +
        "           <ul style='list-style-type:disc;'>\n" +
        "               <li>The first image is the original image</li>\n" +
        "               <li>The second is an image of comparison on the areas most affected by the process.</li>\n" +
        "               <li>The third image is the output image</li>\n" +
        "           </ul>\n" +
        "       <p>If you click the DOWNLOAD button, the app saves the outputs to your PC and returns to the home page.</p>\n" +
        "       <p>If you click the RESTART button, the app returns to the home page and deletes all the processed images.</p></div>\n" +
        "  </div>\n" +
        "  <div id='output-images'>\n" +
        "  </div>\n" +
        "<div id='buttons'>" +
        "   <a id='download_button'  class='square_btn'>DOWNLOAD</a>\n" +
        "   <p id='or'> or </p>\n" +
        "   <a id='restart_button'  class='square_btn'>RESTART</a>\n" +
        "</div>\n" +
        "      <br>\n" +
        "</div>\n" +
        "<div id='enlarged' class='hidden_tag'> </div>\n" +
        "  </div>"

    let main_section = $("#central");

    main_section.html(landing_section);

    const startButton = $("#start_button");  // select the substitute button by ID
    const landing = $("#landing");  // select the landing element by ID

    // ENTERING INPUT SECTION
    startButton.click(function () {
        landing.replaceWith(input_section);  // replace the landing element with the new input section
        let files = {}
        let fileList = []

        const submit_label = $("#submit_label");  // select the landing element by ID
        submit_label.addClass('hidden_tag')
        $("#image-input").change(function () {  // add a change event listener to the file input
            const selected_files = $(this)[0].files;
            console.log('selected files: ', selected_files)
            if (Object.keys(files).length === 0) {
                files = selected_files;
            } else {
                for (let i = 0; i < selected_files.length; i++) {
                    // does the file already exist?
                    if (Object.values(files).some(e =>
                        e.name === selected_files[i].name &&
                        e.size === selected_files[i].size &&
                        e.type === selected_files[i].type)) {
                        console.log(selected_files[i].name + ' already exists')
                    } else {
                        // does the key already exist in files object? if yes, create a new key
                        if (Object.keys(files).some(e => Number(e) === i)) {
                            let new_key = Object.keys(files).length

                            files = {...files, [new_key]: selected_files[i]}
                        } else {
                            files = {...files, [i]: selected_files[i]}
                        }
                    }
                }
            }
            const dataTransfer = new DataTransfer();
            submit_label.removeClass('hidden_tag')
            for (let i = 0; i < Object.keys(files).length; i++) {
                const file = new File([files[i]], files[i].name, {
                    type: files[i].type,
                    lastModified: files[i].lastModified
                });
                dataTransfer.items.add(file);
            }
            fileList = dataTransfer.files;
            // loop through the selected files
            for (let i = 0; i < fileList.length; i++) {
                console.log('file ', i, ': ', fileList[i].name)
                if (!selected_images.some(e =>
                    e.name === fileList[i].name &&
                    e.size === fileList[i].size &&
                    e.type === fileList[i].type)) {
                    selected_images.push(fileList[i])
                    // create a file reader
                    var reader = new FileReader();

                    // add a load event listener to the file reader
                    reader.onload = function (event) {
                        const image_name = fileList[i].name
                        scratched_images.push('')
                        hd_images.push('')
                        // create an tags element
                        let image = document.createElement("img");
                        let image_div = document.createElement("div");
                        let checkbox_1 = document.createElement("div");
                        let checkbox_2 = document.createElement("div");

                        image.src = event.target.result;
                        image.id = image_name;
                        image.height = 200;
                        image_div.id = image_name + '_div';

                        checkbox_1.innerHTML = '<input type="checkbox" class="checkbox" id="check_' + image_name + '" onchange="checkboxChanged(\'' + image_name + '\', \'' + i + '\', \'scratched\')" name="check_' + image_name + '"><label class="check_label" for="check_' + image_name + '" >with scratches</label>'
                        checkbox_2.innerHTML = '<input type="checkbox" class="checkbox hd"  id="check_hd_' + image_name + '" disabled onchange="checkboxChanged(\'' + image_name + '\', \'' + i + '\', \'hd\')" name="check_hd_' + image_name + '"><label class="check_label" for="check_hd_' + image_name + '" >is HD</label>'

                        image.onclick = function () {
                            let enlarged = $("#enlarged");
                            enlarged.html("<img src='" + image.src + "' height='80%' style='margin: 10px;'>")
                            enlarged.removeClass('hidden_tag')
                            enlarged.click(function () {
                                enlarged.addClass('hidden_tag')
                            })
                        }
                        image_div.appendChild(image);
                        image_div.appendChild(checkbox_1);
                        image_div.appendChild(checkbox_2);
                        // add the image element to the selected images div
                        $("#selected-images").append(image_div);
                    };


                    // read the selected file as a data URL
                    reader.readAsDataURL(files[i]);
                }
            }


            /* UPLOAD FILES AND START TO PROCESS THEM */
            document.getElementById('image-form').addEventListener('submit', (event) => {
                event.preventDefault();
                const fileNames = [];
                const formData = new FormData();
                const files = fileList  // event.target.elements.image.files;
                console.log('files: ', files)
                for (let i = 0; i < files.length; i++) {
                    const fileName = files[i].name;

                    const scratched = scratched_images[i] !== '' ? 'true' : 'false';
                    const hd = hd_images[i] !== '' ? 'true' : 'false';
                    fileNames.push({'name':fileName, 'scratched':scratched, 'hd':hd});
                    formData.append('base', files[i]);
                    formData.append('scratched', scratched);
                    formData.append('hd', hd);

                }
                // select the landing element by ID
                const input_section = $("#input-section");
                console.log(formData)
                // replace the landing element with the new input section
                input_section.replaceWith(loading_div);

                const loading = $("#loader");
                const messages = ['Loading...', 'Please wait...', 'Almost done...', 'Hang tight...', 'Wow, how big it is!', 'Oh my goodness!', 'what a tremendous size it has!'];
                // Get a reference to the loading text field
                const loading_text = document.getElementById('loading-text');
                // Start an interval to change the text every 10 seconds
                let index = 0;
                setInterval(() => {
                    loading_text.value = messages[index];
                    index = (index + 1) % messages.length;
                }, 5000);
                fetch(`${protocol}://${host}:8000/upload/image/`, {
                    method: 'POST',
                    headers: {
                        'X-User-Id': user_id,
                        'Access-Control-Allow-Origin': '*'
                    },
                    body: formData,
                    timeout: 65000 // timeout in milliseconds
                }).then(response => {
                    if (response.ok) {
                        console.log('Image uploaded successfully');
                        return response.json()
                    } else {
                        console.error('Error uploading image');
                    }
                }).then(data => {
                    // console.log(data)
                    loading.replaceWith(output_section);
                    const output_images = $("#output-images");
                    // Create an array to store the file names from data['images']
                    const dataImageNames = data["images"].map(fileName => {
                        const file_name = fileName.split("\\").pop();
                        const name = file_name.split(".")[0];
                        // const ext = file_name.split(".")[1];
                        return name;
                    });
                    console.log(dataImageNames)
                    console.log(fileNames)
                    // Loop through fileNames and check if each file is present in dataImageNames
                    for (let i = 0; i < fileNames.length; i++) {
                        const fileName = fileNames[i].name;
                        const is_scratch = fileNames[i].scratched;
                        const is_hd = fileNames[i].hd;
                        const type = is_hd === 'true' ? '_hd_' : is_scratch === 'true' ? '_scratch_' : '_';
                        console.log('fileName: ', fileName, 'is_scratch: ', is_scratch, 'is_hd: ', is_hd)
                        const input_extension = fileName.split(".")[1];
                        console.log('input_extension: ', input_extension)
                        const ext = 'png';
                        const name = fileName.split(".")[0];
                        if (!dataImageNames.includes(name)) {
                            const folder_name = 'input'+type+'images/'

                            const container = document.createElement("div");
                            container.classList.add("unavailable_container");
                            container.style.position = "relative";
                            container.style.display = "inline-block";
                            container.style.height = "200px";
                            container.style.margin = "10px";

                            const input_image = document.createElement("img");
                            input_image.src = DJANGO_MEDIA_URL + user_id + '/' + folder_name + fileName;
                            input_image.style.filter = "grayscale(100%)";
                            input_image.style.height = "100%";

                            const textOverlay = document.createElement("div");
                            textOverlay.innerHTML = "This image is too big, try to upload a smaller version!";
                            textOverlay.classList.add("unavailable_text");
                            textOverlay.style.position = "absolute";
                            textOverlay.style.bottom = "0";
                            textOverlay.style.left = "0";
                            textOverlay.style.width = "100%";
                            textOverlay.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
                            textOverlay.style.color = "white";
                            textOverlay.style.padding = "10px";

                            container.append(input_image);
                            container.append(textOverlay);
                            output_images.append(container);
                        } else {
                            // Image is present in data['images'], assign it to output_strips
                            const output_strips = document.createElement("div");
                            output_strips.classList.add("output_strips");

                            const input_image = document.createElement("img");
                            const output_image = document.createElement("img");
                            const paragon_image = document.createElement("img");

                            // const name = fileName.split(".")[0];
                            input_image.src = DJANGO_MEDIA_URL + user_id + '/' + name + '_input.' + ext;
                            output_image.src = DJANGO_MEDIA_URL + user_id + '/' + name + '_output.' + ext;
                            paragon_image.src = DJANGO_MEDIA_URL + user_id + '/' + name + '_paragon.' + ext;

                            output_image.height = input_image.height = paragon_image.height = 200;

                            output_strips.onclick = function () {
                                let enlarged = $("#enlarged");
                                enlarged.html("<img src='" + input_image.src + "' class='enlarged-image'>" +
                                    "<img src='" + paragon_image.src + "' class='enlarged-image'>" +
                                    "<img src='" + output_image.src + "' class='enlarged-image'>");

                                enlarge_images();
                                enlarged.removeClass('hidden_tag');
                                enlarged.click(function () {
                                    enlarged.addClass('hidden_tag');
                                });
                            };

                            output_strips.append(input_image);
                            output_strips.append(paragon_image);
                            output_strips.append(output_image);
                            output_images.append(output_strips);
                        }
                    }

                    // for (let i = 0; i < data["images"].length; i++) {
                    //     const file_name = data["images"][i].split("\\").pop()
                    //     const name = file_name.split(".")[0]
                    //     const ext = file_name.split(".")[1]
                    //     const input_image = document.createElement("img");
                    //     const output_image = document.createElement("img");
                    //     const paragon_image = document.createElement("img");
                    //     // console.log('django media url: ', DJANGO_MEDIA_URL)
                    //     output_image.src = DJANGO_MEDIA_URL + user_id + '/' + name + '_output.' + ext;
                    //     input_image.src = DJANGO_MEDIA_URL + user_id + '/' + name + '_input.' + ext;
                    //     paragon_image.src = DJANGO_MEDIA_URL + user_id + '/' + name + '_paragon.' + ext;
                    //     output_image.height = input_image.height = paragon_image.height = 200;
                    //
                    //     const output_strips = document.createElement("div");
                    //     output_strips.classList.add("output_strips");
                    //     output_strips.onclick = function () {
                    //         let enlarged = $("#enlarged");
                    //         enlarged.html("<img src='" + input_image.src + "' class='enlarged-image'>" +
                    //             "<img src='" + paragon_image.src + "' class='enlarged-image'>" +
                    //             "<img src='" + output_image.src + "' class='enlarged-image'>")
                    //
                    //         enlarge_images()
                    //         enlarged.removeClass('hidden_tag')
                    //         enlarged.click(function () {
                    //             enlarged.addClass('hidden_tag')
                    //         })
                    //     }
                    //     // output_strips.style = "display:flex;flex-wrap:wrap;justify-content:center;margin: 10px;"
                    //     output_strips.append(input_image);
                    //     output_strips.append(paragon_image);
                    //     output_strips.append(output_image);
                    //     output_images.append(output_strips);
                    // }
                    const download_button = document.getElementById("download_button");
                    const restart_button = document.getElementById("restart_button");
                    download_button.addEventListener("click", function () {
                        downloadAllImages(user_id, protocol, host);
                    });
                    restart_button.addEventListener("click", function () {
                        //delete temp folder
                        fetch(`${protocol}://${host}:8000/delete/folder/`, {
                            method: 'DELETE',
                            headers: {
                                'X-User-Id': user_id,
                                'Access-Control-Allow-Origin': '*'
                            },
                        })
                            .then(response => {
                                location.reload();
                            })
                            .catch(error => {
                                console.error(error);
                            });
                    })

                }).catch(error => {
                    console.error('Error uploading image', error);
                });
            });

        });

    });
    window.addEventListener('beforeunload', function (event) {
        //delete temp folder
        fetch(`${protocol}://${host}:8000/delete/folder/`, {
            method: 'DELETE',
            headers: {
                'X-User-Id': user_id,
                'Access-Control-Allow-Origin': '*'
            },
            keepalive: true,
        })
            .then(response => {
                location.reload();
            })
            .catch(error => {
                console.error(error);
            });

    });

});

function downloadImage(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = 'images/' + filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

async function downloadAllImages(user, protocol, host) {
    const images = document.querySelectorAll("#output-images img");
    const downloadPromises = [];
    for (let i = 0; i < images.length; i++) {
        const url = images[i].src;
        const filename = url.split("/").pop();
        if (filename.includes('output')) {
            downloadPromises.push(downloadImage(url, filename));
        }
    }
    await fetch(`${protocol}://${host}:8000/delete/folder/`, {
        method: 'DELETE',
        headers: {
            'X-User-Id': user_id,
            'Access-Control-Allow-Origin': '*'
        },
    })
        .then(response => {
            console.log(response);
        })
        .catch(error => {
            console.error(error);
        });
    location.reload();
}

function checkboxChanged(file_name, number, which) {
    // Check if 'scratched' checkbox is selected
    const scratchedCheckbox = document.getElementById(`check_${file_name}`);
    const scratchedChecked = scratchedCheckbox.checked;

    // Activate 'hd' checkbox if 'scratched' is selected
    const hdCheckbox = document.getElementById(`check_hd_${file_name}`);
    if (scratchedChecked) {
        hdCheckbox.disabled = false;
    } else {
        hdCheckbox.disabled = true;
        hdCheckbox.checked = false;
    }
    if (which === 'scratched') {
        if (scratched_images.indexOf(file_name) !== -1) {
            scratched_images[number] = ''
            console.log('removed: ', scratched_images)
        } else {
            scratched_images[number] = file_name
            console.log('added: ', scratched_images)
        }
    } else if (which === 'hd') {
        if (hd_images.indexOf(file_name) !== -1) {
            hd_images[number] = ''
            console.log('removed: ', hd_images)
        } else {
            hd_images[number] = file_name
            console.log('added: ', hd_images)
        }
    }
}

async function enlarge_images() {
    // Get the width and height of the #enlarged div
    const enlargedDiv = document.querySelector('#enlarged');
    const enlargedWidth = enlargedDiv.offsetWidth;
    const enlargedHeight = enlargedDiv.offsetHeight;
    // Get the dimensions of each image and find the largest one
    const images = document.querySelectorAll('.enlarged-image');
    let largestWidth = 0;
    let largestHeight = 0;
    let width = 0;
    let height = 0;
    await imageDimensions(images[0].src).then(dimensions => {
        width = dimensions.width
        height = dimensions.height

        if (width > largestWidth) {
            largestWidth = width;
        }

        if (height > largestHeight) {
            largestHeight = height;
        }

        // Calculate the maximum size for the three images
        const maxWidth = (enlargedWidth - 20) / 3;
        const maxHeight = enlargedHeight - 20;

        // Determine the width and height for each image
        let imageWidth = largestWidth;
        let imageHeight = largestHeight;

        if (imageWidth > maxWidth) {
            imageWidth = maxWidth;
            imageHeight = (largestHeight / largestWidth) * maxWidth;
        }

        if (imageHeight > maxHeight) {
            imageHeight = maxHeight;
            imageWidth = (largestWidth / largestHeight) * maxHeight;
        }
        // Set the width and height for each image
        images.forEach(image => {
            image.style.width = imageWidth + 'px';
            image.style.height = imageHeight + 'px';
        });
    })
}

// helper to get dimensions of an image
const imageDimensions = file =>
    new Promise((resolve, reject) => {
        const img = new Image()

        // the following handler will fire after a successful loading of the image
        img.onload = () => {
            const {naturalWidth: width, naturalHeight: height} = img
            resolve({width, height})
        }

        // and this handler will fire if there was an error with the image (like if it's not really an image or a corrupted one)
        img.onerror = () => {
            reject('There was some problem with the image.')
        }

        img.src = file
    })


