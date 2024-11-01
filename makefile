setup:
	pipenv install --dev
update:
	pipenv update --dev
deploy:
	gcloud functions deploy gcal-shift-parser --entry-point main --runtime python311 --trigger-resource gcal-shift-parser-update-schedule --trigger-location us-east1 --trigger-event google.pubsub.topic.publish --timeout 540s 
