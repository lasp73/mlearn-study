# Executando Ray sobre Kubernetes

Podemos criar um cluster Ray de várias formas, mas aqui usaremos um cluster
Kubernetes.

## Kubernetes numa máquina local

Para executar Ray em Kubernetes numa máquina local, vamos usar o
[kind](https://kind.sigs.k8s.io/).

Instale o [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).

Instale o [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)

Instale Ray e cliente Python para Kubernetes:

```bash

pip install "ray[serve]==1.11.0"

pip install kubernetes

```

Crie o cluster Kubernetes:

```bash

kind create cluster --config kind-cluster.yaml

```

Para evitar baixar várias vezes a imagem Docker do Ray, vamos baixá-la
primeiro no host e carregá-la no worker do kubernetes pelo kind através do
comando `kind load docker-image`.

```bash

docker pull rayproject/ray:1.11.0-py38-cpu

kind load docker-image rayproject/ray:1.11.0-py38-cpu --nodes kind-worker

```

Verifique as imagens Docker carregadas no nodes do k8s:

```bash
docker exec kind-worker crictl images
```

```bash
$ docker exec kind-worker crictl images

IMAGE                                      TAG                  IMAGE ID            SIZE
docker.io/kindest/kindnetd                 v20210326-1e038dc5   6de166512aa22       54MB
docker.io/rancher/local-path-provisioner   v0.0.14              e422121c9c5f9       13.4MB
docker.io/rayproject/ray                   1.11.0-py38-cpu      b07e8bb5b5801       2.71GB
k8s.gcr.io/build-image/debian-base         v2.1.0               c7c6c86897b63       21.1MB
k8s.gcr.io/coredns/coredns                 v1.8.0               296a6d5035e2d       12.9MB
k8s.gcr.io/etcd                            3.4.13-0             0369cf4303ffd       86.7MB
k8s.gcr.io/kube-apiserver                  v1.21.1              94ffe308aeff9       127MB
k8s.gcr.io/kube-controller-manager         v1.21.1              96a295389d472       121MB
k8s.gcr.io/kube-proxy                      v1.21.1              0e124fb3c695b       133MB
k8s.gcr.io/kube-scheduler                  v1.21.1              1248d2d503d37       51.9MB
k8s.gcr.io/pause                           3.5                  ed210e3e4a5ba       301kB
```

Crie o cluster Ray:

```bash

ray up -y --no-config-cache ray-cluster.yaml

```

Inicialmente, tive um erro relacionado ao Object Store, mas usei `--object-store-memory=134217728` no comando
`ray start` de `ray-cluster.yaml`, alocando 128Mi para Object Store.

```bash
Traceback (most recent call last):
  File "/home/ray/anaconda3/bin/ray", line 8, in <module>
    sys.exit(main())
  File "/home/ray/anaconda3/lib/python3.7/site-packages/ray/scripts/scripts.py", line 1958, in main
    return cli()
  File "/home/ray/anaconda3/lib/python3.7/site-packages/click/core.py", line 1128, in __call__
    return self.main(*args, **kwargs)
  File "/home/ray/anaconda3/lib/python3.7/site-packages/click/core.py", line 1053, in main
    rv = self.invoke(ctx)
  File "/home/ray/anaconda3/lib/python3.7/site-packages/click/core.py", line 1659, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/home/ray/anaconda3/lib/python3.7/site-packages/click/core.py", line 1395, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/home/ray/anaconda3/lib/python3.7/site-packages/click/core.py", line 754, in invoke
    return __callback(*args, **kwargs)
  File "/home/ray/anaconda3/lib/python3.7/site-packages/ray/autoscaler/_private/cli_logger.py", line 808, in wrapper
    return f(*args, **kwargs)
  File "/home/ray/anaconda3/lib/python3.7/site-packages/ray/scripts/scripts.py", line 622, in start
    ray_params, head=True, shutdown_at_exit=block, spawn_reaper=block)
  File "/home/ray/anaconda3/lib/python3.7/site-packages/ray/node.py", line 274, in __init__
    self.start_ray_processes()
  File "/home/ray/anaconda3/lib/python3.7/site-packages/ray/node.py", line 1117, in start_ray_processes
    huge_pages=self._ray_params.huge_pages
  File "/home/ray/anaconda3/lib/python3.7/site-packages/ray/_private/services.py", line 1945, in determine_plasma_store_config
    ray_constants.OBJECT_STORE_MINIMUM_MEMORY_BYTES))
ValueError: Attempting to cap object store memory usage at 65523302 bytes, but the minimum allowed is 78643200 bytes.

Setup command `kubectl -n ray exec -it study-ray-head-kfr49 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (export RAY_OVERRIDE_RESOURCES='"'"'{"CPU":1,"GPU":0,"memory":375809638}'"'"';ulimit -n 65536; ray start --head --port=6379 --autoscaling-config=~/ray_bootstrap_config.yaml --dashboard-host 0.0.0.0)'` failed with exit code 1. stderr:
```

O resultado obtido deve ser algo assim:

```bash
$ ray up -y --no-config-cache ray-cluster.yaml

Cluster: study

2022-05-06 18:54:07,343	INFO util.py:278 -- setting max workers for head node type to 0
Checking Kubernetes environment settings
2022-05-06 18:54:07,756	INFO config.py:224 -- KubernetesNodeProvider: namespace 'ray' not found, attempting to create it
2022-05-06 18:54:07,777	INFO config.py:228 -- KubernetesNodeProvider: successfully created namespace 'ray'
2022-05-06 18:54:07,904	INFO config.py:345 -- KubernetesNodeProvider: service 'study-ray-head' not found, attempting to create it
2022-05-06 18:54:08,296	INFO config.py:347 -- KubernetesNodeProvider: successfully created service 'study-ray-head'
2022-05-06 18:54:08,602	INFO config.py:253 -- KubernetesNodeProvider: autoscaler_service_account 'autoscaler' not found, attempting to create it
2022-05-06 18:54:08,869	INFO config.py:255 -- KubernetesNodeProvider: successfully created autoscaler_service_account 'autoscaler'
2022-05-06 18:54:08,960	INFO config.py:279 -- KubernetesNodeProvider: autoscaler_role 'autoscaler' not found, attempting to create it
2022-05-06 18:54:09,046	INFO config.py:281 -- KubernetesNodeProvider: successfully created autoscaler_role 'autoscaler'
2022-05-06 18:54:09,049	INFO config.py:312 -- KubernetesNodeProvider: autoscaler_role_binding 'autoscaler' not found, attempting to create it
2022-05-06 18:54:09,053	INFO config.py:314 -- KubernetesNodeProvider: successfully created autoscaler_role_binding 'autoscaler'
No head node found. Launching a new cluster. Confirm [y/N]: y [automatic, due to --yes]

Acquiring an up-to-date head node
2022-05-06 18:54:09,080	INFO node_provider.py:141 -- KubernetesNodeProvider: calling create_namespaced_pod (count=1).
  Launched a new head node
  Fetching the new head node

<1/1> Setting up head node
  Prepared bootstrap config
2022-05-06 18:54:09,458	INFO node_provider.py:108 -- KubernetesNodeProvider: Caught a 409 error while setting node tags. Retrying...
  New status: waiting-for-ssh
  [1/7] Waiting for SSH to become available
    Running `uptime` as a test.
2022-05-06 18:54:10,261	INFO command_runner.py:172 -- NodeUpdater: study-ray-head-bzqf5: Running kubectl -n ray exec -it study-ray-head-bzqf5 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (uptime)'
error: unable to upgrade connection: container not found ("ray-node")
    SSH still not available (Exit Status 1): kubectl -n ray exec -it study-ray-head-bzqf5 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (uptime)', retrying in 5 seconds.
2022-05-06 18:54:41,753	INFO command_runner.py:172 -- NodeUpdater: study-ray-head-bzqf5: Running kubectl -n ray exec -it study-ray-head-bzqf5 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (uptime)'
 14:54:42 up  9:49,  0 users,  load average: 1.49, 1.35, 1.17
    Success.
  Updating cluster configuration. [hash=28ac53f5ada8823e34b95820979c3c29566381da]
  New status: syncing-files
  [2/7] Processing file mounts
2022-05-06 18:54:42,824	INFO command_runner.py:172 -- NodeUpdater: study-ray-head-bzqf5: Running kubectl -n ray exec -it study-ray-head-bzqf5 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (mkdir -p ~)'
  [3/7] No worker file mounts to sync
  New status: setting-up
  [4/7] No initialization commands to run.
  [5/7] Initalizing command runner
  [6/7] No setup commands to run.
  [7/7] Starting the Ray runtime
2022-05-06 18:54:43,981	INFO command_runner.py:172 -- NodeUpdater: study-ray-head-bzqf5: Running kubectl -n ray exec -it study-ray-head-bzqf5 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (export RAY_OVERRIDE_RESOURCES='"'"'{"CPU":1,"GPU":0,"memory":375809638}'"'"';ray stop)'
Did not find any active Ray processes.
2022-05-06 18:54:45,818	INFO command_runner.py:172 -- NodeUpdater: study-ray-head-bzqf5: Running kubectl -n ray exec -it study-ray-head-bzqf5 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (export RAY_OVERRIDE_RESOURCES='"'"'{"CPU":1,"GPU":0,"memory":375809638}'"'"';ulimit -n 65536; ray start --head --object-store-memory=134217728 --port=6379 --autoscaling-config=~/ray_bootstrap_config.yaml --dashboard-host 0.0.0.0)'
Local node IP: 10.244.1.5
2022-05-06 14:54:50,566	INFO services.py:1412 -- View the Ray dashboard at http://10.244.1.5:8265

--------------------
Ray runtime started.
--------------------

Next steps
  To connect to this Ray runtime from another node, run
    ray start --address='10.244.1.5:6379' --redis-password='5241590000000000'

  Alternatively, use the following Python code:
    import ray
    ray.init(address='auto', _redis_password='5241590000000000')

  To connect to this Ray runtime from outside of the cluster, for example to
  connect to a remote cluster from your laptop directly, use the following
  Python code:
    import ray
    ray.init(address='ray://<head_node_ip_address>:10001')

  If connection fails, check your firewall settings and network configuration.

  To terminate the Ray runtime, run
    ray stop
  New status: up-to-date

Useful commands
  Monitor autoscaling with
    ray exec ray-cluster.yaml 'tail -n 100 -f /tmp/ray/session_latest/logs/monitor*'
  Connect to a terminal on the cluster head:
    ray attach ray-cluster.yaml
  Get a remote shell to the cluster manually:
    kubectl -n ray exec -it study-ray-head-bzqf5 -- bash
```

Examine os pods existentes:

```bash
$ kubectl -n ray get pods

NAME                             READY   STATUS    RESTARTS   AGE
study-ray-head-rg2m8     1/1     Running   0          74s
study-ray-worker-g2674   1/1     Running   0          51s
```

Para acessar o Ray através do service do Kubernetes, incluindo o dashboard, faça um port-forward:

```bash
kubectl -n ray port-forward service/study-ray-head 8265 8000 10001
```

Há diferentes formas de executar código.

Local:

```bash
RAY_ADDRESS="ray://127.0.0.1:10001" python myapp.py
```

No cluster:

```bash
ray submit ray-cluster.yaml myapp.py
```

Execute o código a seguir para criar um deployment (Ray Serve):

```bash
ray submit ray-cluster.yaml start-serve.py
```

Esse deployment pode ser acionado, executando o cliente no cluster:

```bash
ray submit ray-cluster.yaml run-client.py
```

Ou executando na máquina local:

```bash
RAY_ADDRESS="ray://127.0.0.1:10001" python run-client.py
```

## Removendo o cluster

```bash
ray down -y ray-cluster.yaml

kind delete cluster
```
