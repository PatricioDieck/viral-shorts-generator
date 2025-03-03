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
# pprint(all_text)

# define the LLM

llm = ChatOpenAI(model='gpt-4o', 
                 temperature=0.7, 
                 max_completion_tokens=None, 
                 timeout=None, 
                 max_retries=2
                 )

# specify the prompt 

prompt = f"So, provided you use a transcript of a video, I want you to identify all the segments that are as highly relevant, useful, and can be extracted into subtopics from the video based on the transcript. We're basically creating viral reels from the transcript, and I want you to make sure that each segment is between 30 to a minute long in duration. Make sure you provide extremely accurate timestamps and respond only in the format provided. Here is the transcription.: {transcript}"

messages = [
    { "role" : "system" , "content" : f"You're a viral YouTube master, and I have a Nike 480 and are phenomenal at reading YouTube transcripts and extracting the most valuable segments from each one of them. and extracting the mosst intriguing content from the transcript. " },
    { "role" : "user" , "content" : prompt }
]

class Segment(BaseModel):
    """Represents a segment of the transcript"""
    start_time: float = Field(..., description="The start time of the segment in seconds")
    end_time: float = Field(..., description="The end time of the segment in seconds")
    text: str = Field(..., description="The text of the segment")
    title: str = Field(..., description="The youtube title of the segment to make it highly engaging and viral" )
    description: str = Field(..., description="The description of the segment to make it highly engaging and viral" )
    duration: float = Field(..., description="The duration of the segment in seconds")

class VideoTranscript(BaseModel):
    """Represents a video transcript with identified viral segments"""
    segments: List[Segment] = Field(..., description="The segments of the transcript")

structured_llm = llm.with_structured_output(VideoTranscript)

ai_response = structured_llm.invoke(messages)

pprint(ai_response)

parsed_content = ai_response.dict()['segments']

# store clips in a folder

os.makedirs("generated_clips", exist_ok=True)

segment_labels = []

video_title = safe_title
input_file = f"videos/{safe_title}.mp4"  # Fix: Use the correct input file path

for i, segment in enumerate(parsed_content):
    start_time = segment['start_time']
    end_time = segment['end_time']
    text = segment['text']
    title = segment['title']
    description = segment['description']
    duration = segment['duration']

    output_file_name = f"generated_clips/{video_title}_{str(i + 1)}.mp4"

    # Fix: Use the correct input file path in the ffmpeg command
    command = f"ffmpeg -i {input_file} -ss {start_time} -to {end_time} -c:v libx264 -c:a aac -strict experimental -b:a 192k {output_file_name}"

    subprocess.run(command, shell=True)

    segment_labels.append(f"{i + 1}. {title}, \n {description}")

    print(f"Generated clip {i + 1} of {len(parsed_content)}")

with open("generated_clips/segment_labels.txt", "w") as f:
    for label in segment_labels:
        f.write(label + "\n")

# save segments to json

with open("generated_clips/segments.json", "w") as f:
    json.dump(parsed_content, f, indent=4)





    
    






