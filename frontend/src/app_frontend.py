import gradio as gr
import requests

def check_health(msg):
    resp = requests.get("http://localhost:8000/health")
    return resp.json()

chat_app = gr.Interface(
    fn = check_health,
    inputs=["text"],
    outputs=["text"],
    title = "Health",
)

chat_app.launch()