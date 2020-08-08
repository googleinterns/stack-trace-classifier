"""Module for summarization of the errors collected in the classification phase."""
import re

import numpy as np
import pandas as pd

from tokenizer import Tokenizer


class Summarizer:
  """Class for presenting the information given by the classifier algorithms.

  The summary output dataframe is in the below format:
    error_code / cluster_code : the error code or cluster code of the group
    'Size' : the size of the cluster group / error code group
    'ClassLines' : a filtered list of the class lines in this exception group
    'Text' : the non-class line information in this exception group
    etc... : other input dataframe columns in list format denoting one error per item.
  """
  INTERNAL_COLUMN_NAME = '_internal_preprocessor_output_col_'

  def __init__(self, df, config):
    """Initializes the needed data for summarizer.

      Preconditions:
        config contains a not None field clusterer, tokenizer and preprocessor

      Args:
        df: A pandas dataframe that has finished running the various classification algorithms
          as defined in config

        config: A configuration file in the format as specified by the
          config.proto.
    """
    self.df = df
    self.error_code_matcher_has_run = config.HasField('error_code_matcher')
    if self.error_code_matcher_has_run:
      self.error_code_matcher_col = config.error_code_matcher.output_column_name
    self.clusterer_has_run = config.HasField('clusterer')
    if self.clusterer_has_run:
      self.clusterer_col = config.clusterer.output_column_name
    self.n_messages = config.summarizer.n_messages
    self.n_class_lines_to_show = config.summarizer.n_class_lines_to_show
    self.tokenizer = Tokenizer(config)

  def summarize_exception(self, exception_message_column):
    """Extracts the useful information from the exception column.

    Method that attempts to extract possibly useful information from input stack-trace messages
    All java class lines found in filters are explicitly excluded from the message.
    Java class line information is accumulated in stack_lines_col
    Whereas all non-java (presumably text information) is included in other_text_lines_col

    Args:
      exception_message_column: grouped column of exception information we are attempting to
      extract a summary from

    Returns:
      tuple of (stack_lines_col, other_text_lines_col)
        stack_lines_col : list that represents the possibly useful information as found in
        each of the stack trace lines of the chosen message column
      other_text_lines_col : list that represents the possibly useful (text) information
        in each stack trace in the message column
    """
    stack_lines_col = []
    other_text_lines_col = []
    for message_json in exception_message_column:
      message_list = pd.read_json(message_json).values
      # we arbitrarily choose the first message as the representative
      exception_message = message_list[0][0]
      stack_lines = self.tokenizer.stack_trace_line_tokenizer(
          exception_message)[:self.n_class_lines_to_show]
      other_text_lines = self.tokenizer.human_readable_tokenizer(
          exception_message)
      stack_lines_col.append('\n'.join(stack_lines))
      other_text_lines_col.append('\n'.join(other_text_lines))
    return stack_lines_col, other_text_lines_col

  def summarize_classifier(self, column, cols_to_drop):
    """Summarizes the results from the given classification mode determined by column.

    Does not include the information stored in the columns specified in cols_to_drop in output
    The summary includes the first n errors determined by n_messages (as an array since
    pandas does not inherently support repeated fields) as well as the number of errors in the
    cluster / error code group

    Args:
      column: string the classification algorithm that is being summarized denoted by the column
        string it corresponds with

      cols_to_drop: list of columns to drop in the summary dataframe

    Returns:
      a dataframe holding the information
    """
    error_counts = self.df[column].value_counts()
    groups = self.df.groupby(column).agg(
        lambda x: x[x.notna()].head(self.n_messages).to_json(orient='values'))
    groups['Size'] = error_counts
    stack_lines_col, text_lines_col = self.summarize_exception(
        groups[self.INTERNAL_COLUMN_NAME])
    groups['Text'] = text_lines_col
    groups['ClassLines'] = stack_lines_col
    groups.drop(columns=cols_to_drop, inplace=True)
    return groups.reset_index()

  def reorganize_dataframe(self, dataframe, cols_to_reorganize):
    """Reorganizes the dataframe such that the columns to reorganize appear first.

    This makes the dataframe more readable during output.
    This method ensures that SIZE is the first column to appear after the possible cluster codes.
    This method also ensures that cluster_code appears as the first column.

    Args:
      dataframe: dataframe to reorganize the information of

      cols_to_reorganize: columns to be placed first, ahead of the other columns

    Returns:
      A dataframe with the same information exception with the cols_to_reorganize occurring
      first
    """
    dataframe_cols = set(dataframe.columns)
    other_cols = dataframe_cols ^ cols_to_reorganize
    cols_list = list(cols_to_reorganize)
    # Ensure the column order is, 'TEXT', 'CLASS_LINES'
    cols_list.append(cols_list.pop(cols_list.index('Text')))
    cols_list.append(cols_list.pop(cols_list.index('ClassLines')))
    # Ensure the column that is second is 'SIZE'
    cols_list.insert(0, cols_list.pop(cols_list.index('Size')))
    # Ensure that the first column is the clusterer column
    cols_list.insert(0, cols_list.pop(cols_list.index(self.clusterer_col)))
    return dataframe.loc[:, cols_list + list(other_cols)]

  def generate_summary(self):
    """Outputs a summary of the various error codes in a readable dataframe format.

    Returns:
      A dataframe of summary consisting of the following columns:
        error_code / cluster_code : the error code or cluster code of the group
        'Size' : the size of the cluster group / error code group
        'ClassLines' : a filtered list of the class lines in this exception group
        'Text' : the non-class line information in this exception group
        etc... : other input dataframe columns in list format denoting one error per item.

    Note: directly using a to_gbq on this dataframe will produce columns consisting of arrays
    since pandas does not naturally support the repeated fields that GBQ does
    """
    # need to drop added columns in final summary table
    cols_to_drop = [self.INTERNAL_COLUMN_NAME]
    # cols to be reordered to the front
    cols_to_reorganize = set()

    if self.error_code_matcher_has_run:
      cols_to_reorganize.add(self.error_code_matcher_col)

    # Generate the summary data for clusterer
    if self.clusterer_has_run:
      cluster_code_groups = self.summarize_classifier(self.clusterer_col,
                                                      cols_to_drop)
      cols_to_reorganize.add(self.clusterer_col)

    # need to reorganize the columns
    cols_to_reorganize.add('Size')
    cols_to_reorganize.add('Text')
    cols_to_reorganize.add('ClassLines')
    return self.reorganize_dataframe(cluster_code_groups, cols_to_reorganize)
