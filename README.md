# OKE 애플리케이션 배포 자동화

Oracle Cloud Infrastructure (OCI)의 Oracle Kubernetes Engine (OKE) 클러스터에 핵심 애플리케이션들을 자동으로 배포하는 Pulumi 프로젝트입니다.

## 📋 개요

이 프로젝트는 [pulumi-python-oke-full](https://github.com/flexyzwork/pulumi-python-oke-multi-infrastructure) 레포지토리의 infrastructure(pulumi계정/oke-infrastructure/prod) 스택으로 생성된 OKE 클러스터 위에 필수 애플리케이션들을 배포합니다.

### ✅ 제공하는 기능

- **Cert Manager**: Let's Encrypt를 통한 SSL/TLS 인증서 자동 발급 및 갱신
- **Ingress NGINX**: HTTP/HTTPS 트래픽 라우팅 및 로드밸런싱
- **멀티 환경 지원**: 개발(se), 프로덕션(os) 환경 분리

### ❌ 제공하지 않는 것

- OCI 기본 인프라 구조 (VCN, 서브넷, 보안 그룹 등)
- OKE 클러스터 자체의 생성 및 관리
- 데이터베이스, 스토리지 등 백엔드 서비스
- 애플리케이션별 세부 설정 (직접 커스터마이징 필요)

## 🛠 사전 요구사항

### 1. 기본 인프라 구축
먼저 OKE 클러스터가 생성되어 있어야 합니다:

```bash
# 기본 인프라 레포지토리 클론 및 배포
git clone https://github.com/flexyzwork/pulumi-python-oke-multi-infrastructure
cd pulumi-python-oke-multi-infrastructure
# 해당 레포지토리의 README 따라 OKE 클러스터 생성
```

### 2. 필수 도구 설치

```bash
# Pulumi CLI 설치
curl -fsSL https://get.pulumi.com | sh

# kubectl 설치 (macOS)
brew install kubectl

# kubectl 설치 (Linux)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# OCI CLI 설치 및 구성
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
oci setup config
```

### 3. Kubeconfig 설정
OKE 클러스터의 kubeconfig는 `~/.kube/config-<region>` 에 저장 되어 있음

```bash
# 컨텍스트 전환
export KUBECONFIG=~/.kube/config-se
kubectl get nodes

export KUBECONFIG=~/.kube/config-os
kubectl get nodes
```

## 🚀 설치 및 배포

### 1. 프로젝트 클론

```bash
git clone https://github.com/flexyzwork/pulumi-python-oke-multi-kubernetes
cd pulumi-python-oke-multi-kubernetes
```

### 2. Python 환경 설정
```bash
# 개발 환경 설정
make install
```

### 3. Pulumi 스택 설정

현재 설정에서 **17번째 줄의 스택 참조를 확인하고 수정**하세요:

```python
# __main__.py 17번째 줄
infra_stack = StackReference('pulumi계정/oci-infrastructure/prod')
```

사용 중인 실제 스택 이름으로 변경:

```bash
# 현재 사용 가능한 스택 목록 확인
pulumi stack ls -a

# 출력 예시:
# NAME                                  LAST UPDATE     RESOURCE COUNT
# flexyzwork/oci-infrastructure/infra     6 minutes ago   41
```

### 4. 스택 초기화 및 배포

```bash
# 새 스택 생성 (환경별로 각각 생성)
pulumi stack init k8s

# 설정 미리보기
make preview

# 배포 실행
make up
```

## 📁 프로젝트 구조

```
.
├── __main__.py                    # 메인 Pulumi 프로그램
├── cert_manager/                  # Cert Manager 관련 설정
│   ├── cert_manager.py           # Cert Manager 배포 로직
│   ├── cluster-issuer-prod.yaml  # 프로덕션 인증서 발급자
│   └── cluster-issuer-staging.yaml # 스테이징 인증서 발급자
├── ingress/                       # Ingress NGINX 관련 설정
│   ├── ingress_nginx_manager.py   # Ingress 배포 로직
│   └── *.yaml                     # Ingress 설정 파일들
└── utils/                         # 유틸리티 함수들
    ├── logger.py                  # 로깅 설정
    └── exception_handler.py       # 예외 처리
```

## 🔧 환경별 설정

### 개발 환경 (se)
```bash
export KUBECONFIG=~/.kube/kube-se
pulumi stack select dev
pulumi up
```

### 프로덕션 환경 (os)
```bash
export KUBECONFIG=~/.kube/kube-os
pulumi stack select prod
pulumi up
```

## 🔍 배포 후 확인

### 1. 파드 상태 확인
```bash
kubectl get pods -A
```

### 2. Cert Manager 인증서 상태
```bash
kubectl get certificates.cert-manager.io -A
```

### 3. Ingress 상태 확인
```bash
kubectl get ingress -A
```

## 🚨 문제 해결

### Cert Manager 인증서 문제
인증서가 `False` 상태일 경우:

```bash
# 문제가 있는 인증서 삭제 후 재생성
kubectl delete certificates.cert-manager.io <certificate-name> -n <namespace>
```

## 🔄 백업 및 모니터링

### CloudCasa 백업 설정
```bash
# 각 환경별 백업 에이전트 설치
kubectl apply -f https://api.cloudcasa.io/kubeclusteragents/[AGENT_TOKEN].yaml
```

## ⚠️ 주의사항

1. **스택 참조 확인**: `__main__.py`의 17번째 줄 스택 참조가 정확한지 확인
2. **kubeconfig 경로**: 각 환경의 kubeconfig 파일 경로가 올바른지 확인
3. **네트워크 정책**: OCI 보안 그룹에서 필요한 포트가 열려있는지 확인
4. **도메인 설정**: 인증서 발급을 위한 도메인 DNS 설정 필요
5. **리소스 한계**: OCI 계정의 리소스 한계 확인

## 📞 지원

문제가 발생하거나 추가 도움이 필요한 경우:

1. 이슈 트래커에 문제 보고
2. 로그 파일 (`app.log`) 확인
3. Pulumi 콘솔에서 배포 상태 확인

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
