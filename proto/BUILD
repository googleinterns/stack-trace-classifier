load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_proto_library(
    name = "config",
    srcs = ["config.proto"],
    visibility = ["//python/final:__subpackages__"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)

py_proto_library(
    name = "big_query_config",
    srcs = ["big_query_config.proto"],
    visibility = ["//python/final:__subpackages__"],
    deps = ["@com_google_protobuf//:protobuf_python"],
)
