"""Module for second prototype of error tokenization using stack trace lines."""
import config


def error_tokenize(trace):
  """Extracts the lines from the stack trace.

  Args:
    trace: String, or object to transformed to string that is in the form
      of a java stack trace

  Returns:
    A List of Strings, each representing one line of the java stack trace
  """
  trace = str(trace)
  str_list = trace.splitlines()

  stack_lines = []
  for line in str_list:
    if line.startswith('\tat'):
      stack_lines.append(line[4:line.index('(')])

  for expr in config.STACK_LINE_FILTERS:
    stack_lines = list(filter(lambda s: not expr.search(s), stack_lines))  # pylint: disable=cell-var-from-loop

  return stack_lines
