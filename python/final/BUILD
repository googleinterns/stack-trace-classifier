load("@pip3_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_binary(
    name = "test",
    srcs = ["test.py"],
    main = "test.py",
    deps = [":reqs"],
)

py_library(
    name = "reqs",
    deps = [
        requirement("numpy"),
        "//proto:config",
    ],
)
