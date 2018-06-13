from os import path
import yaml
from kubernetes import client, config

NAMESPACE = "default"

def create_deployment_object(name, imageName, replicaCount):
    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image=imageName,
        ports=[client.V1ContainerPort(container_port=80)])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=replicaCount,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    return deployment

# Create deployement
def create_deployment(name, namespace, imageName, replicaCount):
    api_instance = client.ExtensionsV1beta1Api()
    deployment = create_deployment_object(name, imageName, replicaCount)
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=namespace)
    print("Deployment created. status='%s'" % str(api_response.status))
    return api_response.status

# get deployement
def get_deployment_list():
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.list_namespaced_deployment(
        namespace=NAMESPACE)
    print("Deployment List='%s'" % str(api_response))
    return api_response.items


def update_deployment(name, imageName, replicaCount):
    # Update container image
    api_instance = client.ExtensionsV1beta1Api()
    deployment = api_instance.read_namespaced_deployment(name=name,
        namespace=NAMESPACE)
    deployment.spec.template.spec.containers[0].image = imageName
    deployment.spec.replicas = replicaCount

    # Update the deployment
    api_response = api_instance.patch_namespaced_deployment(
        name=name,
        namespace=NAMESPACE,
        body=deployment)
    print("Deployment updated. status='%s'" % str(api_response.status))
    return api_response.status


# Delete deployment
def delete_deployment(name):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.delete_namespaced_deployment(
        name=name,
        namespace=NAMESPACE,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Deployment deleted. status='%s'" % str(api_response.status))
    return api_response.status


def init():
    config.load_kube_config()
    return

def main():
    config.load_kube_config()
    create_deployment("hack-test-deployment", "nginx:1.9.1" , 2)
    update_deployment("hack-test-deployment", "nginx:1.9.1" , 3)
    get_deployment_list()
    delete_deployment("hack-test-deployment")

if __name__ == '__main__':
    main()