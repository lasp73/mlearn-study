import ray
from ray import serve

ray.init(address="auto", namespace="serve")

serve.start(detached=True)

@serve.deployment(ray_actor_options={"resources": {"WORKER": 1}})
class MyBot:
    def say_hello(self, name):
        return f"Hello {name}!!"

MyBot.deploy()
