// Declare a global array variable to store the uploaded video files
var uploadedVideos = [];

// Function to handle file upload for a specific video
function handleFileUpload(videoNumber) {
  console.log("runs");

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
    // Set placeholder image
    videoThumbnail.src = 'load.png';

    
    var formData = new FormData();
    formData.append('file', file);
    formData.append('videoNumber', videoNumber); // Add the videoNumber to the formData

    console.log("data23")

    fetch('http://107.23.246.78/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        console.log("asdasd", data.message); // Display the message
        console.log("DSADAS", data.imagePath);

        if (data.imagePath) {
          // Set the thumbnail image source to the base64 data
          var videoThumbnail = document.getElementById('videoThumbnail' + videoNumber);
          console.log("DSADAS", data.imagePath);
          videoThumbnail.src = 'data:image/jpeg;base64,' + data.imagePath;
          videoThumbnail.style.display = 'block';
          videoThumbnail.style.width = '100%'; // Set the width to 450 pixels
          videoThumbnail.style.height = '100%'; // Set the height to 540 pixels
        } else {
          // Hide the image tag if no thumbnail available
          var videoThumbnail = document.getElementById('videoThumbnail' + videoNumber);
          videoThumbnail.style.display = 'none';
        }

        // Add the uploaded file to the array
        uploadedVideos[videoNumber - 1] = data.filePath;
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
  fileInput.value = '';
}

// Function to handle file upload for video 2 and video 3
function chooseFile(videoNumber) {
  var fileInput = document.getElementById('fileInput' + videoNumber);
  fileInput.onchange = function () {
    handleFileUpload(videoNumber);
  };
  fileInput.click();
}

function handleAudioUpload() {

  console.log("runsauido")
  var audioInput = document.getElementById('audioInput');
  var audioFile = audioInput.files[0];

  var formData = new FormData();
  formData.append('file', audioFile);

}



function uploadAudio() {
  var audioInput = document.getElementById('audioInput');

  audioInput.onchange = function () {
    handleAudioUpload();
  };
  audioInput.click();
  audioInput.value = ''; // Reset the value of the audio input
}
// Add event listeners to the file input elements when the page is loaded
document.addEventListener("DOMContentLoaded", function () {
  var fileInputs = document.querySelectorAll("input[type='file']");
  fileInputs.forEach(function (fileInput) {
    fileInput.addEventListener('change', function () {
      var videoNumber = this.id.replace("fileInput", "");
      handleFileUpload(videoNumber);
    });
  });
});

function combine() {
  var loadedVideos = 0;
  var videosToLoad = 3; // Minimum number of videos required

  // Check if each video is loaded
  for (var i = 1; i <= 3; i++) {
    var videoThumbnail = document.getElementById('videoThumbnail' + i);
    if (videoThumbnail.src.includes('html')) {
      // Skip if the video is not loaded
      continue;
    }
    loadedVideos++;
  }

  console.log("loadedVideos", uploadedVideos.length)
  if (videosToLoad === uploadedVideos.length) {
    var loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');
    var text = ""
    // Create a new FormData object and append all uploaded videos even if multiple files are selected
    var formData = new FormData();
    for (var i = 1; i <= 3; i++) {
      var fileInput = document.getElementById('fileInput' + i);
      if (fileInput.files.length > 0) {
        // Loop through all selected files and append them
        for (var j = 0; j < fileInput.files.length; j++) {
          text += i + ","
          var file = fileInput.files[j];
          formData.append('files', file);
        }
      }

      formData.append('videoNumber', text);

    }
    // Append the audio file if available
    var audioInput = document.getElementById('audioInput');
    if (audioInput.files.length > 0) {
      var audioFile = audioInput.files[0];
      formData.append('audio', audioFile);
    }

    // Upload the videos and combine them
    fetch('http://107.23.246.78/combine', {
      method: 'POST',
      body: formData,
    })
      .then(response => {
        if (response.ok) {
          return response.blob();
        } else {
          throw new Error('Unable to combine videos');
        }
      })
      .then(blob => {
        var downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = 'combined.mp4';

        downloadLink.click();
        loadingOverlay.classList.remove('active'); // Hide the loading overlay
      })
      .catch(error => {
        console.error('Error:', error);
        loadingOverlay.classList.remove('active'); // Hide the loading overlay
      });
  } else {
    // Show a dialog box with the error message
    alert('All videos must be loaded');
  }
}