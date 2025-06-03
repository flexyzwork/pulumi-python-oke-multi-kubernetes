import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Release, RepositoryOptsArgs

from utils.exception_handler import apply_exception_handler
from utils.logger import global_logger

logger = global_logger


@apply_exception_handler
class CertManager(pulumi.ComponentResource):
    def __init__(self, name: str, region: str, opts: pulumi.ResourceOptions):
        super().__init__('custom:tls:CertManager', name, {}, opts)
        self.name = name
        self.region = region
        self.opts = opts

    def create_cert_manager(self):
        logger.info('Creating cert-manager')

        # cert-manager Helm Release 설치
        cert_manager_release = Release(
            self.name,
            chart='cert-manager',
            version='1.17.2',
            namespace='cert-manager',
            repository_opts=RepositoryOptsArgs(repo='https://charts.jetstack.io'),
            name='cert-manager',
            values={'installCRDs': True},
            create_namespace=True,
            wait_for_jobs=True,
            opts=self.opts,
        )

        logger.info('Applying cluster issuers')

        # cluster-issuer-prod.yaml 적용
        k8s.yaml.ConfigFile(
            'cluster-issuer-prod',
            file='cert_manager/cluster-issuer-prod.yaml',
            resource_prefix=f'{self.region}',
            opts=pulumi.ResourceOptions.merge(self.opts, pulumi.ResourceOptions(depends_on=[cert_manager_release])),
        )

        # cluster-issuer-staging.yaml 적용
        k8s.yaml.ConfigFile(
            'cluster-issuer-staging',
            file='cert_manager/cluster-issuer-staging.yaml',
            resource_prefix=f'{self.region}',
            opts=pulumi.ResourceOptions.merge(self.opts, pulumi.ResourceOptions(depends_on=[cert_manager_release])),
        )

        return cert_manager_release
