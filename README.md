# Hypervolt EV Charger Exporter 
Prometheus Exporter for Hypervolt EV Charger

![Build Status](https://dev.azure.com/stupid3ish/hypervolt_exporter/_apis/build/status/stupid3ish.hypervolt_exporter?branchName=master)

## Summary

This exporter has been written to pull the available API data provided by Hypervolt, translate and make available as a Prometheus target.
It has been compiled into a Docker image for ease of use, currently only available in amd64 platform.


## Example Docker Run

To manually start a docker container using the above built image, we can run a single Docker CLI command:

```
docker run -p 8080:8080 --name hypervolt-exporter -d stupid3ish.azurecr.io/hypervolt-exporter:latest \
-e USERNAME='name@email.com' \
-e PASSWORD='password'
```

This will start the container with standard settings.

## Example Docker Compose

Using a docker-compose file allows for easy replication of deployment:

```
version: '3'
services:
  hypervolt-exporter:
    image: stupid3ish.azurecr.io/hypervolt-exporter:latest
    restart: always
    environment:
        - HV_USERNAME=name@email.com
        - HV_PASSWORD=password
        - REFRESH_INTERVAL=60
        - LOG_LEVEL=DEBUG
    ports:
        - 8080:8080
```

The above sample also includes additional configuration variables for tuning/debug.

## Example Prometheus Job

In order to scrape using Prometheus, you will need to set up a new job, pointing to the exporter.

```
...
- job_name: 'hypervolt'
    metrics_path: /metrics
    scrape_interval: 30s
    scrape_timeout: 30s
    static_configs:
      - targets:
        - hypervolt-exporter:8080
...
```