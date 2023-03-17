let selected_images = [];

$(document).ready(function () {
    const landing_section = "<div id=\"landing\">\n" +
        "            <p>This is the landing page for this webapp that does a lot of wonderful things</p>\n" +
        "            <img id=\"cover_image\" alt=\"landing image\" src=\"static/assets/images/scratch_detection.png\">\n" +
        "            <a id=\"start_button\"  class=\"square_btn\">START TO RESTORE</a>\n" +
        "        </div>"
    const input_section = "<div id=\"input-section\" \">\n" +
        "  <div id='input-description'>\n" +
        "  <h1>INPUT</h1>\n" +
        "  <p class='vertical'>You can select the images you want to load from your hard disk by browsing to the folder where they are stored. \n" +
        "      <br>\n" +
        "      You can load as many images as you want from the same folder. However, please keep in mind that the more files you select and the larger they are in size, the longer it will take for the files to be processed and loaded.\n" +
        "      <br>\n" +
        "      So, it's important to be patient while the files are being processed.</p>\n" +
        "  </div>\n" +
        "  <form id=\"image-form\">\n" +
        "      <a class=\"square_btn\" type=\"button\" onclick=\"document.getElementById('image-input').click(); return false;\"> BROWSE </a>\n" +
        "      <input type=\"file\" id=\"image-input\" name=\"image\" class='hidden_tag' accept=\"image/*\" multiple>\n" +
        "      <br>\n" +
        "      <div id=\"selected-images\" ></div>\n" +
        "      <br>\n" +
        "      <a id='submit_label' class=\"square_btn\" type=\"button\" onclick=\"document.getElementById('submit-button').click(); return false;\"> PROCESS </a>\n" +
        "      <button id='submit-button' type=\"submit\" class='hidden_tag'></button>\n" +
        "  </form>\n" +
        "       <div id='enlarged' class='hidden_tag'> </div>\n" +
        "  </div>"

    // const loading_div = "<div id=\"loading-container\"><p>PROCESSING IMAGES</p></div>"
    const loading_div = "<div id=\"loader\">\n" +
        "  <div id=\"shadow\"></div>\n" +
        "  <div id=\"box\"></div>\n" +
        "</div>"

    const output_section = "<div id=\"output-section\">\n" +
        "  <div id='output-description'>\n" +
        "       <h1>Output Section</h1>\n" +
        "       <div class='vertical'><p>Here you can see the results of the processing:" +
        "           <ul style=\"list-style-type:disc;\">\n" +
        "               <li>The first image is the original image</li>\n" +
        "               <li>The second is an image of comparison on the areas most affected by the process.</li>\n" +
        "               <li>The third image is the output image</li>\n" +
        "           </ul>\n" +
        "       </p></div>\n" +
        "  </div>\n" +
        "  <div id=\"output-images\">\n" +
        "  </div>\n" +
        "</div>\n" +
        "       <div id='enlarged' class='hidden_tag'> </div>\n" +
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
                        console.log('il file ', selected_files[i].name, ' esiste già')
                    } else {
                        // does the key already exist in files object? if yes, create a new key
                        if (Object.keys(files).some(e => Number(e) === i)) {
                            let new_key = Object.keys(files).length
                            console.log('la key del file ', selected_files[i].name, ' esiste già: ', i, ' new key: ', new_key)
                            // if ('length' in Object.keys(files)) { new_key -= 1;}
                            // else {let new_key = Object.keys(files).length}
                            console.log('lenght in',new_key)
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
                const file = new File([files[i]], files[i].name, {type: files[i].type, lastModified: files[i].lastModified});
                dataTransfer.items.add(file);
            }
            fileList = dataTransfer.files;
            console.log('fileList: ', fileList)
            // loop through the selected files
            for (let i = 0; i < fileList.length; i++) {
                console.log('file ', i, ': ', fileList[i].name)
                if (!selected_images.some(e =>
                    e.name === fileList[i].name &&
                    e.size === fileList[i].size &&
                    e.type === fileList[i].type)) {
                    console.log('file ', i, ': ', fileList[i].name, ' is not in selected_images')
                    selected_images.push(fileList[i])
                    // create a file reader
                    var reader = new FileReader();

                    // add a load event listener to the file reader
                    reader.onload = function (event) {
                        // create an image element
                        let image = document.createElement("img");
                        image.src = event.target.result;
                        image.id = fileList[i].name;
                        // console.log(image.src)
                        image.height = 200;
                        image.style = "margin: 10px;"
                        image.onclick = function () {
                            // console.log('click on image: ', image.id)
                            // console.log('click on image: ', image.src)
                            let enlarged = $("#enlarged");
                            enlarged.html("<img src='" + image.src + "' height='80%' style='margin: 10px;'>")
                            enlarged.removeClass('hidden_tag')
                            enlarged.click(function () {
                                enlarged.addClass('hidden_tag')
                            })
                        }
                        // add the image element to the selected images div
                        $("#selected-images").append(image);
                    };
                    // read the selected file as a data URL
                    reader.readAsDataURL(files[i]);
                }
            }


            /* UPLOAD FILES AND START TO PROCESS THEM */
            document.getElementById('image-form').addEventListener('submit', (event) => {
                event.preventDefault();
                const formData = new FormData();
                console.log('fileList2: ', fileList)
                // console.log('files: ', event.target.elements.image.files)
                const files = fileList  // event.target.elements.image.files;
                for (let i = 0; i < files.length; i++) {
                    formData.append('image', files[i]);
                }
                // select the landing element by ID
                const input_section = $("#input-section");

                // replace the landing element with the new input section
                input_section.replaceWith(loading_div);
                const loading = $("#loader");
                // loading.style.display = "block"
                fetch('http://127.0.0.1:5000/upload-image', {
                    method: 'POST',
                    body: formData
                }).then(response => {
                    console.log(response)
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
                    for (let i = 0; i < data["images"].length; i++) {
                        const file_name = data["images"][i].split("\\").pop()
                        const name = file_name.split(".")[0]
                        const ext = file_name.split(".")[1]
                        const input_image = document.createElement("img");
                        const output_image = document.createElement("img");
                        const paragon_image = document.createElement("img");
                        output_image.src = DJANGO_MEDIA_URL + name + '_output.' + ext;
                        input_image.src = DJANGO_MEDIA_URL + name + '_input.' + ext;
                        paragon_image.src = DJANGO_MEDIA_URL + name + '_paragon.' + ext;
                        output_image.height = input_image.height = paragon_image.height = 200;

                        const output_strips = document.createElement("div");
                        output_strips.classList.add("output_strips");
                        output_strips.onclick = function () {
                            // console.log('click on image: ', image.id)
                            // console.log('click on image: ', image.src)
                            let enlarged = $("#enlarged");
                            // for images in output_strips (input, paragon, output) add to enlarged div
                            enlarged.html("<img src='" + input_image.src + "' style='max-width: 30vw'>" +
                                          "<img src='" + paragon_image.src + "' style='max-width: 30vw'>" +
                                            "<img src='" + output_image.src + "' style='max-width: 30vw'>")


                            enlarged.removeClass('hidden_tag')
                            enlarged.click(function () {
                                enlarged.addClass('hidden_tag')
                            })
                        }
                        // output_strips.style = "display:flex;flex-wrap:wrap;justify-content:center;margin: 10px;"
                        output_strips.append(input_image);
                        output_strips.append(paragon_image);
                        output_strips.append(output_image);
                        output_images.append(output_strips);

                    }

                }).catch(error => {
                    console.error('Error uploading image', error);
                });
            });

        });

    });


});

function FileListItems(files) {
    let b = new ClipboardEvent("").clipboardData || new DataTransfer()
    for (let i = 0; i < files.length; i++) {
        b.items.add(files[i])
    }
    return b.files
}