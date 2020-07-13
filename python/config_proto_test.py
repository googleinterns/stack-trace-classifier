"""
Unittest module for the config proto checks
"""
import unittest
import proto.config_pb2
import proto.big_query_config_pb2

class ConfigProtoTest(unittest.TestCase):
    """
    Unittest class for the config proto
    """

    def test_has_field(self):
        """
        Tests whether HasField on a nonexisting sub message works as intended
        """
        config = proto.config_pb2.Config()
        self.assertFalse(config.HasField('error_code_matcher'))


    def test_existing_field(self):
        """
        Tests whether an existing field works as intended
        """
        config = proto.big_query_config_pb2.BigQueryConfig()
        config.project_id = "name"
        self.assertTrue(config.project_id == "name")


    def test_has_nested_field(self):
        """
        Tests whether HasField in a nested submessage works as intended
        """
        clusterer = proto.config_pb2.Clusterer()
        self.assertFalse(clusterer.HasField('tokenizer'))


if __name__ == "__main__":
    unittest.main()
