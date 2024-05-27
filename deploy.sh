#!/bin/bash

# Stop and remove the existing container if it exists
docker stop wealthwatch && docker rm wealthwatch

# Build the Docker image for the Dash application
docker build -t wealthwatch .

# Run the Docker container for the Dash application with restart policy
docker run -d --name wealthwatch -p 8992:8992 \
  -e WEALTHWATCH_PG_USERNAME=$WEALTHWATCH_PG_USERNAME \
  -e WEALTHWATCH_PG_PASSWORD=$WEALTHWATCH_PG_PASSWORD \
  -e WEALTHWATCH_PG_DBNAME=$WEALTHWATCH_PG_DBNAME \
  -e CURRENCY_API=$CURRENCY_API \
  --restart always wealthwatch
