"""Module for the various Tokenizers usuable by Clusterer."""
import re
import string

import proto.config_pb2


class Tokenizer:
  """Class for our general suite of string tokenizers for our Clusterer."""

  def __init__(self, config):
    """Initializes the information needed by Clusterer.

    Args:
      config: A configuration file in the format as specified by the
        config.proto.
    """
    self.min_token_len = config.clusterer.tokenizer.token_min_length
    # Additional splitting only makes sense on human readable mode
    if config.clusterer.tokenizer.mode == proto.config_pb2.Tokenizer.TokenizerMode.HUMAN_READABLE:
      self.split_ons = config.clusterer.tokenizer.split_on
      self.punctuations = config.clusterer.tokenizer.punctuation

  def human_readable_tokenizer(self, input_string):
    """Tokenization method for parsing the input_string into a human readable list of strings.

    Args:
      input_string: the string we are attempting to tokenize

    Returns:
      List of strings, each string representing a human readable token
    """
    # in case input is stored in a different format in dataframe
    input_string = str(input_string)
    # Base split on new line and spaces
    tokens = input_string.split()
    # Split for every other defined additional splitter
    for split_on in self.split_ons:
      tokens = sum(map(lambda w: re.split(split_on, w), tokens), [])
    # Removing trailing and leading punctuation
    punctuation = string.punctuation + ''.join(self.punctuations)
    tokens = list(map(lambda w: w.strip(punctuation), tokens))
    # Removing all numerical hex values
    # WARNING this regex actually matches to certain words like 'be' since
    # 'be' is indeed a hex value
    numerics_regex = r'[0-9a-f|:|\.|\[|\]]+'
    tokens = list(filter(lambda w: not re.fullmatch(numerics_regex, w), tokens))  # pylint: disable=cell-var-from-loop
    # Remove 1 word characters
    tokens = list(filter(lambda w: len(w) >= self.min_token_len, tokens))
    # Remove empty strings
    tokens = list(filter(lambda w: w, tokens))
    # lowercase all words for consistency
    tokens = list(map(lambda w: w.lower(), tokens))
    return tokens

  def stack_trace_line_tokenizer(self, input_string):
    """Tokenization method for parsing the input_string into a list of stack trace strings.

    Note, each token representing a line in the stack trace.

    Args:
      input_string: the string we are attempting to tokenize

    Returns:
      List of strings, each string representing a stack trace class line
    """
    # in case input is stored in a different format in dataframe
    input_string = str(input_string)
    input_string_lines = input_string.splitlines()
    # search for stack trace lines, i.e those that begin with '\tat'
    stack_lines = []
    for line in input_string_lines:
      if line.startswith('\tat'):
        # we only care about the "class" or anything after the
        # \tat and before line number
        stack_lines.append(line[4:line.index('(')])

    # filter out minimum length tokens
    stack_lines = list(
        filter(lambda line: len(line) >= self.min_token_len, stack_lines))

    return stack_lines
