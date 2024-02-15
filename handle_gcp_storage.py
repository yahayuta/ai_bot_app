from google.cloud import storage

# Delete all files from a Google Cloud Storage bucket.
def delete_bucket_files(bucket_name):
    # Create a Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # List all blobs in the bucket
    blobs = bucket.list_blobs()

    # Delete each blob in the bucket
    for blob in blobs:
        blob.delete()
        print(f"Deleted {blob.name}.")

    print(f"All files in {bucket_name} have been deleted.")

#  Uploads a file to the Google Cloud Storage bucket
def upload_to_bucket(blob_name, file_path, bucket_name):
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