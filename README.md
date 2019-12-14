

# Election Analysis Repository


Contents:
- [/analysis](/analysis): Notebooks, a library, and a Docker container to run them.
    To run locally in Docker:

    ```
    # First time only
    docker pull jupyter/scipy-notebook

    docker run -it \
        -v `pwd`/analysis:/home/jovyan/ \
        -p 8888:8888 \
        jupyter/scipy-notebook
    ```

    then navigate to `localhost:8888`.
