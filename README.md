# insights-nest

A next-generation implementation of [`insights-client`](https://github.com/RedHatInsights/insights-client/).


## Developer setup

1. Fork both this and the insights-core repository.
2. Clone both of them into the same directory.

    ```bash
    git clone git@github.com:$YOU/insights-nest.git
    git clone git@github.com:$YOU/insights-core.git
    ```

3. Install the egg dependencies.
4. Run the client.

    ```bash
    sudo PYTHONPATH=.:$PATH_TO_SUBSCRIPTION_MANAGER/src EGG=$PATH_TO_INSIGHTS_CORE \
        python3 insights_nest/app.py [--format json] [--register | --unregister | --checkin]
    ```


## Contributing

The easiest way to use the `ruff` linter and formatter is through [`pre-commit`](https://pre-commit.org):

```bash
ruff format && ruff check && mypy .
# ...to run it automatically,
pre-commit install
```


## License

To be determined.


## Debugging

### Environment variables

- `NEST_DEBUG_HTTP`: Print HTTP responses.

### Containers

Running the code inside a container is easy, and may be required for some types of commands (e.g. compliance scan).
For that, we need to bind-mount the Nest and Core into the container, point Python to Nest and RHSM python packages (so it is able to find them), point the EGG to the Core upstream and then run the Nest code.

```bash
podman run -it --rm -v .:/insights-nest --workdir /insights-nest -v $CORE:/insights-core ubi9:latest bash
subscription-manager register
vi /etc/insights-client/insights-client.conf.d/dev.conf
PYTHONPATH=/insights-nest:/usr/lib64/python3.9/site-packages/ EGG=/insights-core python3 insights_nest/__init__.py --no-update --help
```
