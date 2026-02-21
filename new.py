import os
from huggingface_hub import InferenceClient

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

completion = client.chat.completions.create(
    model="HuggingFaceH4/zephyr-7b-beta",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(completion.choices[0].message)
