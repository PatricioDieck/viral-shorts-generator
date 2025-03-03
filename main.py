import os
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from pprint import pprint

import subprocess
import json
from typing import List

# load environment variables
from dotenv import load_dotenv
load_dotenv()


youtube_url = "https://www.youtube.com/watch?v=Z1cz3MyjlBo&ab_channel=TheTruthSeekerPodcast"

# download video 
os.makedirs("videos", exist_ok=True)

yt = YouTube(youtube_url)

video = yt.streams.filter(file_extension='mp4').first()

safe_title = yt.title.replace(' ', '-')

# Fix the download location issue
video.download(output_path="videos", filename=f"{safe_title}.mp4")

# get transcript 

video_id = yt.video_id
transcript = YouTubeTranscriptApi.get_transcript(video_id,  )


all_text = [entry['text'] for entry in transcript]
pprint(all_text)

# define the LLM

llm = ChatOpenAI(model='gpt-4o', 
                 temperature=0.7, 
                 max_completion_tokens=None, 
                 timeout=None, 
                 max_retries=2
                 )

# specify the prompt 