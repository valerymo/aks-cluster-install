#!/usr/bin/python

# version: 0.1.0
# date: 13.10.20
# developed by: Valery Mogilevsky
# description: Script for AKS (Kubernetes) Cluster deployment
# Required input parameters:
#           1. Azure SubscriptionId
#           2. Number of Cluster nodes

import argparse
import logging
import re
import sys
import os
import subprocess



AZURE_STORAGE = "cloud-shell-storage1-westeurope" # move to cmd input params
AZURE_LOCATION = "westeurope" # move to cmd input params
NAMESPACE = "test1" # move to cmd input params
MAX_NODES_PER_CLUSTER = 100
INGRESS_CONTROLLER_REPLICACOUNT = 2
API_MODEL_KUBERNETES_JSON_FILE_NAME = "kubernetes.json"

ERROR_RED = "\033[1;31;40m" + "ERROR:" + "\033[0m"
INFO_RED = "\033[1;31;40m" + "INFO:" + "\033[0m"
INFO_BLUE = "\033[1;34;40m" + "INFO:" + "\033[0m"
#31 - Red, 32 - Green, 33 - Yellow, 34 - Blue.

logging.basicConfig(level=logging.INFO)  # for debugging use level=logging.DEBUG
#logging.basicConfig(level=logging.DEBUG)


def main():
    logging.debug("main")
    try:
        parser = argparse.ArgumentParser(description='This Script deploying Azure AKS (Kubernetes) Cluster')
        parser.add_argument(
            'subscription', type=str, help='Azure SubscriptionId')
        parser.add_argument(
            'nodesnum', type=int, help="Number of Kubernetes Cluster Nodes")
        args = parser.parse_args()

        inputproc = InputProcessor(args)
        clientvalidator = ClientEnvironmentValidator(args)
        clusterinst = AKSClusterInstaller(args)
        # clustertest = ClusrerValidator()
        # ingresinst = IngresInstaller()
        # microsvcinst = TestMicroservicesInstaller()

        if not inputproc.check_cluster_nodes_number():
            return

        if not clientvalidator.validate_client_environment():
            logging.info("ERROR in Client Environment Validatation")
            return

        clusterinst.install_cluster()

        logging.debug("\033[1;32;40m" + "Completed:" + "\033[0m")


    except AssertionError:
        print("ERROR: function main - Unexpected error")


class ClientPrerequisites:
    def __init__(self, args):
        logging.debug("class PrerequisitesInstaller")
        self.args = args
        self.aks_inst = AzureAKSEngineInstaller(self.args)
        self.cli = AzureCLIInstaller(self.args)
        self.helm = HelmInstaller(self.args)

    def check_client_prerequisites(self):
        logging.debug("PrerequisitesInstaller.check_client_prerequisites:")
        logging.info("Not implemented")
        pass

    def print_client_prerequisites(self):
        logging.debug("PrerequisitesInstaller.print_client_prerequisites:")
        print("Client Prerequisites:\n  Linux OS\n  Azure CLI\n  Azure AKS-Engine")
        print("Azure CLI and Azure AKS-Engine could be installed by script\n"
              "Please rerun script and select \"yes\" for installation of required prerequisite")
        pass

    def install_azure_cli(self):
        logging.debug("PrerequisitesInstaller.install_azure_cli:")
        self.cli.install_azure_cli()

    def install_aks_engine(self):
        logging.debug("PrerequisitesInstaller.install_aks_engine:")
        self.aks_inst.install_aks_engine()

    def install_helm(self):
        logging.debug("PrerequisitesInstaller.install_aks_engine:")
        self.helm.install_helm3()


class AzureCLIInstaller:
    def __init__(self, args):
        logging.debug("class AzureCLIInstaller")
        self.args = args

    def install_azure_cli(self):
        logging.debug("AzureCLIInstaller.install_azure_cli:")
        try:
            command = "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
            logging.debug("Installing Azure CLI:" + command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + "PrerequisitesInstaller.install_azure_cli - Unexpected error")


class AzureAKSEngineInstaller:
    def __init__(self, args):
        logging.debug("class AzureAKSEngineInstaller")
        self.args = args

    def install_aks_engine(self):
        logging.debug("AzureAKSEngineInstaller.install_aks_engine:")
        #There are 3 steps:
        #1  curl -o get-akse.sh https://raw.githubusercontent.com/Azure/aks-engine/master/scripts/get-akse.sh
        #2  chmod 700 get-akse.sh
        #3  ./get-akse.sh
        logging.debug("Installing Azure AKS Engine...:")
        try:
            # 1
            command = "curl -o get-akse.sh https://raw.githubusercontent.com/Azure/aks-engine/master/scripts/get-akse.sh"
            logging.debug("Get get-akse.sh :" + command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
            #2
            command = "chmod 700 get-akse.sh"
            logging.debug("chmod 700 get-akse.sh :" + command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
            #3
            command = "./get-akse.sh"
            logging.debug("./get-akse.sh :" + command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + "PrerequisitesInstaller.install_aks_engine - Unexpected error")


class ClientEnvironmentValidator:
    def __init__(self, args):
        logging.debug("class ClientEnvironmentValidator")
        self.args = args
        self.pre = ClientPrerequisites(self.args)

    def validate_client_environment(self):
        logging.debug("ClientEnvironmentValidator.validate_client_environment:")
        if self.check_operating_system() \
                and self.check_if_helm3_installed() \
                and self.check_if_aks_engine_installed() \
                and self.check_if_azure_cli_installed():
            return True
        else:
            return False

    def check_operating_system(self):
        logging.debug("ClientEnvironmentValidator.check_operating_system")
        from sys import platform
        logging.debug("platform: " + str(platform))
        if "linux" in str(platform):
            return True
        else:
            logging.info("Script is intended for Linux OS. Exiting ...")
            return False
        
    def check_if_azure_cli_installed(self):
        logging.debug("ClientEnvironmentValidator.check_if_azure_cli_installed:")
        proc = subprocess.Popen(["which az", self.args.subscription], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        #logging.debug("which az:" + str(out))
        if not "az" in str(out):
            print(INFO_BLUE + "Azure CLI is not installed on Client.")
            answer = input("Do you want install Azure CLI now? yes/no ").lower()
            if answer == "yes":
                self.pre.install_azure_cli()
            elif answer == "no":
                self.pre.print_client_prerequisites()
                return False
        return True

    def check_if_aks_engine_installed(self):
        logging.debug("ClientEnvironmentValidator.check_if_aks_engine_installed:")
        proc = subprocess.Popen(["which aks-engine", self.args.subscription], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        #logging.debug("which aks-engine:" + str(out))
        if not "aks-engine" in str(out):
            print(INFO_BLUE + "AKS-Engine is not installed on Client.")
            answer = input("Do you want install Azure AKS-Engine now? yes/no ").lower()
            if answer == "yes":
                self.pre.install_aks_engine()
            elif answer == "no":
                self.pre.print_client_prerequisites()
                return False
        return True

    def check_if_helm3_installed(self):
        logging.debug("ClientEnvironmentValidator.check_if_helm3_installed:")
        proc = subprocess.Popen(["helm version", self.args.subscription], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if not "Version:\"v3" in str(out):
            print(INFO_BLUE + "Helm3 is not installed on Client.")
            answer = input("Do you want install Helm3 now? yes/no ").lower()
            if answer == "yes":
                self.pre.install_helm()
            elif answer == "no":
                self.pre.print_client_prerequisites()
                return False
        return True




class InputProcessor:
    def __init__(self, args):
        logging.debug("class InputProcessor")
        self.args = args

    def check_cluster_nodes_number(self):
        logging.debug("InputProcessor.get_cluster_nodes_number")
        try:
            if self.args.nodesnum < 1 or self.args.nodesnum > MAX_NODES_PER_CLUSTER:
                print ("ERROR: Not valid number of Cluster nodes. Shoulld be in range from 1 to " + str(MAX_NODES_PER_CLUSTER))
                return False
            return True
        except AssertionError:
            print("ERROR: InputProcessor.get_cluster_nodes_number - Unexpected error")

    def check_subscription(self):
        logging.debug("InputProcessor.check_subscription")
        try:
            proc = subprocess.Popen(["az account list -o table |grep ", args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print ("az account list -- output:", str(out))
            if not out.find("AzureCloud"):
                print("ERROR: subscription not found")
                return False
            return True
        except AssertionError:
            print("ERROR: InputProcessor.check_subscription - Unexpected error")


class AKSClusterInstaller:
    def __init__(self, args):
        logging.debug("class AKSClusterInstaller")
        self.args = args
        self.ingress = IngressInstaller(self.args)
        self.utils = Utils(self.args)
        self.appid = ""
        self.password = ""

    def install_cluster(self):
        logging.debug("AKSClusterInstaller.install_cluster")
        logging.debug("Installing Cluster ...")
        self.create_group()
        self.create_role("Contributor")
        self.deploy_cluster()
        self.set_kubeconfig()
        self.create_namespace()
        self.install_ingress()

    def create_group(self):
        logging.debug("AKSClusterInstaller.create_group")
        command = "az group create --name " + AZURE_STORAGE + " --location " + AZURE_LOCATION
        logging.debug("command:" + command)
        self.utils.run_command(command, "AKSClusterInstaller.create_group")


    def create_role(self, role):
        logging.debug("AKSClusterInstaller.create_role")
        #command = az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/803fbfe1-411b-4055-aed5-a02de15bde2b/resourceGroups/cloud-shell-storage-westeurope"
        command = "az ad sp create-for-rbac --role=\"" + role + "\" --scopes=\"/subscriptions/" + self.args.subscription + "/resourceGroups/"+ AZURE_STORAGE +"\""
        try:
            logging.debug(command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
            list = str(out).split("\"")
            print ("after split: ", list)
            self.appid = list[3]
            self.password = list[15]
            logging.debug("\nappid: " +  self.appid + "\npassword: " + self.password)
        except AssertionError:
            print(ERROR_RED + "AKSClusterInstaller.create_role Unexpected error")

    def deploy_cluster(self):
        logging.debug("AKSClusterInstaller.deploy_cluster")
        #command = aks-engine deploy --subscription-id 803fbfe1-411b-4055-aed5-a02de15bde2b     --dns-prefix cloud-shell-storage-westeurope     --resource-group cloud-shell-storage-westeurope     --location westeurope     --api-model kubernetes.json     --client-id 630c39b3-70ff-476f-a699-195b9591ff8d     --client-secret 8ZsTAh7.aueCNRN_v5Gr7r8RNdlZWzoTZB     --set servicePrincipalProfile.clientId="630c39b3-70ff-476f-a699-195b9591ff8d"     --set servicePrincipalProfile.secret="630c39b3-70ff-476f-a699-195b9591ff8d"
        command = "aks-engine deploy --subscription-id " + self.args.subscription \
                + " --dns-prefix " + AZURE_STORAGE \
                + " --resource-group " + AZURE_STORAGE \
                + " --location " +  AZURE_LOCATION  \
                + " --api-model " + API_MODEL_KUBERNETES_JSON_FILE_NAME \
                + " --client-id " + self.appid \
                + " --client-secret " + self.password \
                + " --set servicePrincipalProfile.clientId=" + self.appid\
                + " --set servicePrincipalProfile.secret=" + self.appid
        logging.debug("command: " + command)
        self.utils.run_command(command, "AKSClusterInstaller.deploy_cluster")

    def set_kubeconfig(self):
        logging.debug("AKSClusterInstaller.set_kubeconfig")
        #command: export KUBECONFIG=/home/valerym/_output/cloud-shell-storage-westeurope/kubeconfig/kubeconfig.westeurope.json
        kubeconfig_local_path = "_output/" + AZURE_STORAGE + "/kubeconfig/" + "kubeconfig." + AZURE_LOCATION + ".json"
        command = "export KUBECONFIG=" + kubeconfig_local_path
        logging.debug("command: " + command)
        self.utils.run_command(command, "AKSClusterInstaller.set_kubeconfig")

    def create_namespace(self):
        logging.debug("AKSClusterInstaller.create_namespace")
        command = "kubectl create namespace " + NAMESPACE
        logging.debug("command: " + command)
        self.utils.run_command(command, "AKSClusterInstaller.set_kubeconfig")

    def install_ingress(self):
        logging.debug("AKSClusterInstaller.install_ingress")
        self.ingress.add_ingress_nginx_to_helm_repo()


class IngressInstaller:
    def __init__(self, args):
        logging.debug("class IngressInstaller")
        self.args = args
        self.utils = Utils(self.args)

    def install_ingress(self):
        self.add_ingress_nginx_to_helm_repo()
        self.install_ingress_controller()

    def add_ingress_nginx_to_helm_repo(self):
        logging.debug("IngressInstaller.add_ingress_nginx")
        command = "helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx"
        self.utils.run_command(command, "IngressInstaller.add_ingress_nginx")

    def install_ingress_controller(self):
        logging.debug("IngressInstaller.install_iingress_controller")
        command = "helm install nginx-ingress ingress-nginx/ingress-nginx \
                  --namespace " + NAMESPACE \
                  + " --set controller.replicaCount=" + INGRESS_CONTROLLER_REPLICACOUNT \
                  + " --set controller.nodeSelector.\"beta\.kubernetes\.io/os\"=linux \
                  --set defaultBackend.nodeSelector.\"beta\.kubernetes\.io/os\"=linux"
        self.utils.run_command(command, "IngressInstaller.install_iingress_controller")


class HelmInstaller:
    def __init__(self, args):
        logging.debug("class HelmInstaller")
        self.args = args

    def check_helm3_installation(self):
        logging.debug("HelmInstaller.check_helm3_installation")
        logging.info("Not implemented")
        pass

    def install_helm3(self):
        logging.debug("HelmInstaller.install_helm3")
        try:
            command = "curl -L https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sudo bash"
            logging.debug("Installing Helm3:" + command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + "HelmInstaller.install_helm3")


class MicroservicesInstallerTest:
    def __init__(self, args):
        logging.debug("class MicroservicesInstallerTest")
        self.args = args

    def install_services_for_cluster_test(self):
        logging.debug("MicroservicesInstallerTest.install_services_for_cluster_test")
        self.install_service_a()
        self.install_service_b()

    def install_service_a(self):
        logging.debug("MicroservicesInstallerTest.install_service_a")
        logging.info("Not implemented")
        pass

    def install_service_b(self):
        logging.debug("MicroservicesInstallerTest.install_service_b")
        logging.info("Not implemented")
        pass


class Utils:
    def __init__(self, args):
        logging.debug("class Utils")
        self.args = args
        # self.command = command
        # self.class_function_name = class_function_name

    def run_command(self,command, class_function_name ):
        logging.debug("Utils.run_command")
        logging.debug("Run command for: " + class_function_name)
        try:
            command = str(command).strip()
            logging.debug(command)
            proc = subprocess.Popen([command, self.args.subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + class_function_name + "Unexpected error")


if __name__ == "__main__":
    main()
