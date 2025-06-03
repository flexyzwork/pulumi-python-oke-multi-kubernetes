# rancher

```shell
# os
# 만약 아래와 같다면
k get certificates.cert-manager.io -A -w
NAMESPACE       NAME               READY   SECRET             AGE
cattle-system   rancher-prod-tls   False    rancher-prod-tls   23h

k delete  certificates.cert-manager.io rancher-prod-tls -n cattle-system


# se rancher 등록
export KUBECONFIG=~/.kube/kube-se
kubectl apply -f https://rancher.code-lab.kr/v3/import/mkjfjfsf7tlf88ggblhxlmxt5vvwmbqw6h6rkg22zj64xtr9bkr2xq_c-m-n6g5qt67.yaml
k get pods -A -w



```


# Cloud Casa
https://cloudcasa.io

```shell
# os (ID: 66fce8aeb87b9778a87b5672)
kubectl apply -f https://api.cloudcasa.io/kubeclusteragents/z9WVDQuWKjnnTlFIinhZf4sG8acb2D350C8TRU0WsNk.yaml

# se (ID: 66fceb450670c266e2b4e549)
kubectl apply -f https://api.cloudcasa.io/kubeclusteragents/A45U--aOkQziVRWLg1-Ne2ZJFU2qLoMdMvAXSsGpQto.yaml



# 10/29 16시 기본 + 모니터링 + 스타트업 코어 앱(se, ch) 백업 후 아래 삭제 실행

kubectl delete namespace/cloudcasa-io clusterrolebinding/cloudcasa-io
```
