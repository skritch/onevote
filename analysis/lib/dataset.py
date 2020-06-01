import os
import pandas as pd
import requests
import shutil


def get_csv(url, name, file_format='csv', **pd_kwargs):
    cache_filename = f'cache/{name}.{file_format}'
    if os.path.exists(cache_filename):
        print(f"Using cached file {cache_filename}")
    else:
        print(f"Cache file {cache_filename} not found, requesting {url}...")
        with requests.get(url, stream=True) as r, \
             open(cache_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return pd.read_csv(cache_filename, **pd_kwargs)
