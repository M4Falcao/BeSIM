from openai import OpenAI
import os
import base64


#  Base64 encoding format
def encode_video(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode("utf-8")

# Replace xxxx/test.mp4 with the absolute path of your local video
base64_video = encode_video("downloads/videos/27.mp4")
client = OpenAI(
    # If environment variables are not configured, replace the following line with: api_key="sk-xxx" using your Model Studio API Key
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)
print("Base64 video encoding completed.")
completion = client.chat.completions.create(
    model="qwen-vl-max",  
    messages=[
        {
            "role": "system",
            "content": [{"type":"text","text": "You are a helpful assistant."}]},
        {
            "role": "user",
            "content": [
                {
                    # When passing a video file directly, set the type value to video_url
                    "type": "video_url",
                    "video_url": {"url": f"data:video/mp4;base64,{base64_video}"},
                },
                {"type": "text", "text": "What scene does this video depict?"},
            ],
        }
    ],
)
print(completion.choices[0].message.content)