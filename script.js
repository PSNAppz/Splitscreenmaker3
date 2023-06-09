// Function to handle file upload for a specific video
function handleFileUpload(videoNumber) {
  var fileInput = document.getElementById('fileInput' + videoNumber);

  fileInput.onchange = function () {
    var file = fileInput.files[0];
    var fileURL = URL.createObjectURL(file);

    var videoPlayer = document.getElementById('videoPlayer' + videoNumber);
    var videoThumbnail = document.getElementById('videoThumbnail' + videoNumber);

    videoPlayer.style.display = 'none';
    videoThumbnail.style.display = 'block';
    videoThumbnail.style.width = '100%'; // Set the width to 450 pixels
    videoThumbnail.style.height = '100%'; // Set the height to 540 pixels
    videoThumbnail.src = ''; // Clear the previous thumbnail
    videoThumbnail.alt = ''; // Clear the alt text

    var formData = new FormData();
    formData.append('file', file);
    formData.append('videoNumber', videoNumber); // Add the videoNumber to the formData

    fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        console.log(data.message); // Display the message

        if (data.imagePath) {
          // Add a cache-busting parameter to the image URL
          var imageURL = data.imagePath + '?' + new Date().getTime();
          videoThumbnail.src = imageURL;
        } else {
          videoThumbnail.style.display = 'none'; // Hide the image tag if no thumbnail available
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  fileInput.click();
}

// Function to handle file upload for video 1
function uploadFile(videoNumber) {
  var fileInput = document.getElementById('fileInput' + videoNumber);
  fileInput.onchange = function () {
    handleFileUpload(videoNumber);
  };
  fileInput.click();
}

// Function to handle file upload for video 2 and video 3
function chooseFile(videoNumber) {
  var fileInput = document.getElementById('fileInput' + videoNumber);
  fileInput.onchange = function () {
    handleFileUpload(videoNumber);
  };
  fileInput.click();
}

// Add event listeners to the file input elements when the page is loaded
document.addEventListener("DOMContentLoaded", function() {
  var fileInputs = document.querySelectorAll("input[type='file']");
  fileInputs.forEach(function(fileInput) {
    fileInput.addEventListener('change', function() {
      var videoNumber = this.id.replace("fileInput", "");
      handleFileUpload(videoNumber);
    });
  });
});
