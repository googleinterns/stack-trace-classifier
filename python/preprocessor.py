"""
Module for general preprocessing of the available data before further Clustering
"""
import re

class Preprocessor:
    """
    Class for preprocessing input data before being passed forward to tokenization and clustering

    Params:
        df: A pandas dataframe consisting of the exception column, a name
            column, an errorMessage column and optionally a remoteException
            column

        config: A configuration file in the format as specified by the
            config.proto.

        output_column_name: Internal output_column_name to propagate the results of the Preprocessor
            to our Tokenizer and Classifier.
            Note, this column is used exclusively internally and should be passed in from Classifier
    """
    def __init__(self, df, config, output_column_name):
        """
        Preconditions:
            config contains a not None field clusterer, tokenizer and preprocessor
        """
        self.df = df
        self.informative_columns = config.informative_column
        self.ignore_regexes = config.clusterer.tokenizer.preprocessor.ignore_line_regex_matcher
        self.search_regexes = config.clusterer.tokenizer.preprocessor.search_line_regex_matcher
        self.output_column_name = output_column_name


    def filter_lines(self, input_lines):
        """
        Searches the input_lines for matching regular expressions as specified by the configuration
        and REMOVES these matching lines.

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
        """
        Searches the input_lines for matching regular expressions as specified by the configuration
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
        """
        Processes the dataframe creating a new column containing all information post-preprocessing

        On Return:
            Creates a new column with all the available information as found in the informative
            columns concatenated with new lines.
        """
        col = []

        # TODO: This logic is heavily repeated in error_code_matcher and can to be refactored
        # after we have a fuller picture of the Classifier.
        for _, row in self.df.iterrows():
            messages = []
            # Gather information from only columns that store strings of exception traces
            for column in self.informative_columns:
                if isinstance(row[column], str):
                    messages.append(row[column])
                elif isinstance(row[column], list):
                    for sub_message in row[column]:
                        if isinstance(sub_message, str):
                            messages.append(sub_message)

            joined_line_information = '\n'.join(messages).splitlines()
            joined_line_information = self.filter_lines(joined_line_information)
            joined_line_information = self.search_lines(joined_line_information)
            col.append('\n'.join(joined_line_information))

        # We store the result into a column that only the tokenizer will use in the future
        # This column should NOT be outputted in the final table and is used exclusively internally
        self.df[self.output_column_name] = col
