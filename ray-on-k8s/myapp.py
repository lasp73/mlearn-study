import ray

ray.init("auto")

@ray.remote
def calculate(a, b):
    return a + b

res = ray.get(calculate.remote(1, 2))

print(f"RES = {res}")
