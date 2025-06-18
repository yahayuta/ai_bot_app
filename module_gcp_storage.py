from google.cloud import storage

# Uploads a file to the Google Cloud Storage bucket
def upload_to_bucket(blob_name, file_path, bucket_name):
    """
    Upload a file to a specified Google Cloud Storage bucket and make it publicly accessible.
    Args:
        blob_name (str): The name to assign to the file (blob) in the bucket.
        file_path (str): The local path to the file to upload.
        bucket_name (str): The name of the target GCP bucket.
    Returns:
        str: The public URL of the uploaded file.
    """
    # Create a Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob and upload the file's content
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    # Make the blob publicly viewable
    blob.make_public()

    # Return the public URL of the uploaded file
    return blob.public_url
