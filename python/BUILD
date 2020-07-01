load("@pip3_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_binary(
    name = "stub",
    srcs = ["stub.py"],
    main = "stub.py",
    deps = [":stub_deps"],
)

py_test(
    name = "tokenizer_test",
    srcs = [
        "tokenizer.py",
        "tokenizer_test.py",
    ],
    data = [
        "//testdata:tokenizer/sample_stack_trace.txt",
    ],
    main = "tokenizer_test.py",
    deps = [
        "//proto:config",
        requirement("regex"),
    ],
)

py_test(
    name = "preprocessor_test",
    srcs = [
        "preprocessor.py",
        "preprocessor_test.py",
    ],
    data = [
        "//testdata:preprocessor/empty_data.json",
        "//testdata:preprocessor/simple_data.json",
    ],
    main = "preprocessor_test.py",
    deps = [
        "//proto:config",
        requirement("numpy"),
        requirement("regex"),
        requirement("pandas"),
    ],
)

py_test(
    name = "error_code_matcher_test",
    srcs = [
        "error_code_matcher.py",
        "error_code_matcher_test.py",
    ],
    data = [
        "//testdata:error_code_matcher/empty_data.json",
        "//testdata:error_code_matcher/simple_data.json",
        "//testdata:error_code_matcher/uninformative_data.json",
    ],
    main = "error_code_matcher_test.py",
    deps = [
        "//proto:config",
        requirement("numpy"),
        requirement("regex"),
        requirement("pandas"),
    ],
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
