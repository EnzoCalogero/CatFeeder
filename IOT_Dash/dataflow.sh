#!/usr/bin/env bash

# creating
gcloud dataflow jobs run test01 --gcs-location "gs://dataflow-templates/latest/PubSub_Subscription_to_BigQuery" --staging-location="gs://enzus/temp" --parameters inputSubscription="projects/pi-iot-project-235918/subscriptions/my-sub2",outputTableSpec="pi-iot-project-235918:home.sensors"


# listing
gcloud dataflow jobs list --status=active

# from listextract the dataflow id job.
id_job=$(gcloud dataflow jobs list --status=active |sed -n -e '2,2p' |grep -Eo '^[^ ]+')

# wait for 30 minutes sec 30*60=1800
sleep 1800

# dfrain the dataflow job.
gcloud dataflow jobs drain $id_job

