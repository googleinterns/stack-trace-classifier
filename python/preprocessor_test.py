"""Unittest module for Preprocessor."""
import unittest

import pandas as pd
from preprocessor import Preprocessor
import proto.config_pb2 as config_pb2


class PreprocessorTest(unittest.TestCase):
  """Unit test case suite for our Preprocessor class."""

  def setUp(self):
    """General setup for configuration files and pandas dataframes."""
    ignore_lines = ['USELESS_INFORMATION', 'chicken', 'turkey']
    search_lines = ['USEFUL_INFORMATION', 'error']
    informative_columns = ["exception", "remoteException", "errorMessage"]
    ignore_words = ['testIgnoreWord']
    # config set ups
    self.config = config_pb2.Config()
    self.config.clusterer.tokenizer.preprocessor.ignore_line_regex_matcher.extend(
        ignore_lines)
    self.config.clusterer.tokenizer.preprocessor.search_line_regex_matcher.extend(
        search_lines)
    self.config.clusterer.tokenizer.preprocessor.ignore_word_regex_matcher.extend(
        ignore_words)
    self.config.informative_column.extend(informative_columns)

    # dataframe set ups
    self.empty_dataframe = pd.read_json('testdata/preprocessor/empty_data.json',
                                        orient='columns')
    self.simple_dataframe = pd.read_json(
        'testdata/preprocessor/simple_data.json', orient='columns')
    super(PreprocessorTest, self).setUp()

  def test_filter_lines(self):
    """Various test cases for preprocessor.filter_lines."""
    preprocessor = Preprocessor(self.empty_dataframe, self.config, '_INFO_')
    # These lines should remain the same
    no_matches = ['This information could be useful', 'we will not delete it']
    self.assertEqual(preprocessor.filter_lines(no_matches), no_matches)

    # The first line should be deleted (it contains a word in the IGNORE list)
    single_match = ['This is USELESS_INFORMATION', 'but this might not be']
    self.assertEqual(preprocessor.filter_lines(single_match),
                     ['but this might not be'])

    # Both lines should be deleted since both contain words in the IGNORE list
    multi_match = [
        'This is completely USELESS_INFORMATION',
        'chicken and turkey share the same order'
    ]
    self.assertFalse(preprocessor.filter_lines(multi_match))

  def test_word_filter(self):
    """Tests pertaining to preprocessor.filter_words."""
    preprocessor = Preprocessor(self.empty_dataframe, self.config, '_INFO_')
    sample_string = 'Some error information here, testIgnoreWord'
    self.assertEqual(preprocessor.filter_words(sample_string),
                     'Some error information here, ')

  def test_search_lines(self):
    """Various test cases for preprocessor.search_lines."""
    preprocessor = Preprocessor(self.empty_dataframe, self.config, '_INFO_')

    # These lines should get deleted
    no_matches = ['not matching text', 'should get deleted']
    self.assertFalse(preprocessor.search_lines(no_matches))

    # The first line should be kept since it explicitly matches
    # to all RE in USEFUL_INFORMATION
    # The second line is removed since although it matches to error,
    # it does not match to USEFUL_INFORMATION
    single_match = ['this error is USEFUL_INFORMATION', 'but this error is not']
    self.assertEqual(preprocessor.search_lines(single_match),
                     ['this error is USEFUL_INFORMATION'])

    # Both lines should be kept since both are explicitly matched to
    # by both regular expressions in search_lines
    multi_match = [
        'this error is USEFUL_INFORMATION',
        'of course that error is USEFUL_INFORMATION!'
    ]
    self.assertEqual(preprocessor.search_lines(multi_match), multi_match)

  def test_process_dataframe(self):
    """End to end test of Preprocessor through preprocessor.process."""
    preprocessor_simple = Preprocessor(self.simple_dataframe, self.config,
                                       '_INFO_')
    preprocessor_simple.process_dataframe()
    self.assertEqual(preprocessor_simple.df['_INFO_'][0], "")
    self.assertEqual(preprocessor_simple.df['_INFO_'][1],
                     "we have an error that contains USEFUL_INFORMATION")
    self.assertEqual(
        preprocessor_simple.df['_INFO_'][2],
        "This line should be kept since it has an error that is USEFUL_INFORMATION"
    )


if __name__ == "__main__":
  unittest.main()
