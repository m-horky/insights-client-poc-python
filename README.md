# insights-shell

A next-generation implementation of [`insights-client`](https://github.com/RedHatInsights/insights-client/).


## Developer setup

1. Fork both this and the insights-core repository.
2. Clone both of them into the same directory.

    ```bash
    git clone git@github.com:$YOU/insights-shell.git
    git clone git@github.com:$YOU/insights-core.git
    ```

3. Install the egg dependencies.
4. Run the client.

    ```bash
    sudo PYTHONPATH=. EGG=../insights-core python3 insights_shell/__init__.py --insecure-egg ...
    ```


## Contributing

The easiest way to use the `ruff` linter and formatter is through [`pre-commit`](https://pre-commit.org):

```bash
pre-commit run -a
# ...to run it automatically,
pre-commit install
```


## License

To be determined.
