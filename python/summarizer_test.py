"""Unittest module for Summarizer."""
import unittest

import pandas as pd
from summarizer import Summarizer
import proto.config_pb2 as config_pb2


class SummarizerTest(unittest.TestCase):
  """Unit test case suite for our Summarizer class."""

  def setUp(self):
    """General setup for configuration files and pandas dataframes."""
    # config dummy error_code_matcher and clusterer set ups
    self.config = config_pb2.Config()
    self.config.error_code_matcher.output_column_name = 'ERROR_CODE'
    self.config.clusterer.output_column_name = 'CLUSTER_CODE'

    self.config.summarizer.n_messages = 5
    self.config.summarizer.n_class_lines_to_show = 5

    # dataframe set ups
    self.simple_dataframe = pd.read_json('testdata/summarizer/simple_data.json',
                                         orient='columns')
    self.stack_lines_dataframe = pd.read_json(
        'testdata/summarizer/stack_lines.json', orient='columns')
    self.multi_cluster_dataframe = pd.read_json(
        'testdata/summarizer/multi_cluster.json', orient='columns')
    super(SummarizerTest, self).setUp()

  def test_generate_summary(self):
    """Various test cases for summarizer.generate_summary."""
    summarizer_simple = Summarizer(self.simple_dataframe, self.config)
    output_df_simple = summarizer_simple.generate_summary()
    self.assertEqual(len(output_df_simple), 3)
    self.assertIn(1, output_df_simple['Size'].values)
    self.assertIn('test', output_df_simple['Text'].values)
    self.assertIn('test2', output_df_simple['Text'].values)
    self.assertIn('test3', output_df_simple['Text'].values)
    self.assertIn('', output_df_simple['ClassLines'].values)

    summarizer_stack_lines = Summarizer(self.stack_lines_dataframe, self.config)
    output_df_stack_lines = summarizer_stack_lines.generate_summary()
    self.assertIn('some.class.java', output_df_stack_lines['ClassLines'].values)
    self.assertIn('some.class2.java',
                  output_df_stack_lines['ClassLines'].values)
    self.assertIn('some.class3.java',
                  output_df_stack_lines['ClassLines'].values)
    self.assertIn('', output_df_stack_lines['Text'].values)

    summarizer_multi_cluster = Summarizer(self.multi_cluster_dataframe,
                                          self.config)
    output_df_multi_cluster = summarizer_multi_cluster.generate_summary()
    self.assertEqual(len(output_df_multi_cluster), 2)
    self.assertIn(2, output_df_multi_cluster['Size'].values)
    self.assertIn(1, output_df_multi_cluster['Size'].values)


if __name__ == "__main__":
  unittest.main()
