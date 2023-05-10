# Great Bear

*Great Bear Sample App - Edge Frame Grabber*

These are sample files which complement the Great Bear documentation, found at [docs.greatbear.io](https://docs.greatbear.io)


The Edge Frame Grabber App is a *very* simple packaging of an image grabber and image uploader in a Great Bear compatible Helm Chart. The Edge Frame Grabber App is for demonstration purposes only - and is to be used with deployments with a single node per site only.

At a high level, the code needed to create the image container can be found in the `app` directory, and the Helm charts needed to deploy the app can be found in the `charts` directory. The Great Bear App metadata is provided in the file `charts/gbear/appmetadata.yaml`.
You can follow the application publishing steps in the [GreatBear documentation](https://docs.greatbear.io/docs/creating-and-publishing-applications/publish-application-package/) to publish the image uploader container image and overall GreatBear App.

> Note: If publishing a new version of this GreatBear app to your tenant remember to change the `image.repository` value in the `charts/values.yaml` file to match your GreatBear tenant name, so that the app looks in the correct location for the image uploader container image
---

## Image Grabber

The image grabber component makes use of a publically available FFmpeg docker image, and is defined in the `charts/templates/deployment.yaml` file. 

The `deployment.yaml` file templates the FFmpeg command to confgiure the RTSP input, FPS, output image size and file format, and the path to save the grabbed image to. By editing the defaults in the `charts/values.yaml` file, you can deploy and test this locally using helm (which will also deploy the image uploader component).

Currently the Image Grabber expects the following values to be injected from the `charts/values.yaml` file
- config.CAMERA_NAME: (e.g. "TEST_CAMERA")
- config.RTSP_IP: (e.g. "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4")
- config.OUTPUT_IMAGE_FORMAT ("JPEG 2000", "JPEG", "PNG")
- config.OUTPUT_SCALE (pixel width:height, e.g. "640:360")
- config.OUTPUT_FPS (e.g. "0.25")
- config.GreatBear_SITE_NAME (e.g. "TEST_SITE")
- volume.mountPath (e.g. "/cache")

---

## Image Uploader

The image uploader component uses a simple python script to look for files in a specified directory, uploads each file to an S3 bucket, and then deletes the files once they are uploaded. 

The files needed to modify, test and build the image uploader are located in the `app` directory, along with a dedicated `README.md`  

The deployment configuration of this component is also defined in the `charts/templates/deployment.yaml` file so that it can be deployed as part of the Edge Recorder app. 

Currently the Image Uploader expects the following values to be injected from the `charts/values.yaml` or `charts/cm.yaml` files
- config.AWS_S3_HOST (e.g. https://s3.eu-west-1.amazonaws.com")
- config.AWS_S3_ACCESS_KEY (e.g. AKIAVRIAM5J7SF5FDCWS")
- config.AWS_S3_SECRET_KEY (e.g. "GJ93+duPGwlfi3ZZtdf1fsrgeg3Gh")
- config.AWS_S3_BUCKET (e.g. "eti-ea-pilot-shared-data-pipeline")
- volume.mountPath (e.g. "/cache")

> Note: the `https_proxy`, `http_proxy` and `no_proxy` values allow the uploader to run behind a proxy, and are injected by the GreatBear edge operator at deployment time if they are configured

---

### Testing Locally

This app can be run and tested on a local k8s/k3s cluster with the following steps (assuming you have the `.env` file created and helm installed). 

- Build the image uploader container image locally using the command:
    ```
    docker buildx build --platform linux/amd64,linux/arm64 -t repo.greatbear.io/<your-tenant-id>/edge-frame-grabber-image-uploader:0.0.1 --push app/image-uploader
    ```
- Load the AWS_S3_SECRET_KEY environment variable from the .env file:
    ```
    source .env
    ```
- Install the app using helm, overriding some of the defaults in the `charts/values.yaml` file (by default the app will use a pubically available RTSP stream for testing, however you can also override the RTSP_IP value for local stream testing if you wish):
    ```
    helm install edge-frame-grabber charts \
        --set image.repository=edge-frame-grabber-image-uploader \
        --set image.pullPolicy=Never \
        --set config.AWS_S3_SECRET_KEY=${AWS_S3_SECRET_KEY} \
        --set config.RTSP_IP=<target-rtsp-url>
    ```

- You can check the app logs as usual with kubectl, and remove the app using:
    ```
    helm uninstall edge-frame-grabber
    ``` 

> Note: the `AWS_S3_SECRET_KEY` is not part of this repo for obvious reasons. It would be read from a `.env` file that you can create locally inside the `app` directory (see above).

---

## License

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
