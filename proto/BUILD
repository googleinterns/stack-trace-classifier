load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_proto_library(
    name = "config",
    srcs = ["config.proto"],
    visibility = ["//python:__subpackages__"],
    deps = [
        ":server_error_reason",
        ":storage_error_reason",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_proto_library(
    name = "big_query_config",
    srcs = ["big_query_config.proto"],
    visibility = ["//python:__subpackages__"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)

py_proto_library(
    name = "server_error_reason",
    srcs = ["server_error_reason.proto"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)

py_proto_library(
    name = "storage_error_reason",
    srcs = ["storage_error_reason.proto"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)
