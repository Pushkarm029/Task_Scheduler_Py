#!/bin/bash

folders=("createjob" "deletejob" "updatejob" "readjob")

password=$(kubectl get secret --namespace default my-release-mariadb -o jsonpath="{.data.mariadb-root-password}" | base64 -d)
# echo $password

for folder in "${folders[@]}"
do
    filePath="$folder/values.yaml"
    sed -i "s/password:.*/password: \"$password\"/" $filePath
done