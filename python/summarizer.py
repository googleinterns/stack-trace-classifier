"""
Module for summarization of the errors collected in the classification phase
"""
import pandas as pd

class Summarizer:
    """
    Class for presenting the information given by the classifier algorithms and presenting
    them in a readable format

    Params:
        df: A pandas dataframe that has finished running the various classification algorithms
            as defined in config

        config: A configuration file in the format as specified by the
            config.proto.
    """
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
            A dataframe with the same information exception with the cols_to_reorganize occuring first
        """
        dataframe_cols = set(dataframe.columns)
        other_cols = dataframe_cols ^ cols_to_reorganize
        cols_list = list(cols_to_reorganize)
        # Ensure the column 'SIZE' appears last
        cols_list.append(cols_list.pop(cols_list.index('SIZE')))
        return dataframe.loc[:, cols_list + list(other_cols)]


    def generate_summary(self):
        """
        Outputs a summary of the various error codes and clusters with their counts in a readable
        dataframe format.

        Returns:
            A dataframe of summary consisting of the error_code / cluster_code, size of the group and
            a list of the rest of the informative error informations.

        Note: directly using a to_gbq on this dataframe will produce columns consisting of arrays since
        pandas does not naturally support the repeated fields that GBQ does
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
        joined_dataframe = pd.concat(output_dataframes)
        return self.reorganize_dataframe(joined_dataframe, cols_to_reorganize)
