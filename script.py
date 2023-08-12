from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
import cv2
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import subprocess
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def has_audio(file_path: str) -> bool:
    """
    Check if a video file has an audio stream using ffprobe.
    """
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-select_streams", "a", 
        "-show_entries", "stream=codec_type", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "audio" in result.stdout.decode()


@app.get("/")
def read_root():
    return Response(content=open("index.html", "r").read(), media_type="text/html")

@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(None)):
    if audio:
        unique_id = str(uuid.uuid4())
        audio_file_name = f"static/audio_{unique_id}.mp3"
        with open(audio_file_name, "wb") as f:
            f.write(await audio.read())
        return JSONResponse({"message": "Audio uploaded successfully", "unique_id": unique_id})
    else:
        return JSONResponse({"message": "No audio uploaded"})

@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...), videoNumber: int = Form(...)):
    unique_id = str(uuid.uuid4())
    width = 426
    height = 720
    video_files = []
    print(len(files), "TOTAL FILES")

    for file in files:
        temp_file_name = f"static/temp_{unique_id}_{file.filename}"
        with open(temp_file_name, "wb") as f:
            f.write(await file.read())

        resized_file_name = f"static/resized_{unique_id}_{file.filename}"
        
        if file.filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
            # Convert webp to png first if it's a webp image
            if file.filename.endswith(".webp"):
                png_filename = temp_file_name.replace(".webp", ".png")
                subprocess.run(["ffmpeg", "-i", temp_file_name, png_filename])
                temp_file_name = png_filename

            # Convert image to a video of 30 seconds
            print("Converting image to video", temp_file_name)
            resized_file_name = resized_file_name.replace(".png", ".mp4").replace(".jpg", ".mp4").replace(".jpeg", ".mp4").replace(".webp", ".mp4")
            subprocess.run([
                "ffmpeg", "-framerate", "1/30", "-loop", "1", "-i", temp_file_name, "-c:v", "libx264", 
                "-preset", "ultrafast", "-t", "30", "-pix_fmt", "yuv420p", "-crf", "28", 
                resized_file_name
            ])
            print("Image converted to video", resized_file_name)
        else:
            subprocess.run([
                "ffmpeg", "-i", temp_file_name, "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
                "-s", "hd720",  # Limit the video quality to 720p
                resized_file_name
            ])
            # Check if the video has an audio stream. If not, add a silent audio.
            if not has_audio(resized_file_name):
                silent_video_name = f"static/silent_{unique_id}_{file.filename}"
                subprocess.run([
                    "ffmpeg", "-f", "lavfi", "-i", "anullsrc", "-i", resized_file_name, 
                    "-c:v", "copy", "-c:a", "aac", "-shortest", silent_video_name
                ])
                video_files.append(silent_video_name)
                continue
        
        video_files.append(resized_file_name)

    # concatenate videos into one
    list_file = f"static/list_{unique_id}.txt"
    with open(list_file, "w") as f:
        for video_file in video_files:
            f.write(f"file '{os.path.join(os.getcwd(), video_file)}'\n")

    # concatenate videos into one
    final_clip_name = f"static/video_{unique_id}_{videoNumber}.mp4"
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", final_clip_name])
    os.remove(list_file)  # remove the list file
    
    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(final_clip_name)
    success, frame = video_capture.read()
    if success:
        thumbnail_path = f"static/thumbnail_{unique_id}_{videoNumber}.jpg"
        cv2.imwrite(thumbnail_path, frame)
    else:
        thumbnail_path = None
    print("Thumbnail path", thumbnail_path)
    print("Video ID", unique_id)
    return JSONResponse({"message": "Videos uploaded successfully", "imagePath": thumbnail_path, "unique_id": unique_id})
    unique_id = str(uuid.uuid4())
    width = 426
    height = 720
    video_files = []
    print(len(files), "TOTAL FILES")

    for file in files:
        temp_file_name = f"static/temp_{unique_id}_{file.filename}"
        with open(temp_file_name, "wb") as f:
            f.write(await file.read())

        resized_file_name = f"static/resized_{unique_id}_{file.filename}"
        
        if file.filename.endswith(".jpg") or file.filename.endswith(".jpeg") or file.filename.endswith(".png"):
            # Convert image to a video of 30 seconds
            print("Converting image to video", temp_file_name)
            resized_file_name = resized_file_name.replace(".png", ".mp4").replace(".jpg", ".mp4").replace(".jpeg", ".mp4")
            subprocess.run([
                "ffmpeg", "-framerate", "1/30", "-loop", "1", "-i", temp_file_name, "-c:v", "libx264", 
                "-preset", "ultrafast", "-t", "30", "-pix_fmt", "yuv420p", "-crf", "28", 
                resized_file_name
            ])
            print("Image converted to video", resized_file_name)
        else:
            subprocess.run([
                "ffmpeg", "-i", temp_file_name, "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
                "-s", "hd720",  # Limit the video quality to 720p
                resized_file_name
            ])
            # Check if the video has an audio stream. If not, add a silent audio.
            if not has_audio(resized_file_name):
                silent_video_name = f"static/silent_{unique_id}_{file.filename}"
                subprocess.run([
                    "ffmpeg", "-f", "lavfi", "-i", "anullsrc", "-i", resized_file_name, 
                    "-c:v", "copy", "-c:a", "aac", "-shortest", silent_video_name
                ])
                video_files.append(silent_video_name)
                continue
        
        video_files.append(resized_file_name)

    # concatenate videos into one
    list_file = f"static/list_{unique_id}.txt"
    with open(list_file, "w") as f:
        for video_file in video_files:
            f.write(f"file '{os.path.join(os.getcwd(), video_file)}'\n")

    # concatenate videos into one
    final_clip_name = f"static/video_{unique_id}_{videoNumber}.mp4"
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", final_clip_name])
    os.remove(list_file)  # remove the list file
    
    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(final_clip_name)
    success, frame = video_capture.read()
    if success:
        thumbnail_path = f"static/thumbnail_{unique_id}_{videoNumber}.jpg"
        cv2.imwrite(thumbnail_path, frame)
    else:
        thumbnail_path = None
    print("Thumbnail path", thumbnail_path)
    print("Video ID", unique_id)
    return JSONResponse({"message": "Videos uploaded successfully", "imagePath": thumbnail_path, "unique_id": unique_id})

@app.get("/combine/{unique_ids}/{audio_id}")
async def combine_videos(unique_ids: str, audio_id: str = None):
    for file in os.listdir("static"):
        if file.startswith("test_"):
            os.remove(os.path.join("static", file))

    unique_ids = unique_ids.split(",")
    videos = [f"static/video_{unique_id}_{i+1}.mp4" for i, unique_id in enumerate(unique_ids)]
    width = 426
    height = 720
    unique_id = str(uuid.uuid4())
    video_filters = []
    audio_filters = []
    ffmpeg_command = ["ffmpeg"]

    for i, video in enumerate(videos):
        ffmpeg_command.extend(["-i", video])
        video_filters.append(f"[{i}:v]scale={width}:{height},pad=426:720:(426-iw)/2:(720-ih)/2:black[v{i}]")

        if has_audio(video):
            audio_filters.append(f"[{i}:a]anull[a{i}]")
        else:
            print("Adding silent audio:", i)
            audio_filters.append(f"aevalsrc=0:d=30[a{i}]")

    # Fill up to 3 with black videos and silent audio
    for i in range(len(videos), 3):
        video_filters.append(f"color=black:s=426x720:d=30[v{i}]")
        audio_filters.append(f"aevalsrc=0:d=30[a{i}]")

    # Combine video and audio filters
    video_filters.append(f'{"[" + "][".join([f"v{i}" for i in range(3)])}]hstack=inputs=3[v]')
    audio_filters.append(f'{"[" + "][".join([f"a{i}" for i in range(3)])}]amix=inputs=3[a]')

    print("Video Filters:", video_filters)  # Debug print
    print("Audio Filters:", audio_filters)  # Debug print

    filter_complex = '; '.join(video_filters + audio_filters)
    print("Filter Complex:", filter_complex)  # Debug print

    ffmpeg_command.extend(["-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]", "-b:v", "1000k", "-preset", "ultrafast", "-t", "30", "-r", "24", f"static/test_{unique_id}.mp4"])
    print(" ".join(ffmpeg_command))  # Debug print
    subprocess.run(ffmpeg_command)

    # remove all the temporary files
    for video in videos:
        os.remove(video)
    
    for file in os.listdir("static"):
        if file.startswith("video_") or file.startswith("resized_") or file.startswith("temp_") or file.startswith("thumbnail_") or file.startswith("audio_"):
            os.remove(os.path.join("static", file))
    
    return FileResponse(f"static/test_{unique_id}.mp4", media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
