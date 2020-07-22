"""
Module for summarization of the errors collected in the classification phase
"""
import re
import pandas as pd
import numpy as np

class Summarizer:
    """
    Class for presenting the information given by the classifier algorithms and presenting
    them in a readable format

    Params:
        df: A pandas dataframe that has finished running the various classification algorithms
            as defined in config

        config: A configuration file in the format as specified by the
            config.proto.
    
    The summary output dataframe is in the below format:
        error_code / cluster_code : the error code or cluster code of the group
        'SIZE' : the size of the cluster group / error code group
        'CLASS_LINES' : a filtered list of the class lines in this exception group
        'TEXT' : the non-class line information in this exception group
        etc... : other input dataframe columns in list format denoting one error per item.
    """
    JAVA_CLASS_LINE_PREFIX = '\tat'

    def __init__(self, df, config):
        """
        Preconditions:
            config contains a not None field clusterer, tokenizer and preprocessor
        """
        self.df = df
        self.error_code_matcher_has_run = config.HasField('error_code_matcher')
        if self.error_code_matcher_has_run:
            self.error_code_matcher_col = config.error_code_matcher.output_column_name
        self.clusterer_has_run = config.HasField('clusterer')
        if self.clusterer_has_run:
            self.clusterer_col = config.clusterer.output_column_name
        self.n_messages = config.summarizer.n_messages
        self.summary_input_column = config.summarizer.summary_input_column
        self.ignore_lines = [re.compile(st) for st in config.summarizer.ignore_class_line_regex_matcher]
        self.n_class_lines_to_show = config.summarizer.n_class_lines_to_show


    def summarize_exception(self, exception_message_column):
        """
        Method that attempts to extract possibly useful information from input stack-trace messages
        All java class lines found in filters are explicitly excluded from the message.
        Java class line information is accumulated in stack_lines_col
        Whereas all non-java (presumably text information) is included in other_text_lines_col
        Returns:
            tuple of stack_lines_col, other_text_lines_col
                stack_lines_col : list that represents the possibly useful information as found in
                each of the stack trace lines of the chosen message column

                other_text_lines_col : list that represents the possibly useful (text) information
                in each stack trace in the message column
        """
        stack_lines_col = []
        other_text_lines_col = []
        for message_list in exception_message_column:
            # we arbitrarily choose the first message as the representative from the cluster / error group
            exception_message = message_list[0]
            exception_message_lines = exception_message.splitlines()
            # get all stack trace lines
            stack_lines = list(filter(lambda st: st.startswith(self.JAVA_CLASS_LINE_PREFIX), exception_message_lines))
            other_text_lines = list(np.setdiff1d(exception_message_lines, stack_lines))
            other_text_lines = list(filter(lambda w: w, other_text_lines))
            # filter out lines that contain embedded stack trace lines
            other_text_lines = list(filter(lambda w: not re.search(self.JAVA_CLASS_LINE_PREFIX, w), other_text_lines))
            # filtering out class lines that contain uniformative classes.
            for expr in self.ignore_lines:
                stack_lines = list(filter(lambda st: not expr.search(st), stack_lines))
            stack_lines = stack_lines[:self.n_class_lines_to_show]
            stack_lines = list(filter(lambda w: w, stack_lines))
            stack_lines_col.append('\n'.join(stack_lines))
            other_text_lines_col.append('\n'.join(other_text_lines))
        return stack_lines_col, other_text_lines_col


    def summarize_classifier(self, column, cols_to_drop):
        """
        Summarizes the results from the given classification mode determined by column.
        Does not include the information stored in the columns specified in cols_to_drop in output
        The summary includes the first n errors determined by n_messages (as an array since
        pandas does not inherently support repeated fields) as well as the number of errors in the
        cluster / error code group

        Params:
            column: string the classification algorithm that is being summarized denoted by the column
                string it corresponds with

            cols_to_drop: list of columns to drop in the summary dataframe

        Returns:
            a dataframe holding the information
        """
        error_counts = self.df[column].value_counts()
        df_dropped_cols = self.df.drop(columns=cols_to_drop)
        groups = df_dropped_cols.groupby(column).agg(lambda x: list(x)[:self.n_messages])
        groups['SIZE'] = error_counts
        stack_lines_col, text_lines_col = self.summarize_exception(groups[self.summary_input_column])
        groups['TEXT'] = text_lines_col
        groups['CLASS_LINES'] = stack_lines_col
        return groups.reset_index()


    @staticmethod
    def reorganize_dataframe(dataframe, cols_to_reorganize):
        """
        Reorganizes the dataframe such that the columns to reorganize appear first.
        This makes the dataframe more readable during output.
        This method ensures that SIZE is the last column to appear after the possible error codes.

        Params:
            dataframe: dataframe to reorganize the information of

            cols_to_reorganize: columns to be placed first, ahead of the other columns

        Returns:
            A dataframe with the same information exception with the cols_to_reorganize occuring
                first
        """
        dataframe_cols = set(dataframe.columns)
        other_cols = dataframe_cols ^ cols_to_reorganize
        cols_list = list(cols_to_reorganize)
        # Ensure the column 'SIZE' appears last
        cols_list.append(cols_list.pop(cols_list.index('SIZE')))
        cols_list.append(cols_list.pop(cols_list.index('TEXT')))
        cols_list.append(cols_list.pop(cols_list.index('CLASS_LINES')))
        return dataframe.loc[:, cols_list + list(other_cols)]


    def generate_summary(self):
        """
        Outputs a summary of the various error codes and clusters with their counts in a readable
        dataframe format.

        Returns:
            A dataframe of summary consisting of the following columns:
            error_code / cluster_code : the error code or cluster code of the group
            'SIZE' : the size of the cluster group / error code group
            'CLASS_LINES' : a filtered list of the class lines in this exception group
            'TEXT' : the non-class line information in this exception group
            etc... : other input dataframe columns in list format denoting one error per item.

        Note: directly using a to_gbq on this dataframe will produce columns consisting of arrays
        since pandas does not naturally support the repeated fields that GBQ does
        """
        # need to drop added columns in final summary table
        cols_to_drop = ['_internal_proprocessor_output_col_']
        # dataframes to be joined for output
        output_dataframes = []
        # cols to be reordered to the front
        cols_to_reorganize = set()

        # Generate the corresponding data for each classification algorithm
        if self.error_code_matcher_has_run:
            # make sure to drop the other classification column's information since its useless
            # for this classifier
            if self.clusterer_has_run:
                cols_to_drop.append(self.clusterer_col)
            error_code_groups = self.summarize_classifier(self.error_code_matcher_col, cols_to_drop)
            output_dataframes.append(error_code_groups)
            if self.clusterer_has_run:
                cols_to_drop.remove(self.clusterer_col)
            cols_to_reorganize.add(self.error_code_matcher_col)

        if self.clusterer_has_run:
            if self.error_code_matcher_has_run:
                cols_to_drop.append(self.error_code_matcher_col)
            cluster_code_groups = self.summarize_classifier(self.clusterer_col, cols_to_drop)
            output_dataframes.append(cluster_code_groups)
            if self.error_code_matcher_has_run:
                cols_to_drop.remove(self.error_code_matcher_col)
            cols_to_reorganize.add(self.clusterer_col)

        # need to reorganize the columns
        cols_to_reorganize.add('SIZE')
        cols_to_reorganize.add('TEXT')
        cols_to_reorganize.add('CLASS_LINES')
        joined_dataframe = pd.concat(output_dataframes)
        return self.reorganize_dataframe(joined_dataframe, cols_to_reorganize)
