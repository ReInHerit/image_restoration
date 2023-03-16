let selected_images = [];

$(document).ready(function() {
    const landing_section= "<div id=\"landing\">\n" +
        "            <p>This is the landing page for this webapp that does a lot of wonderful things</p>\n" +
        "            <img id=\"cover_image\" alt=\"landing image\" src=\"static/assets/images/scratch_detection.png\">\n" +
        "            <a id=\"start_button\"  class=\"square_btn\">START TO RESTORE</a>\n" +
        "        </div>"
    const input_section = "<div id=\"input-section\" \">\n" +
        "  <h1>Input Section</h1>\n" +
        "  <p>Select one or more images to process. "+
        "      <br>\n" +
        "   You can add as many images as you want, but be careful because the processing process can be very long.</p>\n" +
        "  <form id=\"image-form\">\n" +
        "      <input type=\"file\" id=\"image-input\" name=\"image\" accept=\"image/*\" multiple>\n" +
        "      <br>\n" +
        "      <div id=\"selected-images\" style='display:flex;flex-wrap:wrap;justify-content:center'></div>\n" +
        "      <br>\n" +
        "      <button type=\"submit\">Upload Image</button>\n" +
        "  </form>\n" +
        "  </div>"
    const loading_div = "<div id=\"loading-container\"><p>PROCESSING IMAGES</p></div>"

    const output_section = "<div id=\"output-section\">\n" +
        "  <h1>Output Section</h1>\n" +
        "  <p>Here you can see the results of the processing</p>\n" +
        "  <div id=\"output-images\">\n" +
        "  </div>\n" +
        "</div>"
    console.log(landing_section);
    let main_section = $("#central");

    main_section.html(landing_section);
    // select the substitute button by ID
    var substituteButton = $("#start_button");

    // add a click event listener to the substitute button
    substituteButton.click(function() {
        // select the landing element by ID
        const landing = $("#landing");

        // replace the landing element with the new input section
        landing.replaceWith(input_section);
        // add a change event listener to the file input
        $("#image-input").change(function() {
            console.log($(this))
            // get the file input element
            var input = $(this)[0];

            // get the selected files
            var files = input.files;
            console.log(files)
            let images_urls = []

            // loop through the selected files
            for (var i = 0; i < files.length; i++) {
                if (!selected_images.some(e => e.name === files[i].name)) {
                    selected_images.push(files[i])
                    // create a file reader
                    var reader = new FileReader();

                    // add a load event listener to the file reader
                    reader.onload = function (event) {
                        // create an image element
                        var image = document.createElement("img");
                        image.src = event.target.result;
                        // console.log(image.src)
                        image.height = 200;
                        image.style = "margin: 10px;"
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
                const files = event.target.elements.image.files;
                for (let i = 0; i < files.length; i++) {
                    formData.append('image', files[i]);
                }
                // select the landing element by ID
                const input_section = $("#input-section");

                // replace the landing element with the new input section
                input_section.replaceWith(loading_div);
                const loading = $("#loading-container");
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
                        console.log(data["images"][i])
                        const file_name = data["images"][i].split("\\").pop()
                        const name = file_name.split(".")[0]
                        const ext = file_name.split(".")[1]
                        const input_image = document.createElement("img");
                        const output_image = document.createElement("img");
                        const paragon_image = document.createElement("img");
                        output_image.src = DJANGO_MEDIA_URL + name + '_output.' + ext;
                        input_image.src = DJANGO_MEDIA_URL +  name + '_input.' + ext;
                        paragon_image.src = DJANGO_MEDIA_URL +  name + '_paragon.' + ext;
                        console.log(output_image.src, input_image.src)
                        output_image.height = input_image.height =paragon_image.height = 200;

                        const parallel_images = document.createElement("div");
                        parallel_images.style = "display:flex;flex-wrap:wrap;justify-content:center;margin: 10px;"
                        parallel_images.append(input_image);
                        parallel_images.append(paragon_image);
                        parallel_images.append(output_image);
                        output_images.append(parallel_images);

                    }

                }).catch(error => {
                    console.error('Error uploading image', error);
            });
        });

        });

    });


});