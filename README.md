<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

# jcli-kernel-client

A small, independent fork of [Datalayer's jupyter-kernel-client](https://github.com/datalayer/jupyter-kernel-client), for jcli's HTTP/WebSocket kernel execution. Distribution: `jcli-kernel-client`; Python namespace: `jcli_kernel_client`; initial fork version: `0.1.0`.

## Source and scope

The baseline is upstream **0.15.0**, commit [`02acbe69699759c737383d0e5d710c7816ed5f3b`](https://github.com/datalayer/jupyter-kernel-client/commit/02acbe69699759c737383d0e5d710c7816ed5f3b). Upstream has no 0.15.0 Git tag. Its version-file commit matches the Python sources in the 0.15.0 PyPI wheel used by jcli. The upstream Git history is retained; `upstream` points at the official repository.

This fork changes package identity and makes object-transfer dependencies optional. It retains the existing transport, execution, output hooks, snippets, and APIs; it does not add transport features or deeply trim the client. Inherited Colab/Kaggle support remains but has not been validated against those external services. Upstream's documentation site and publishing workflows are removed to avoid claiming this fork is the official project or publishing to its targets. This repository does not automatically publish releases.

## Install locally

Python 3.10 or later is required. No PyPI publication is implied by these instructions.

```bash
uv pip install /home/tpob/playground/jcli-kernel-client
# Editable development install:
uv pip install -e /home/tpob/playground/jcli-kernel-client
```

The default installation does **not** require `jupyter-mimetypes` or its `pyarrow` dependency. Normal code execution, WebSocket messaging, output hooks, `list_variables()`, and `get_variable_mimetypes()` remain available.

### Optional object transfer

Default installation does **not** support Python object transfer via `set_variable()`, `get_variable()`, or nonempty `variables=` passed to `execute()` / `execute_interactive()`. These APIs lazily import `jupyter-mimetypes` and give an installation hint if it is missing:

```bash
uv pip install '/home/tpob/playground/jcli-kernel-client[objects]'
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

## Development and validation

The original Hatchling/pytest/uv toolchain is retained. Use a dedicated environment in this repository, not jcli's environment.

```bash
uv sync
# Default-install behavior and upstream tests not requiring object transfer:
uv run python -m pytest jcli_kernel_client/tests -k 'not set_variable_and_get_variable and not set_variables_on_execute'
# Original object-transfer assertions, with the optional dependency installed:
uv sync --extra objects
uv run --extra objects python -m pytest jcli_kernel_client/tests/test_client.py -k 'set_variable_and_get_variable or set_variables_on_execute'
uv build
```

Integration tests start a real local Jupyter Server and kernels; they require local sockets and processes. New boundary tests import the real package in a subprocess, execute through that server, and check missing-dependency errors, rather than substituting mock-call assertions. The historical upstream changelog is retained as history, not as this fork's release history.

## License

BSD 3-Clause. The complete upstream `LICENSE` and existing Datalayer copyright notices are retained. This fork is not endorsed by Datalayer.
