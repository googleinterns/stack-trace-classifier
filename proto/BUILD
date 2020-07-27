load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_proto_library(
    name = "config_py_pb2",
    srcs = ["config.proto"],
    visibility = ["//python:__subpackages__"],
    deps = [
        ":server_error_reason_py_pb2",
        ":storage_error_reason_py_pb2",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_proto_library(
    name = "big_query_config_py_pb2",
    srcs = ["big_query_config.proto"],
    visibility = ["//python:__subpackages__"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)

py_proto_library(
    name = "server_error_reason_py_pb2",
    srcs = ["server_error_reason.proto"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)

py_proto_library(
    name = "storage_error_reason_py_pb2",
    srcs = ["storage_error_reason.proto"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)

exports_files(glob(["*.textproto"]))
