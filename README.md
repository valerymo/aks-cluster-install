# Azure AKS Cluster Installation application

## Azure AKS Cluster Installation application
   
   deploy_aks_cluster.py 

Application could be used to install Azure AKS Cluster from any Linux clint machine.
It installing All required prerequsites on client machine:
- Azure CLI
- AKS-Angine
- Helm

This is first working version of the Python application. Tested on WSL Ubuntu.
Code - easy for understanding.
To see how to use - need just start/try it.

Usage examples:
$ deploy_aks_cluster.py SubscriptionID NodesNumber

$ ./deploy_aks_cluster.py
usage: deploy_aks_cluster.py [-h] subscription nodesnum
deploy_aks_cluster.py: error: the following arguments are required: subscription, nodesnum

$ ./deploy_aks_cluster.py --help
usage: deploy_aks_cluster.py [-h] subscription nodesnum

This Script deploying Azure AKS (Kubernetes) Cluster

positional arguments:
  subscription  Azure SubscriptionId
  nodesnum      Number of Kubernetes Cluster Nodes

optional arguments:
  -h, --help    show this help message and exit

------------------

## Microservice for test on AKS
service-a
Microservice intended for validation of Cluster environment,
but it contains also some logics.
Microservice is printing Bitcoin Price.

$ oc exec service-a-xxx -it sh
curl localhost:8080/actuator/health
{"status":"UP","groups":["liveness","readiness"]}#

curl localhost:8080/hello
{"id":2,"content":"Hello, Bitcoin!"}#

curl localhost:8080/start&

$kubectl logs service-a-xxx  
11378.163       USD   Tue Oct 13 17:46:51 UTC 2020    
11376.995       USD   Tue Oct 13 17:47:51 UTC 2020    
11376.995       USD   Tue Oct 13 17:47:51 UTC 2020    
Bitcoin average for 10 min: 11383.22   USD   Tue Oct 13 17:48:51 UTC 2020  
11381.19        USD   Tue Oct 13 17:48:51 UTC 2020  
11381.19        USD   Tue Oct 13 17:48:51 UTC 2020  
11380.465       USD   Tue Oct 13 17:49:51 UTC 2020  
11380.465       USD   Tue Oct 13 17:49:51 UTC 2020  
11381.632       USD   Tue Oct 13 17:50:52 UTC 2020  
11381.632       USD   Tue Oct 13 17:50:52 UTC 2020  

## What is planning for next versions of Cluster installation application

- Microservices will be installed automatically
- Ingress configuration will be added to installation application
- Add references to Microsoft documentation, to code, to better understanding and maintenence.
- More detailed readme file
- Split Cluster installation application to several files (?), 
	as it's long and contains 10 Classes.
	Although code is easy for understanding if using PyCharm (or similar IDE).
- Cleanup
- Move several hardcoded parameters to cmd input (see global vars in code):
