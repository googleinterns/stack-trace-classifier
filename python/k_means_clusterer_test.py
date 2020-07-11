"""
Unittest module for Clusterer
"""
import unittest
import pandas as pd
import proto.config_pb2
from k_means_clusterer import KMeansClusterer

class KMeansClustererTest(unittest.TestCase):
    """
    Unittest class for Clusterer
    """

    def setUp(self):
        """
        Need to setup the configuration files and dataframes
        """
        informative_columns = [
            "exception",
            "remoteException",
            "errorMessage"
        ]
        # configuration using human readable tokenizer
        self.config_human_readable = proto.config_pb2.Config()
        self.config_human_readable.informative_column.extend(informative_columns)
        self.config_human_readable.clusterer.tokenizer.token_min_length = 2
        self.config_human_readable.clusterer.tokenizer.mode = proto.config_pb2.Tokenizer.TokenizerMode.HUMAN_READABLE
        self.config_human_readable.clusterer.mini_batch = False
        self.config_human_readable.clusterer.min_cluster = 2
        self.config_human_readable.clusterer.max_cluster = 5
        self.config_human_readable.clusterer.output_column_name = 'clusterer_output'

        # configuration for stack trace lines
        self.config_stack_trace_lines = proto.config_pb2.Config()
        self.config_stack_trace_lines.informative_column.extend(informative_columns)
        self.config_stack_trace_lines.clusterer.tokenizer.token_min_length = 2
        self.config_stack_trace_lines.clusterer.tokenizer.mode = proto.config_pb2.Tokenizer.TokenizerMode.STACK_TRACE_LINES
        self.config_stack_trace_lines.clusterer.mini_batch = False
        self.config_stack_trace_lines.clusterer.min_cluster = 2
        self.config_stack_trace_lines.clusterer.max_cluster = 5
        self.config_stack_trace_lines.clusterer.output_column_name = 'clusterer_output'

        # sample data
        self.simple_dataframe = pd.read_json('testdata/k_means_clusterer/simple_data.json', orient='columns')
        self.repeated_dataframe = pd.read_json('testdata/k_means_clusterer/repeated_data.json', orient='columns')
        self.stack_trace_dataframe = pd.read_json('testdata/k_means_clusterer/stack_trace_data.json', orient='columns')


    def test_cluster_errors_simple(self):
        """
        Simple test on 2 different clusters
        """
        clusterer = KMeansClusterer(self.simple_dataframe, self.config_human_readable)
        clusterer.cluster_errors()

        # number of clusters should be 2
        self.assertTrue(len(clusterer.df['clusterer_output'].unique()) == 2)


    def test_cluster_errors_repeated(self):
        """
        Test with repeated data, should still only be 2 clusters despite repeated data
        """
        clusterer = KMeansClusterer(self.repeated_dataframe, self.config_human_readable)
        clusterer.cluster_errors()

        # number of clusters should be 2
        self.assertTrue(len(clusterer.df['clusterer_output'].unique()) == 2)


    def test_cluster_errors_stack_trace(self):
        """
        Test using stack trace lines
        """
        clusterer = KMeansClusterer(self.stack_trace_dataframe, self.config_stack_trace_lines)
        clusterer.cluster_errors()

        # number of clusters should be 2
        self.assertTrue(len(clusterer.df['clusterer_output'].unique()) == 2)


if __name__ == "__main__":
    unittest.main()
