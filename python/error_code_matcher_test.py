"""
Unittest module for the ErrorCodeMatcher
"""
import unittest
import pandas as pd
import proto.config_pb2
import proto.server_error_reason_pb2
import proto.storage_error_reason_pb2
from error_code_matcher import ErrorCodeMatcher

class TestErrorCodeMatcher(unittest.TestCase):
    """
    Unittest class for ErrorCodeMatcher
    """

    def setUp(self):
        """
        Need to setup the test configuration files as well as the test panda df
        """
        uninformative_server_errors = [
            proto.server_error_reason_pb2.SERVER_UNEXPECTED_EXCEPTION,
            proto.server_error_reason_pb2.SERVER_ERROR_REASON_UNKNOWN
        ]
        uninformative_storage_errors = [
            proto.storage_error_reason_pb2.STORAGE_ERROR_REASON_UNKNOWN
        ]
        informative_columns = [
            "exception",
            "remoteException",
            "errorMessage"
        ]

        # configuration using default error codes to match to, see informative_errors.proto
        self.config_default = proto.config_pb2.Config()
        self.config_default.error_code_matcher.ignore_server_error_reason.extend(uninformative_server_errors)
        self.config_default.error_code_matcher.ignore_storage_error_reason.extend(uninformative_storage_errors)
        self.config_default.error_code_matcher.output_column_name = "ERRCODE"
        self.config_default.informative_column.extend(informative_columns)

        self.simple_dataframe = pd.read_json('testdata/error_code_matcher/simple_data.json', orient='columns')
        self.empty_dataframe = pd.read_json('testdata/error_code_matcher/empty_data.json', orient='columns')
        self.uninformative_dataframe = pd.read_json('testdata/error_code_matcher/uninformative_data.json', orient='columns')


    def test_simple_data(self):
        """
        Various tests pertaining to the simple_data.json data.
        See testdata/error_code_matcher_test/simple_data.json for details
        """
        # Should have matches for all
        error_code_matcher_default = ErrorCodeMatcher(self.simple_dataframe, self.config_default)
        error_code_matcher_default.match_informative_errors()
        self.assertTrue(len(error_code_matcher_default.df['ERRCODE'] == 3))
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][0] == 'SERVER_NOT_IMPLEMENTED_EXCEPTION')
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][1] == 'STORAGE_PAGINATED_DISALLOWED_WITHOUT_SNAPSHOT_TIMESTAMP')
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][2] == 'STORAGE_STALE_LOCK_TIMESTAMP')


    def test_empty_data(self):
        """
        Various tests pertaining to the empty_data.json data.
        See testdata/error_code_matcher_test/empty_data.json for details
        """
        # Should have no matches data is empty
        error_code_matcher_default = ErrorCodeMatcher(self.empty_dataframe, self.config_default)
        error_code_matcher_default.match_informative_errors()
        self.assertTrue(len(error_code_matcher_default.df['ERRCODE'] == 3))
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][0] is None)
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][1] is None)
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][2] is None)


    def test_uninformative_data(self):
        """
        Various tests pertaining to the uninformative_data.json data.
        See testdata/error_code_matcher_test/uninformative_data.json for details
        """
        error_code_matcher_default = ErrorCodeMatcher(self.uninformative_dataframe, self.config_default)
        error_code_matcher_default.match_informative_errors()
        # All errors are uninformative, thus all should be None.
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][0] is None)
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][1] is None)
        self.assertTrue(error_code_matcher_default.df['ERRCODE'][2] is None)


if __name__ == "__main__":
    unittest.main()
