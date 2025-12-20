from ollama import chat
from ollama import ChatResponse

model = 'gemma3:4b'
message = {
    "role": "user",
    "content": "What are the primary colors"
}
response: ChatResponse = chat(
    model=model,
    messages=[message]
)
print("RESPONSE:")
print(response)

print("MESSAGE:")
print(response["message"])

print("CONTENT:")
print(response["message"]["content"])