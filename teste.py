import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
import numpy as np

load_dotenv()
client = OpenAI(
    # If environment variables are not configured, replace the following line with: api_key="sk-xxx" using Model Studio API Key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

#  Base64 encoding format
def encode_video(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode("utf-8")


base64_video = encode_video("downloads/videos/3.mp4")

completion = client.chat.completions.create(
    model="qwen2.5-omni-7b",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": f"data:;base64,{base64_video}"},
                },
                {"type": "text", "text": "What is she singing"},
            ],
        },
    ],
    # Set the output data modality, currently supports two types: ["text","audio"], ["text"]
    modalities=["text"],
    audio={"voice": "Chelsie", "format": "wav"},
    # stream must be set to True, otherwise an error will occur
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)