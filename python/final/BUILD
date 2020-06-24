load("@pip3_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_binary(
    name = "stub",
    srcs = ["stub.py"],
    main = "stub.py",
    deps = [":stub_deps"],
)

py_test(
    name = "config_proto_test",
    srcs = ["config_proto_test.py"],
    deps = [
        "//proto:big_query_config",
        "//proto:config",
    ],
)

py_library(
    name = "stub_deps",
    deps = [
        requirement("numpy"),
    ],
)
