# Azure AKS Cluster Installation application

## Azure AKS Cluster Installation application
   
   deploy_aks_cluster.py 

Application could be used to install Azure AKS Cluster from any Linux client machine.
It installing All required prerequsites on client machine:
- Azure CLI
- AKS-Angine
- Helm

This is first working version of the Python application. Tested on WSL Ubuntu.
Code - easy for understanding.
To see how to use - need just start/try it.

Usage:
$ ./deploy_aks_cluster.py  -f input.json

To get help:
$./deploy_aks_cluster.py
usage: deploy_aks_cluster.py [-h] --file FILE
deploy_aks_cluster.py: error: the following arguments are required: --file/-f

$./deploy_aks_cluster.py --help
usage: deploy_aks_cluster.py [-h] --file FILE

This Script deploying Azure AKS (Kubernetes) Cluster

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Json file with input parameters

Example for input.json file:
{
  "AZURE_SUBSCRIPTION_ID": "xxxx-xxx-xxx-xxx-xxxxxx",
  "NUMBER_OF_KUBERNETES_CLUSTER_NODES": "1",
  "NAMESPACE": "test4",
  "AZURE_STORAGE": "cloud-shell-storage-westeurope",
  "AZURE_LOCATION": "westeurope",
  "MAX_NODES_PER_CLUSTER": "100",
  "INGRESS_CONTROLLER_REPLICA_COUNT": "2",
  "API_MODEL_KUBERNETES_JSON_FILE_NAME": "kubernetes.json",
  "APP_HELM_CHARTS_FOR_TEST":[
         { "service-a":"service-a.yaml"},
         { "service-b":"service-b.yaml"}]
}

------------------

## Microservice for test on AKS
service-a
Microservice intended for validation of Cluster environment,
but it contains also some logics.
Microservice is printing Bitcoin Price.

$ $ curl 192.168.1.2:32084/actuator/health
{"status":"UP","groups":["liveness","readiness"]}

$ curl 192.168.1.2:32084/hello
{"id":3,"content":"Hello, Bitcoin!"}

$ curl 192.168.1.2:30371/start&

$kubectl logs service-a-xxx  
BitcoinPrice monitoring started. Printing in USD:
. . . . . 
12847.865       USD   Wed Oct 21 17:31:12 UTC 2020
12845.417       USD   Wed Oct 21 17:32:12 UTC 2020
12847.735       USD   Wed Oct 21 17:33:13 UTC 2020
12856.878       USD   Wed Oct 21 17:34:13 UTC 2020
Bitcoin average for 10 min: 12850.277   USD   Wed Oct 21 17:35:13 UTC 2020
12854.045       USD   Wed Oct 21 17:35:13 UTC 2020
12856.537       USD   Wed Oct 21 17:36:14 UTC 2020
12855.038       USD   Wed Oct 21 17:37:14 UTC 2020
12840.455       USD   Wed Oct 21 17:38:14 UTC 2020
12837.313       USD   Wed Oct 21 17:39:15 UTC 2020
12835.948       USD   Wed Oct 21 17:40:15 UTC 2020
. . . . . 

## What is new in this version
- All parameters were moved to input file, and usage of deploy_aks_cluster.py - changed
- Microservices for test -  installed automatically, by deploy_aks_cluster.py
- Readme file updated

## What is planning for next versions of Cluster installation application
- Ingress configuration
- Add references to Microsoft documentation, to code, to better understanding and maintenence (?)
- More detailed readme file (?)
- Split Cluster installation application to several files (?), 
	as it's long and contains 10 Classes.
	Although code is easy for understanding if using PyCharm (or similar IDE).


