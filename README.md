

# Election Analysis Repository

The overall goal: to demonstrate the unfairness of US elections.

Initial plan:
- presidential elections due to electoral college VS popular
- VS better than popular?
  - might need some kind of ranked-choice polls?
- Presidential including primaries


### Contents:

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
