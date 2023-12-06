from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import os  # Add the missing import
import re
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# Initialize the model only once when the server starts
model_id = "stabilityai/stable-diffusion-2"
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# Initialize the zephyr model for text generation
zephyr_pipe = pipeline("text-generation", model="HuggingFaceH4/zephyr-7b-beta", torch_dtype=torch.bfloat16, device_map="auto")

# Set the directory where images will be saved
image_dir = "../client/src/generated_images"
os.makedirs(image_dir, exist_ok=True)

# Stablediffusion API route
@app.route("/stablediffusion", methods=["POST"])
def stablediffusion():
    if request.method == "POST":
        # Get the input prompt from the frontend
        data = request.get_json()

        # Check if the 'prompt' key is present in the received JSON data
        if 'prompt' in data:
            prompt = data['prompt']

            if not prompt.endswith('.') and not prompt.endswith('?') and not prompt.endswith('!'):
                prompt += '.'

              # Additional text about adding 2 sentences in the story
            additional_text = "Continue the story with 2 short sentences with a maximum of 10 words each."

            # Define system and user messages for zephyr
            messages = [
                {"role": "system", "content": "You are a storyteller for fictional stories"},
                {"role": "user", "content": f"{prompt} {additional_text}"},
            ]

            # Apply chat template to format messages for zephyr
            prompt_zephyr = zephyr_pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

            # Generate additional text with zephyr
            generated_text = zephyr_pipe(prompt_zephyr, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)[0]["generated_text"]
           # Remove any text that includes and is before the "</s>" token
            generated_text = generated_text.split("<|assistant|>")[-1]
            generated_text = re.sub(r'\n\d*', ' ', generated_text)
            generated_text = re.sub(r'[^A-Za-z0-9.,!?\'"\s]+', '', generated_text)
            print(generated_text)

             # Combine user input and AI-generated text into a list of sentences
            combined_text = f"{prompt} {generated_text}"

            # Split the combined text into sentences based on "."
            sentences = combined_text.split(".")
            print(sentences)

            # Process each sentence and generate an image
            image_responses = []
            for i, sentence in enumerate(sentences):
                # Skip empty sentences
                if sentence.strip() and len(sentence) > 1:
                     # Check if the sentence contains a numerical value (e.g., '\n1')
                    cleaned_sentence = sentence.replace(" ", "_")
                    # Call stablediffusion and save the resulting image
                    image = pipe(sentence).images[0]
                    image_path = os.path.join(image_dir, f"{cleaned_sentence}_V2.png")
                    print("Saving image to:", image_path)
                    image.save(image_path)
                    # Append the image path to the response
                    image_responses.append({"sentence": sentence, "image_path": f"{cleaned_sentence}_V2.png"})

            # Return a list of generated image paths
            return jsonify({"image_responses": image_responses})
        else:
            return jsonify({"error": "Missing 'prompt' key in the JSON data"}), 400
    else:
        return jsonify({"error": "Only POST requests are allowed for this endpoint"}), 405
    

if __name__ == "__main__":
    app.run(debug=False)
