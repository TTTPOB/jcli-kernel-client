<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

# jcli-kernel-client

A small, independent fork of [Datalayer's jupyter-kernel-client](https://github.com/datalayer/jupyter-kernel-client), for jcli's HTTP/WebSocket kernel execution. Distribution: `jcli-kernel-client`; Python namespace: `jcli_kernel_client`.

## Source and scope

The baseline is upstream **0.15.0**, commit [`02acbe69699759c737383d0e5d710c7816ed5f3b`](https://github.com/datalayer/jupyter-kernel-client/commit/02acbe69699759c737383d0e5d710c7816ed5f3b). Upstream has no 0.15.0 Git tag. Its version-file commit matches the Python sources in the 0.15.0 PyPI wheel used by jcli. The upstream Git history is retained; `upstream` points at the official repository.

This fork changes package identity and makes object-transfer dependencies optional. It retains the existing transport, execution, output hooks, snippets, and APIs; it does not add transport features or deeply trim the client. Inherited Colab/Kaggle support remains but has not been validated against those external services. Upstream's documentation site and publishing workflows are removed to avoid claiming this fork is the official project or publishing to its targets.

## Install

Fork source: [TTTPOB/jcli-kernel-client](https://github.com/TTTPOB/jcli-kernel-client). Install from PyPI:

```bash
uv pip install jcli-kernel-client
# Optional object transfer:
uv pip install 'jcli-kernel-client[objects]'
```

### Install from a local checkout

Python 3.10 or later is required. Run the following installation commands from the fork repository root. No PyPI publication is implied by these instructions.

```bash
uv pip install .
# Editable development install:
uv pip install -e .
```

The default installation does **not** require `jupyter-mimetypes` or its `pyarrow` dependency. Normal code execution, WebSocket messaging, output hooks, `list_variables()`, and `get_variable_mimetypes()` remain available.

### Optional object transfer

Default installation does **not** support Python object transfer via `set_variable()`, `get_variable()`, or nonempty `variables=` passed to `execute()` / `execute_interactive()`. These APIs lazily import `jupyter-mimetypes` and give an installation hint if it is missing:

```bash
uv pip install '.[objects]'
```

The `objects` extra installs `jupyter-mimetypes` (and consequently `pyarrow`) in the **client** environment. The **target Python kernel** also needs `jupyter-mimetypes` installed in its own environment. Object transfer uses the unchanged upstream snippets and serialization behavior; install the extra only when that functionality is needed.

The optional console is installed with `[konsole]` and launched as `jcli-konsole` (renamed to avoid colliding with the upstream console command).

## Execute code

Start a Jupyter Server with an IPython kernel separately, then:

```python
from jcli_kernel_client import KernelClient

with KernelClient(server_url="http://localhost:8888", token="MY_TOKEN") as kernel:
    reply = kernel.execute("print('hello')")
    assert reply["status"] == "ok"
    assert reply["outputs"] == [
        {"output_type": "stream", "name": "stdout", "text": "hello\n"}
    ]
```

The server URL/token and kernel lifecycle semantics are unchanged from upstream. Existing consumers must change imports from `jupyter_kernel_client` to `jcli_kernel_client`; there is no compatibility alias.

## Known server compatibility

An external server running ipykernel 7.3.0 can strand the first shell request after a new WebSocket connection; resending code on that connection does not resolve it. This is the server-side ROUTER wake-up bug documented in [ipykernel #1554](https://github.com/ipython/ipykernel/issues/1554) and fixed by [PR #1529](https://github.com/ipython/ipykernel/pull/1529), included in ipykernel 7.4.0.

The fixed 7.4.0 release requires Python 3.11 or later; no fixed 7.x release supports Python 3.10. Both test dependency entry points therefore use stable ipykernel `>=6.31,<7` on Python 3.10 and `>=7.4` on Python 3.11+. These versions configure the local test server only: ipykernel is not a runtime dependency of this client, and the client does not install or downgrade kernels on external servers.

## Development and validation

The original Hatchling/pytest/uv toolchain is retained. Use a dedicated environment in this repository, not jcli's environment.

```bash
uv sync
# Default-install behavior and upstream tests not requiring object transfer:
uv run python -m pytest jcli_kernel_client/tests -k 'not set_variable_and_get_variable and not set_variables_on_execute'
# Original object-transfer assertions, with the optional dependency installed:
uv sync --extra objects
uv run --extra objects python -m pytest jcli_kernel_client/tests -k 'set_variable_and_get_variable or set_variables_on_execute'
uv build
```

Integration tests start a real local Jupyter Server and kernels; they require local sockets and processes. New boundary tests import the real package in a subprocess, execute through that server, and check missing-dependency errors, rather than substituting mock-call assertions. The historical upstream changelog is retained as history, not as this fork's release history.

## Release

1. Push the release commit to `main` and require its Tests workflow to pass on Python 3.10 and 3.13.
2. Create and push a lightweight `v<version>` tag matching the single version source in `jcli_kernel_client/__version__.py`.
3. The tag-only release workflow verifies the version, builds the wheel and sdist, publishes via PyPI trusted publishing, and attaches both artifacts to a GitHub release.

The PyPI publisher is configured for `TTTPOB/jcli-kernel-client`, workflow `release.yml`, and GitHub environment `pypi`. No upstream publication credentials are used.

## License

BSD 3-Clause. The complete upstream `LICENSE` and existing Datalayer copyright notices are retained. This fork is not endorsed by Datalayer.
