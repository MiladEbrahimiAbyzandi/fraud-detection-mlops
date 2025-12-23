from google.cloud import storage
from pathlib import Path


def upload_file_to_gcs(
    bucket_name: str,
    source_file_path: str,
    destination_blob_name: str | None = None,
):
    """
    Uploads a file to Google Cloud Storage.

    :param bucket_name: GCS bucket name
    :param source_file_path: Local file path
    :param destination_blob_name: Path in GCS (defaults to filename)
    """
    source_file_path = Path(source_file_path)

    if not source_file_path.exists():
        raise FileNotFoundError(f"{source_file_path} does not exist")

    if destination_blob_name is None:
        destination_blob_name = source_file_path.name

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    print(f"✅ Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")


if __name__ == "__main__":
    upload_file_to_gcs(
        bucket_name="my-gcs-bucket",
        source_file_path="data/report.csv",
        destination_blob_name="uploads/report.csv",
    )
