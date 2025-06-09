import os
import io

from stability_sdk import client # type: ignore
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation # type: ignore
from PIL import Image # type: ignore

STABILITY_KEY = os.environ.get('STABILITY_KEY', '')

# generate image by stability api
def generate(prompt, image_path):
    stability_api = client.StabilityInference(key=STABILITY_KEY, verbose=True)
    answers = stability_api.generate(prompt=prompt)
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                print("NSFW")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(image_path)