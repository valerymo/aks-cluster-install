#!/usr/bin/python

# version: 0.2.2
# date: 25.10.20
# developed by: Valery Mogilevsky
# description: Script for AKS (Kubernetes) Cluster deployment
# Required input parameters: -f input.json - json file with parameters definitions
# Usage example: $./deploy_aks_cluster.py  -f input.json

import argparse
import json
import logging
import subprocess
import time
import os

ERROR_RED = "\033[1;31;40m" + "ERROR:" + "\033[0m"
INFO_RED = "\033[1;31;40m" + "INFO:" + "\033[0m"
INFO_BLUE = "\033[1;34;40m" + "INFO:" + "\033[0m"
#31 - Red, 32 - Green, 33 - Yellow, 34 - Blue.

#logging.basicConfig(level=logging.INFO)  # for debugging use level=logging.DEBUG
logging.basicConfig(level=logging.DEBUG)

def main():
    logging.debug("main")
    try:
        parser = argparse.ArgumentParser(description='This Script deploying Azure AKS (Kubernetes) Cluster')
        parser.add_argument("--file", "-f", type=str, required=True, help='Json file with input parameters')
        args = parser.parse_args()
        input_file = args.file

        with open(input_file) as json_file:
            input_params = json.load(json_file)
        if not validate_params(input_params):
            logging.info("ERROR in Input parameters validation")
            return
        input_processor = InputProcessor(input_params)
        if not input_processor.check_cluster_nodes_number():
            logging.info("ERROR in InputProcessor")
            return
        client_environment_validator = ClientEnvironmentValidator(input_params)
        if not client_environment_validator.validate_client_environment():
            logging.info("ERROR in Client Environment Validation")
            return

        aks_cluster_installer = AKSClusterInstaller(input_params)
        aks_cluster_installer.install_cluster()
        logging.info("\033[1;32;40m" + "Completed:" + "\033[0m")

    except AssertionError:
        print("ERROR: function main - Unexpected error")

def validate_params(input_params):
    if ((not input_params.get('AZURE_SUBSCRIPTION_ID'))
        or (not input_params.get('NUMBER_OF_KUBERNETES_CLUSTER_NODES'))
        or (not input_params.get('NAMESPACE'))
        or (not input_params.get('RBAC_ROLE'))
        or (not input_params.get('LOCAL_TEST_INST'))
        or (not input_params.get('RESOURCE_GROUP'))
        or (not input_params.get('AZURE_LOCATION'))
        or (not input_params.get('MAX_NODES_PER_CLUSTER'))
        or (not input_params.get('INGRESS_CONTROLLER_REPLICA_COUNT'))
        or (not input_params.get('API_MODEL_KUBERNETES_JSON_FILE_NAME'))
        or (not input_params.get('APP_HELM_CHARTS_FOR_TEST'))):
        print ("Missing mandatory parameter in input file")
        print ("Expected json input file structure sample: ")
        print ("{\n" +
            "  \"AZURE_SUBSCRIPTION_ID\": \"xxxxxx\",\n" +
            "  \"NUMBER_OF_KUBERNETES_CLUSTER_NODES\": \"1\",\n" +
            "  \"NAMESPACE\": \"test1\",\n" +
            "  \"RBAC_ROLE\": \"Contributor\",\n" +
            "  \"LOCAL_TEST_INST\": \"no\",\n" +
            "  \"RESOURCE_GROUP\": \"cloud-shell-storage1-westeurope\",\n" +
            "  \"AZURE_LOCATION\": \"westeurope\",\n"+
            "  \"MAX_NODES_PER_CLUSTER\": \"100\",\n"+
            "  \"INGRESS_CONTROLLER_REPLICA_COUNT\": \"2\",\n"+
            "  \"API_MODEL_KUBERNETES_JSON_FILE_NAME\": \"kubernetes.json\",\n"+
            "  \"APP_HELM_CHARTS_FOR_TEST\": [\n"+
            "    {\"service-a\": \"service-a-0.2.0.tgz\"},\n"+
            "    {\"service-b\": \"service-b-0.2.0.tgz\"}]\n"+
       "}\n")
        return False
    else:
        return True


class ClientPrerequisites:
    def __init__(self, input_params):
        logging.debug("class PrerequisitesInstaller")
        self.input_params = input_params
        self.aks_inst = AzureAKSEngineInstaller(self.input_params)
        self.cli = AzureCLIInstaller(self.input_params)
        self.helm = HelmInstaller(self.input_params)

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
    def __init__(self, input_params):
        logging.debug("class AzureCLIInstaller")
        self.input_params = input_params

    def install_azure_cli(self):
        logging.debug("AzureCLIInstaller.install_azure_cli:")
        try:
            command = "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
            logging.debug("Installing Azure CLI:" + command)
            azure_subscription_id = self.input_params.get('AZURE_SUBSCRIPTION_ID')
            proc = subprocess.Popen([command, azure_subscription_id], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + "PrerequisitesInstaller.install_azure_cli - Unexpected error")


class AzureAKSEngineInstaller:
    def __init__(self, input_params):
        logging.debug("class AzureAKSEngineInstaller")
        self.input_params = input_params
        self.azure_subscription_id = self.input_params.get('AZURE_SUBSCRIPTION_ID')

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
            proc = subprocess.Popen([command, self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
            #2
            command = "chmod 700 get-akse.sh"
            logging.debug("chmod 700 get-akse.sh :" + command)
            proc = subprocess.Popen([command, self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
            #3
            command = "./get-akse.sh"
            logging.debug("./get-akse.sh :" + command)
            proc = subprocess.Popen([command, self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + "PrerequisitesInstaller.install_aks_engine - Unexpected error")


class ClientEnvironmentValidator:
    def __init__(self, input_params):
        logging.debug("class ClientEnvironmentValidator")
        self.input_params = input_params
        self.pre = ClientPrerequisites(self.input_params)
        self.azure_subscription_id = self.input_params.get('AZURE_SUBSCRIPTION_ID')

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
        proc = subprocess.Popen(["which az", self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
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
        proc = subprocess.Popen(["which aks-engine", self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
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
        proc = subprocess.Popen(["helm version", self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
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
    def __init__(self, input_params):
        logging.debug("class InputProcessor")
        self.input_params = input_params
        self.azure_subscription_id = self.input_params.get('AZURE_SUBSCRIPTION_ID')
        self.nodesnum = self.input_params.get('NUMBER_OF_KUBERNETES_CLUSTER_NODES')
        self.max_nodes_per_cluster = self.input_params.get('MAX_NODES_PER_CLUSTER')

    def check_cluster_nodes_number(self):
        logging.debug("InputProcessor.get_cluster_nodes_number")
        try:
            if int(self.nodesnum) < 1 or int(self.nodesnum) > int(self.max_nodes_per_cluster):
                print ("ERROR: Not valid number of Cluster nodes. Shoulld be in range from 1 to " + str(self.max_nodes_per_cluster))
                return False
            return True
        except AssertionError:
            print("ERROR: InputProcessor.get_cluster_nodes_number - Unexpected error")

    def check_subscription(self):
        logging.debug("InputProcessor.check_subscription")
        try:
            proc = subprocess.Popen(["az account list -o table |grep ", self.azure_subscription_id], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print ("az account list -- output:", str(out))
            if not out.find("AzureCloud"):
                print("ERROR: subscription not found")
                return False
            return True
        except AssertionError:
            print("ERROR: InputProcessor.check_subscription - Unexpected error")


class AKSClusterInstaller:
    def __init__(self, input_params):
        logging.debug("class AKSClusterInstaller")
        self.input_params = input_params
        self.azure_subscription = self.input_params.get('AZURE_SUBSCRIPTION_ID')
        self.resource_group = self.input_params.get('RESOURCE_GROUP')
        self.azure_location = self.input_params.get('AZURE_LOCATION')
        self.kubernetes_json_file_name = self.input_params.get('API_MODEL_KUBERNETES_JSON_FILE_NAME')
        self.namespace = self.input_params.get('NAMESPACE')
        self.local_test_inst = self.input_params.get('LOCAL_TEST_INST')
        self.role = self.input_params.get('RBAC_ROLE')


        self.ingress = IngressInstaller(self.input_params)
        self.apps = AppsInstaller(self.input_params)
        self.utils = Utils(self.input_params)
        self.appid = ""
        self.password = ""

    def install_cluster(self):
        logging.debug("AKSClusterInstaller.install_cluster")
        logging.debug("Installing Cluster ...")
        self.create_group()
        self.create_role(self.role)
        self.azure_account_list_refresh_and_wait()
        self.deploy_cluster()
        #self.set_kubeconfig()
        self.create_namespace()
        self.install_ingress()
        self.install_apps()

    def create_group(self):
        logging.debug("AKSClusterInstaller.create_group")
        command = "az group create --name " + self.resource_group + " --location " + self.azure_location
        logging.debug("command:" + command)
        self.utils.run_command(command, "AKSClusterInstaller.create_group")

    def create_role(self, role):
        logging.debug("AKSClusterInstaller.create_role")
        #command = az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/803fbfe1-411b-4055-aed5-a02de15bde2b/resourceGroups/cloud-shell-storage-westeurope"
        command = "az ad sp create-for-rbac --role=\"" + role + "\" --scopes=\"/subscriptions/" + self.azure_subscription + "/resourceGroups/" + self.resource_group + "\""
        try:
            logging.debug(command)
            proc = subprocess.Popen([command, self.azure_subscription], stdout=subprocess.PIPE, shell=True)
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
        command = "aks-engine deploy --subscription-id " + self.azure_subscription \
                + " --dns-prefix " + self.resource_group \
                + " --resource-group " + self.resource_group \
                + " --location " +  self.azure_location  \
                + " --api-model " + self.kubernetes_json_file_name \
                + " --client-id " + self.appid \
                + " --client-secret " + self.password \
                + " --set servicePrincipalProfile.clientId=" + self.appid\
                + " --set servicePrincipalProfile.secret=" + self.appid
        logging.debug("command: " + command)
        self.utils.run_command(command, "AKSClusterInstaller.deploy_cluster")

    # def set_kubeconfig(self):
    #     logging.debug("AKSClusterInstaller.set_kubeconfig")
    #     #command: export KUBECONFIG=...../_output/cloud-shell-storage-westeurope/kubeconfig/kubeconfig.westeurope.json
    #     kubeconfig_local_path = "_output/" + self.resource_group + "/kubeconfig/" + "kubeconfig." + self.azure_location + ".json"
    #     command = "export KUBECONFIG=" + kubeconfig_local_path
    #     logging.debug("command: " + command)
    #     self.utils.run_command(command, "AKSClusterInstaller.set_kubeconfig")

    def create_namespace(self):
        logging.debug("AKSClusterInstaller.create_namespace")
        command = "kubectl create namespace " + self.namespace
        logging.debug("command: " + command)
        if self.local_test_inst.lower() ==  "yes" :
            self.utils.run_command(command, "AKSClusterInstaller.create_namespace")
        else:
            self.utils.run_command_in_azure_env(command, "AKSClusterInstaller.create_namespace")

    def install_ingress(self):
        logging.debug("AKSClusterInstaller.install_ingress")
        self.ingress.install_ingress()

    def install_apps(self):
        logging.debug("AKSClusterInstaller.install_apps")
        self.apps.install_apps()

    def azure_account_list_refresh_and_wait(self):
        logging.debug("AKSClusterInstaller.azure_account_list_refresh_and_wait")
        wait_sec = 30
        logging.info("Waiting " + str(wait_sec) + " sec ...")
        for i in range(wait_sec):
            print("*",flush=True,end="")
            time.sleep(1)
        print()
        command = "az account list --refresh"
        logging.debug("command: " + command)
        self.utils.run_command(command, "AKSClusterInstaller.azure_account_list_refresh_and_wait")


class IngressInstaller:
    def __init__(self, input_params):
        logging.debug("class IngressInstaller")
        self.input_params = input_params
        self.namespace = self.input_params.get('NAMESPACE')
        self.ingress_controller_replica_count = self.input_params.get('INGRESS_CONTROLLER_REPLICA_COUNT')
        self.local_test_inst = self.input_params.get('LOCAL_TEST_INST')
        self.utils = Utils(self.input_params)

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
                  --namespace " + self.namespace \
                  + " --set controller.replicaCount=" + self.ingress_controller_replica_count \
                  + " --set controller.nodeSelector.\"beta\.kubernetes\.io/os\"=linux \
                  --set defaultBackend.nodeSelector.\"beta\.kubernetes\.io/os\"=linux"
        if self.local_test_inst.lower() ==  "yes" :
            self.utils.run_command(command, "IngressInstaller.install_ingress_controller")
        else:
            self.utils.run_command_in_azure_env(command, "IngressInstaller.install_ingress_controller")


class HelmInstaller:
    def __init__(self, input_params):
        logging.debug("class HelmInstaller")
        self.input_params = input_params
        self.azure_subscription = self.input_params.get('AZURE_SUBSCRIPTION_ID')
        self.namespace = self.input_params.get('NAMESPACE')

    def install_helm3(self):
        logging.debug("HelmInstaller.install_helm3")
        try:
            command = "curl -L https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sudo bash"
            logging.debug("Installing Helm3:" + command)
            proc = subprocess.Popen([command, self.azure_subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + "HelmInstaller.install_helm3")


class AppsInstaller:
    def __init__(self, input_params):
        logging.debug("class AppsInstaller")
        self.input_params = input_params
        self.namespace = self.input_params.get('NAMESPACE')
        self.local_test_inst = self.input_params.get('LOCAL_TEST_INST')
        self.service_a_helmchart = self.input_params.get('APP_HELM_CHARTS_FOR_TEST')[0].get('service-a')
        self.service_b_helmchart = self.input_params.get('APP_HELM_CHARTS_FOR_TEST')[1].get('service-b')
        self.utils = Utils(self.input_params)

    def install_apps(self):
        logging.debug("AppsInstaller.install_services_for_cluster_test")
        self.install_service_a()
        self.install_service_b()
        self.install_network_policy()

    def install_service_a(self):
        logging.debug("AppsInstaller.install_service_a")
        command = "helm install service-a " + self.service_a_helmchart + " --namespace " + self.namespace
        if self.local_test_inst.lower() ==  "yes" :
            self.utils.run_command(command, "AppsInstaller.install_service_a")
        else:
            self.utils.run_command_in_azure_env(command, "AppsInstaller.install_service_a")

    def install_service_b(self):
        logging.debug("AppsInstaller.install_service_b")
        command = "helm install service-b " + self.service_b_helmchart + " --namespace " + self.namespace
        if self.local_test_inst.lower() ==  "yes" :
            self.utils.run_command(command, "AppsInstaller.install_service_b")
        else:
            self.utils.run_command_in_azure_env(command, "AppsInstaller.install_service_b")

    def install_network_policy(self):
        logging.debug("IngressInstaller.install_network_policy")
        command = "kubectl apply -f network_policy.yml --namespace " + self.namespace
        if self.local_test_inst.lower() ==  "yes" :
            self.utils.run_command(command, "IngressInstaller.install_network_policy")
        else:
            self.utils.run_command_in_azure_env(command, "IngressInstaller.install_network_policy")


class Utils:
    def __init__(self, input_params):
        logging.debug("class Utils")
        self.input_params = input_params
        self.azure_subscription = self.input_params.get('AZURE_SUBSCRIPTION_ID')
        self.resource_group = self.input_params.get('RESOURCE_GROUP')
        self.azure_location = self.input_params.get('AZURE_LOCATION')

    def run_command(self,command, class_function_name ):
        logging.debug("Utils.run_command")
        logging.debug("Run command for: " + class_function_name)
        try:
            command = str(command).strip()
            logging.debug(command)
            proc = subprocess.Popen([command, self.azure_subscription], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + class_function_name + "Unexpected error")

    def run_command_in_azure_env(self,command, class_function_name ):
        logging.debug("Utils.run_command_in_azure_env")
        logging.debug("Run command for: " + class_function_name)
        try:
            my_env = os.environ.copy()
            my_env["KUBECONFIG"] = "_output/" + self.resource_group + "/kubeconfig/" + "kubeconfig." + self.azure_location + ".json"
            command = str(command).strip()
            logging.debug(command)
            proc = subprocess.Popen([command, self.azure_subscription], env=my_env, stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            print("Out: " + str(out))
        except AssertionError:
            print(ERROR_RED + class_function_name + "Unexpected error")


if __name__ == "__main__":
    main()
