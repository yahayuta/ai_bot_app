import os
import io

from PIL import Image  # type: ignore # Image processing
from stability_sdk import client  # type: ignore # Stability AI SDK client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation  # type: ignore # Protocol buffer definitions

# Get the Stability API key from environment variables
STABILITY_KEY = os.environ.get('STABILITY_KEY', '')

# generate image by stability api
def generate(prompt, image_path):
    """
    Generate an image using the Stability AI API based on the given prompt.
    Args:
        prompt (str): The text prompt to generate the image from.
        image_path (str): The file path to save the generated image.
    Returns:
        None. Saves the image to the specified path.
    """
    # Initialize the Stability API client
    stability_api = client.StabilityInference(key=STABILITY_KEY, verbose=True)
    # Generate image(s) from the prompt
    answers = stability_api.generate(prompt=prompt)
    for resp in answers:
        for artifact in resp.artifacts:
            # Check if the response was filtered (e.g., NSFW content)
            if artifact.finish_reason == generation.FILTER:
                print("NSFW")
            # If the artifact is an image, save it to the specified path
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(image_path)
                