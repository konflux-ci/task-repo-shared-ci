# hello-oci-ta task

Dummy task whose purpose is to:

1. Make it easier to test the behavior of the scripts and workflows in this repo
2. Provide an example of the repo layout that the workflows expect to operate on

## Parameters
|name|description|default value|required|
|---|---|---|---|
|SOURCE_ARTIFACT|The Trusted Artifact URI pointing to the artifact with the application source code.||true|
|ociArtifactExpiresAfter|Expiration date for the trusted artifacts created in the OCI repository. An empty string means the artifacts do not expire.|""|false|
|ociStorage|The OCI repository where the Trusted Artifacts are stored.||true|

## Results
|name|description|
|---|---|
|SOURCE_ARTIFACT|The Trusted Artifact URI pointing to the artifact with the application source code.|

