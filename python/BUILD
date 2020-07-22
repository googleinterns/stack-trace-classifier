load("@pip3_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_binary(
    name = "stack_trace_classifier_main",
    srcs = [
        "k_means_clusterer.py",
        "preprocessor.py",
        "stack_trace_classifier_main.py",
        "tokenizer.py",
    ],
    data = [
        "//proto:big_query_config_example.textproto",
        "//proto:config_example.textproto",
    ],
    main = "stack_trace_classifier_main.py",
    deps = [":stack_trace_classifier_main_deps"],
)

py_library(
    name = "stack_trace_classifier_main_deps",
    deps = [
        ":error_code_matcher",
        ":k_means_clusterer",
        ":summarizer",
        requirement("six"),
        requirement("google-api-core"),
        requirement("google-auth"),
        requirement("google-cloud-bigquery"),
        requirement("google-resumable-media"),
    ],
)

py_library(
    name = "summarizer",
    srcs = [
        "summarizer.py",
    ],
    deps = [
        requirement("pandas"),
        requirement("numpy"),
        requirement("regex"),
    ],
)

py_library(
    name = "k_means_clusterer",
    srcs = [
        "k_means_clusterer.py",
    ],
    deps = [
        ":preprocessor",
        ":tokenizer",
        "//proto:config",
        requirement("scikit-learn"),
    ],
)

py_test(
    name = "k_means_clusterer_test",
    srcs = [
        "k_means_clusterer.py",
        "k_means_clusterer_test.py",
        "preprocessor.py",
        "tokenizer.py",
    ],
    data = [
        "//testdata:k_means_clusterer/repeated_data.json",
        "//testdata:k_means_clusterer/simple_data.json",
        "//testdata:k_means_clusterer/stack_trace_data.json",
    ],
    main = "k_means_clusterer_test.py",
    deps = [
        "//proto:config",
        requirement("numpy"),
        requirement("regex"),
        requirement("pandas"),
        requirement("scikit-learn"),
    ],
)

py_library(
    name = "tokenizer",
    srcs = [
        "tokenizer.py",
    ],
    deps = [
        "//proto:config",
        requirement("regex"),
    ],
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

py_library(
    name = "preprocessor",
    srcs = [
        "preprocessor.py",
    ],
    deps = [
        "//proto:config",
        requirement("numpy"),
        requirement("regex"),
        requirement("pandas"),
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

py_library(
    name = "error_code_matcher",
    srcs = [
        "error_code_matcher.py",
    ],
    deps = [
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
