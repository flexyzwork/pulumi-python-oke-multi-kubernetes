# -*- coding: utf-8 -*-
import os

import pulumi
import pulumi_kubernetes as k8s
import pulumi_oci as oci
from pulumi import StackReference

from cert_manager.cert_manager import CertManager
from ingress import IngressNginxManager
from utils.logger import global_logger

logger = global_logger


def main():
    regions = ['os', 'se']
    infra_stack = StackReference('flexyzwork/oci-infrastructure/prod')
    for region in regions:
        logger.info(f'Processing {region}')
        compartment_id = infra_stack.get_output(f'{region}-compartment_id')
        public_ip_address = infra_stack.get_output(f'{region}-public_ip_address')
        kubeconfig_path = os.path.expanduser(f'~/.kube/config-{region}')
        k8s_provider = k8s.Provider(f'{region}-k8s-provider', kubeconfig=kubeconfig_path)
        oci_provider = oci.Provider(f'{region}-oci-provider', config_file_profile=region)

        pulumi.Output.all(region, compartment_id, public_ip_address, k8s_provider, oci_provider).apply(
            lambda args: create_ingress_nginx_release(
                args[0], args[1], args[2], pulumi.ResourceOptions(providers=[args[3], args[4]])
            )
        )


def create_ingress_nginx_release(region, compartment_id, public_ip_address, opts):
    logger.info(f'Creating Ingress Nginx release for {region}')
    ingress_nginx_manager = IngressNginxManager(
        f'{region}-ingress-nginx', compartment_id=compartment_id, public_ip_address=public_ip_address, opts=opts
    )
    ingress_nginx_release = ingress_nginx_manager.create_ingress_nginx()

    # Cert Manager 설치 (Ingress NGINX 설치 완료 후)
    cert_manager_release = pulumi.Output.all(ingress_nginx_release).apply(lambda _: install_cert_manager(region, opts))

    return cert_manager_release


def install_cert_manager(region, opts):
    logger.info(f'Installing Cert Manager for {region}')
    cert_manager = CertManager(f'{region}-cert-manager', region, opts=opts)
    return cert_manager.create_cert_manager()


if __name__ == '__main__':
    main()
