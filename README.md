# google-cloud-functions
Some Google Cloud Function tests.

## How to deploy
```bash
gcloud functions deploy hello-world --entry-point hello_get --source hello-world/ --runtime python37 --trigger-http --region <GCLOUD_REGION> --project <GCLOUD_PROJECT_ID>
gcloud functions deploy get-image --entry-point get_gcs_image --source image/ --runtime python37 --trigger-http --region <GCLOUD_REGION> --project <GCLOUD_PROJECT_ID>
gcloud functions deploy raster-profile --entry-point get_raster_profile --source raster/ --runtime python37 --trigger-http --region <GCLOUD_REGION> --project <GCLOUD_PROJECT_ID>
gcloud functions deploy register-gcs-upload --entry-point register_gcs_upload --source bigquery/ --runtime python37 --trigger-resource <GCLOUD_BUCKET> --trigger-event google.storage.object.finalize --region <GCLOUD_REGION> --project <GCLOUD_PROJECT_ID>
``` 
