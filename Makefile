# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

.PHONY: dev test build

dev:
	uv sync --extra objects --extra lint --extra typing

test:
	uv run --extra objects python -m pytest jcli_kernel_client/tests

build:
	uv build
