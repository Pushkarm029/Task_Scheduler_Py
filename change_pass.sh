#!/bin/bash

folders=("createjob" "deletejob" "updatejob" "readjob")

password=$(kubectl get secret --namespace default my-release-mariadb -o jsonpath="{.data.mariadb-root-password}" | base64 -d)

for folder in "${folders[@]}"
do
    filePath="$folder/values.yaml"
    sed -i "s/mariadbRootPassword:.*/mariadbRootPassword: $password/" $filePath
done