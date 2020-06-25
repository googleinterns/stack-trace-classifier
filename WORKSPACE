workspace(name = "stack_trace_classifier")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    sha256 = "b5668cde8bb6e3515057ef465a35ad712214962f0b3a314e551204266c7be90c",
    strip_prefix = "rules_python-0.0.2",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.0.2/rules_python-0.0.2.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories")

py_repositories()

load("@rules_python//python:pip.bzl", "pip3_import", "pip_repositories")

pip_repositories()

pip3_import(
    name = "pip3_deps",
    requirements = "//python:requirements.txt",
)

load("@pip3_deps//:requirements.bzl", "pip_install")

pip_install()

http_archive(
    name = "com_google_protobuf",
    strip_prefix = "protobuf-3.12.3",
    urls = ["https://github.com/protocolbuffers/protobuf/releases/download/v3.12.3/protobuf-all-3.12.3.tar.gz"],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()
