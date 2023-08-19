import sys
import os
import asyncio
import argparse
from pytube import YouTube, Channel
from pytube.exceptions import VideoUnavailable
from moviepy.editor import *

def unique_filename(path, original_name, extension):
    counter = 1
    new_name = original_name
    while os.path.exists(os.path.join(path, f"{new_name}{extension}")):
        new_name = f"{original_name}{counter}"
        counter += 1
    return f"{new_name}{extension}"

def download_video(video_url, mode, save_path="."):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension="mp4").get_highest_resolution()
        print(f"Downloading {yt.title}")

        video_filename = unique_filename(save_path, yt.title, ".mp4")
        filename = stream.download(output_path=save_path, filename=video_filename)

        if mode == "mp3":
            video_clip = AudioFileClip(filename)
            audio_filename = unique_filename(save_path, yt.title, ".mp3")

            os.remove(filename) # remove mp4 file

            video_clip.write_audiofile(audio_filename)
            video_clip.close()

        print(f"Downloaded {yt.title}")
    except VideoUnavailable:
        print(f'Video {video_url} is unavailable')

async def download_video_async(video_url, mode, save_path="."):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, download_video, video_url, mode, save_path)

async def download_channel(channel_url, mode, save_path="."):
    channel = Channel(channel_url)
    tasks = [download_video_async(video.url, mode, save_path) for video in channel.videos]
    await asyncio.gather(*tasks)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="URL of the YouTube video or channel to download", type=str)
    parser.add_argument("-c", "--channel", help="URL of the YouTube channel to download", type=str)
    parser.add_argument('-m', "--mode", choices=["mp3", "mp4"], help="Download mode can be mp3/mp4", type=str, default="mp4")
    parser.add_argument("-p", "--path", help="Path to save the video/channel. Default is current directory.", default=".", type=str)
    args = parser.parse_args()

    if args.url:
        asyncio.run(download_video_async(args.url, args.mode, args.path))
    elif args.channel:
        asyncio.run(download_channel(args.channel, args.mode, args.path))
    else:
        print("Please provide either a video or channel URL.")
        sys.exit(1)

if __name__ == "__main__":
    main()