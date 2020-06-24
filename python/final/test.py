"""
Test module for ensuring bazel dependency linkings are working as intended
"""
import numpy as np
import proto.config_pb2

a = np.array([0, 0, 0])
config = proto.config_pb2.Config()
config.project_name = "test"
print(config)
print(a)
