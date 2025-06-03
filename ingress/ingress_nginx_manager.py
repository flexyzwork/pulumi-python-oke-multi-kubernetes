import pulumi
from pulumi_kubernetes.helm.v3 import Release, RepositoryOptsArgs

from utils.exception_handler import apply_exception_handler
from utils.logger import global_logger

logger = global_logger


@apply_exception_handler
class IngressNginxManager(pulumi.ComponentResource):
    def __init__(self, name: str, compartment_id, public_ip_address, opts: pulumi.ResourceOptions):
        super().__init__('custom:network:IngressNginx', name, {}, opts)
        self.compartment_id = compartment_id
        self.public_ip_address = public_ip_address
        self.opts = opts
        self.name = name

    def create_ingress_nginx(self):
        ingress_nginx_release = Release(
            self.name,
            chart='ingress-nginx',
            version='4.11.2',
            namespace='ingress-nginx',
            repository_opts=RepositoryOptsArgs(repo='https://kubernetes.github.io/ingress-nginx'),
            create_namespace=True,
            name='ingress-nginx',
            timeout=1200,
            values={
                'controller': {
                    'service': {
                        'annotations': {
                            'oci.oraclecloud.com/load-balancer-type': 'nlb',
                            'oci-network-load-balancer.oraclecloud.com/security-list-management-mode': 'All',
                            'oci.oraclecloud.com/health-checks-protocol': 'TCP',
                        },
                        'externalTrafficPolicy': 'Local',
                        'loadBalancerIP': self.public_ip_address,
                    }
                }
            },
            opts=pulumi.ResourceOptions.merge(
                self.opts,
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create='20m')),
            ),
        )
        return ingress_nginx_release
