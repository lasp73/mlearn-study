# Executando Ray sobre Kubernetes

Podemos criar um cluster Ray de várias formas, mas aqui usaremos um cluster
Kubernetes.

## Kubernetes numa máquina local

Para executar Ray em Kubernetes numa máquina local, vamos usar o
[kind](https://kind.sigs.k8s.io/).

Para evitar carregar várias vezes a imagem Docker do Ray, vamos baixá-la
primeiro no host e carregá-la pelo kind através do comando `kind load docker-image`.

```bash

cd ray-k8s

kind create cluster --config kind-cluster.yaml

docker pull rayproject/ray:1.11.0-py38-cpu

kind load docker-image rayproject/ray:1.11.0-py38-cpu --nodes kind-worker

ray up -y --no-config-cache ray-cluster.yaml

```

Tive um erro inicialmente mas usei `--object-store-memory=134217728` no comando
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

Setup command `kubectl -n ray exec -it study-cluster-ray-head-kfr49 -- bash --login -c -i 'true && source ~/.bashrc && export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore && (export RAY_OVERRIDE_RESOURCES='"'"'{"CPU":1,"GPU":0,"memory":375809638}'"'"';ulimit -n 65536; ray start --head --port=6379 --autoscaling-config=~/ray_bootstrap_config.yaml --dashboard-host 0.0.0.0)'` failed with exit code 1. stderr:
```

Verificando as imagens carregadas no nodes do k8s:

```bash
docker exec kind-worker crictl images
```

Para acessar o dashboard através do service:

```bash
kubectl -n ray port-forward service/study-cluster-ray-head 8265:8265
```
