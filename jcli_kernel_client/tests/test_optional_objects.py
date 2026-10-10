# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import subprocess
import sys


def test_import_execution_and_optional_api_without_mimetypes(jupyter_server):
    """Exercise the real client/server boundary with object transfer unavailable."""
    port, token = jupyter_server
    code = r'''
import sys

# Model the missing optional module even when running an extra-enabled suite.
sys.modules["jupyter_mimetypes"] = None

from jcli_kernel_client import KernelClient, KernelHttpManager, KernelWebSocketClient
from jcli_kernel_client import SNIPPETS_REGISTRY, get_mimebundle_text

manager = KernelHttpManager(server_url=sys.argv[1], token=sys.argv[2])
assert manager.client_factory is KernelWebSocketClient
assert "python" in SNIPPETS_REGISTRY.available_languages
assert get_mimebundle_text({"text/plain": "plain", "text/markdown": "rich"}) == "rich"

with KernelClient(server_url=sys.argv[1], token=sys.argv[2]) as kernel:
    reply = kernel.execute("answer = 42; print(answer)")
    assert reply["status"] == "ok"
    assert reply["outputs"] == [
        {"output_type": "stream", "name": "stdout", "text": "42\n"}
    ]
    assert any(v["name"] == "answer" for v in kernel.list_variables())
    assert kernel.get_variable_mimetypes("answer", "text/plain") == ({"text/plain": "42"}, {})

    outputs = []
    from functools import partial
    from jcli_kernel_client.client import output_hook
    reply = kernel.execute_interactive("print('interactive')", output_hook=partial(output_hook, outputs))
    assert reply["content"]["status"] == "ok"
    assert outputs == [{"output_type": "stream", "name": "stdout", "text": "interactive\n"}]

    for operation in (
        lambda: kernel.set_variable("x", [1, 2]),
        lambda: kernel.get_variable("answer"),
        lambda: kernel.execute("pass", variables={"x": [1, 2]}),
        lambda: kernel.execute_interactive("pass", variables={"x": [1, 2]}),
    ):
        try:
            operation()
        except ImportError as exc:
            assert "uv pip install 'jcli-kernel-client[objects]'" in str(exc)
            assert "target Python kernel also needs jupyter-mimetypes" in str(exc)
            assert isinstance(exc.__cause__, ModuleNotFoundError)
            assert exc.__cause__.name == "jupyter_mimetypes"
        else:
            raise AssertionError("Object transfer must require the optional dependency")
'''
    result = subprocess.run(
        [sys.executable, "-c", code, f"http://localhost:{port}", token],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
