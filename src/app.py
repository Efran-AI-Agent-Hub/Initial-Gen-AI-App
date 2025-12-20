from ollama import chat
from ollama import ChatResponse

model = "gemma3:4b"
message = {"role": "user", "content": "What is 17 × 23?"}


def main(stream_flag):
    response: ChatResponse = chat(model=model, messages=[message], stream=stream_flag)

    if stream_flag:
        in_thinking = False
        content = ""
        thinking = ""

        stream: ChatResponse = response

        for chunk in stream:
            if chunk.message.thinking:
                if not in_thinking:
                    in_thinking = True
                    print("Thinking:\n", end="", flush=True)
                print(chunk.message.thinking, end="", flush=True)
                # accumulate the partial thinking
                thinking += chunk.message.thinking
            elif chunk.message.content:
                if in_thinking:
                    in_thinking = False
                    print("\n\nAnswer:\n", end="", flush=True)
                print(chunk.message.content, end="", flush=True)
                # accumulate the partial content
                content += chunk.message.content

            # append the accumulated fields to the messages for the next request
            new_message = [{"role": "assistant", thinking: thinking, content: content}]

    else:
        print("RESPONSE:")
        print(response)

        print("MESSAGE:")
        print(response["message"])

        print("CONTENT:")
        print(response["message"]["content"])


if __name__ == "__main__":
    stream_flag = True
    main(stream_flag=stream_flag)
