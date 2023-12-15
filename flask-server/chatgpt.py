from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import os  # Add the missing import
import re
from diffusers import DiffusionPipeline
from transformers import pipeline
import openai 

app = Flask(__name__)
CORS(app)

# Initialize the model only once when the server starts
pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe = pipe.to("cuda:3")
openai.api_key = 'API KEY'

# Set the directory where images will be saved
image_dir = "../client/src/generated_images"
os.makedirs(image_dir, exist_ok=True)

messages = [{"role": "system", "content": "You are a storyteller."}]
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
            additional_text = "<- user sentence. Include the user sentence and then continue the story with ONLY THREE and not more than three short sentences with a maximum of 10 words each. Numerate sentences and include in the response first user sentences."
            messages.append({"role": "user", "content": f"{prompt} {additional_text}"})

            answers = openai.chat.completions.create( 
                    model="gpt-3.5-turbo", 
                    messages=messages 
                ) 
            print(answers.choices[0].message.content)

            answers = answers.choices[0].message.content
            # Split the combined text into sentences based on "."
            sentences = re.findall(r'\d+\.\s([^\n]+)', answers)
            print(sentences)
            # digital art style
            style ="concept art, digital artwork, illustrative, painterly, matte painting, highly detailed"
            # fantasy art style
            # style ="breathtaking, fantasy art, award-winning, professional, highly detailed"
            # mario game style
            # style= "Super Mario style . vibrant, cute, cartoony, fantasy, playful, reminiscent of Super Mario series"
            # rpg game style
            #style= "role playing fiction game art asset"
            #testin style
            #style="stained glass"
            # Process each sentence and generate an image
            image_responses = []
            for i, sentence in enumerate(sentences):
                # Skip empty sentences
                if sentence.strip() and len(sentence) > 1:
                    cleaned_sentence = sentence.replace(" ", "_")
                    # Call stablediffusion and save the resulting image
                    image_with_style=f"{style} {sentence}"
                    image = pipe(image_with_style).images[0]
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
