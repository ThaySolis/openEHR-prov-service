# Running the service in a container

This folder contains scripts for running the service in a Docker container. There are two ways of doing it:

- Plain: using a regular Linux-based Docker image of the service.
- SCONE-based: using a SCONE-based image of the service which uses SGX.

Either way, this is a two-step process:

1. Build the image of the service. This is done by issuing the `build.sh` command.
2. Run a container with the service. This is done by issuing the `run.sh` command.

## SCONE considerations

Before trying to build and run the SCONE-based container, you must login on the SCONE Docker Image Repository. This is done by issuing the following command:

```bash
docker login registry.scontain.com:5050
```

After the image has been built, a running LAS is required in order to launch the servce. In order to launch a LAS, use the `run-las.sh` script available [here](https://github.com/ThaySolis/demographic-database/tree/main/las).
