import ray
from ray import serve

ray.init(address="auto", namespace="serve")

my_bot = serve.get_deployment("MyBot").get_handle()

resp = ray.get(my_bot.say_hello.remote("John"))

print(resp)
