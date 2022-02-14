# Hypervolt EV Charger Exporter
Prometheus Exporter for Hypervolt EV Charger

## Summary

This exporter is currently undergoing live testing to ensure stability. It must be considered BETA only.
Once the code has been tested a docker container will be provided for ease of use. For the time being, you have to build your own.

## Deployment

To deploy this to your local environment, we have to build and deploy a local container. In this example, we will work from the home folder.

```
mkdir ~/git && cd ~/git
git clone --depth=1 https://github.com/stupid3ish/hypervolt_exporter.git
cd hypervolt_exporter
docker build -t hypervolt-exporter .

```

## Example Docker Run

To manually start a docker container using the above built image, we can run a single Docker CLI command:

```
docker run -p 8080:8080 --name hypervolt-exporter -d hypervolt-exporter:latest \
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
    image: hypervolt-exporter
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
