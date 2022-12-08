import time

def retry_on_empty_result():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            return_value = func(request, *args, **kwargs)
            if return_value.data.get("count") == 0:
                request.query_params._mutable = True
                request.query_params.pop("lng", None)
                request.query_params.pop("lat", None)
                request.query_params._mutable = False
                return_value = func(request, *args, **kwargs)
            return return_value
        return wrapper
    return decorator

def time_func():
    def decorator(func):
        def wrapper(*args, **kwargs):
            t0 = time.time()
            return_value = func(*args, **kwargs)
            t1 = time.time()
            total = t1 - t0
            print(f"{func.func.__name__} ran for {total}")
            return return_value
        return wrapper
    return decorator
