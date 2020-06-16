"""
Module for prototype error tokenization by human readable error messages
"""
from string import punctuation
import re
import nltk
import config


def process_stack_trace(trace):
    """
    Helper Method for errorTokenize
    Extracts 'human readable' text from a stack-trace.

    Args:
        trace: String, or object to be transformed to string that is in the
        form of a java stack trace

    Returns:
        A String that is a human readable java stack trace
    """
    trace = str(trace)
    str_list = trace.splitlines()
    # Filter out bad re
    for expr in config.LINE_FILTERS:
        str_list = list(filter(lambda s: not expr.search(s), str_list))
    # Ensure the re matches
    for expr in config.LINE_MATCHES:
        str_list = list(filter(expr.search, str_list))
    # We only "care" about the message following the first ':' I.E.
    str_list = [word[word.find(':')+1:] for word in str_list]
    msg = '\n'.join(str_list)
    return msg


def error_tokenize(trace):
    """
    A tokenizer for java stack-traces, first uses processStackTrace to extract
    human readable errors from the stack trace then tokenizes the human readable
    error

    Args:
        trace: String of a java stack trace

    Returns:
        A list of strings with each string representing a token
    """
    msg = process_stack_trace(trace)
    # "Base" tokenization
    tokens = nltk.word_tokenize(msg)
    # Many 'words' are just one letter punctuation, I.E. '>'
    tokens = list(filter(lambda w: len(w) > 1, tokens))
    # Split any remaining words that contain '=' in them
    tokens = sum(map(lambda w: re.split(r'=', w), tokens), [])
    # Removing trailing and leading punctuation
    punc = punctuation + ':' + '/' + '\n' + '\t'
    tokens = list(map(lambda w: w.strip(punc), tokens))
    # Removing all numerics and
    tokens = list(filter(lambda w: not re.fullmatch(r'[0-9a-f|:|\.]+', w), tokens))
    # Removes empty strings
    tokens = list(filter(lambda w: w, tokens))
    # Removes all words not in the "english" dictionary this one is a little bit extreme ..
    tokens = list(filter(lambda w: w.lower() in config.WORDS, tokens))
    # lowercase all tokens for consistency
    tokens = list(map(lambda w: w.lower(), tokens))
    return tokens
