"""Module for general preprocessing of the available data before further Clustering."""
import collections.abc
import re


class Preprocessor:
  """Class for preprocessing input data.

  This data will then be used in the future by tokenizer, and clusterer.
  """

  def __init__(self, df, config, output_column_name):
    """Initializes necessary information for preprocessor.

    Preconditions:
      config contains a not None field clusterer, tokenizer and preprocessor

    Args:
      df: A pandas dataframe consisting of the exception column, a name
        column, an errorMessage column and optionally a remoteException
        column

      config: A configuration file in the format as specified by the
        config.proto.

      output_column_name: Internal output_column_name to propagate the results of the Preprocessor
        to our Tokenizer and Classifier.
        Note, this column is used exclusively internally and should be passed in from Classifier
    """
    self.df = df
    self.informative_columns = config.informative_column
    self.ignore_regexes = config.clusterer.tokenizer.preprocessor.ignore_line_regex_matcher
    self.search_regexes = config.clusterer.tokenizer.preprocessor.search_line_regex_matcher
    self.output_column_name = output_column_name

  def filter_lines(self, input_lines):
    """Searches the input_lines for matching regular expressions.

    Matching input lines are scanned for in the configuration file
    This function removes these matching lines.

    Args:
      input_lines: list of strings to filter

    Returns:
      a list of strings as output with all strings not matching to the regular expressions
        as found in ignore_regexes
    """
    regex_expressions = [re.compile(regex) for regex in self.ignore_regexes]
    for expr in regex_expressions:
      input_lines = list(filter(lambda st: not expr.search(st), input_lines))
    return input_lines

  def search_lines(self, input_lines):
    """Searches the input_lines for matching regular expressions.

      Note: all input_lines not containing the matching regular expressions will be removed

    Args:
      input_lines: list of strings to filter

    Returns:
      a list of strings as output filtered such that each string contains all of the
        regular expression matches as found in search_regexes
    """
    regex_expressions = [re.compile(regex) for regex in self.search_regexes]
    for expr in regex_expressions:
      input_lines = list(filter(expr.search, input_lines))
    return input_lines

  def process_dataframe(self):
    """Processes the dataframe creating a new column containing all information.

    On Return:
      Creates a new column with all the available information as found in the informative
        columns concatenated with new lines.
    """
    col = []

    for _, row in self.df.iterrows():
      messages = []
      for column in self.informative_columns:
        if isinstance(row[column], str):
          messages.append(row[column])
        elif isinstance(row[column], collections.abc.Iterable):
          for sub_message in row[column]:
            if isinstance(sub_message, str):
              messages.append(sub_message)

      joined_line_information = '\n'.join(messages).splitlines()
      joined_line_information = self.filter_lines(joined_line_information)
      joined_line_information = self.search_lines(joined_line_information)
      col.append('\n'.join(joined_line_information))

    # We store the result into a column that only the tokenizer will use
    # This column should not be outputted in the final table
    self.df[self.output_column_name] = col
