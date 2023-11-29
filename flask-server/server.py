from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import os  # Add the missing import
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

app = Flask(__name__)
CORS(app)

# Initialize the model only once when the server starts
model_id = "stabilityai/stable-diffusion-2"
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# Set the directory where images will be saved
image_dir = "C:/Users/danie/Desktop/university_master/tool app/client/src/generated_images"
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

            # Split the input prompt into sentences based on "."
            sentences = prompt.split(".")

            # Process each sentence and generate an image
            image_responses = []
            for i, sentence in enumerate(sentences):
                # Skip empty sentences
                if sentence.strip():
                    # Replace spaces with underscores in the sentence to create a valid filename
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
