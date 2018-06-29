deploy:
	source $(branch).env && envsubst < serverless.yml.template > serverless.yml && serverless deploy
