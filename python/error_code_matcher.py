"""
Module for Pattern Matching To Error Codes phase of the Stack Trace Classifier
"""
import re

class ErrorCodeMatcher:
    """
    Classifier that performs the pattern matching on error codes
    of the pandas data frame based on the configuration file.

    Params:
        df: A pandas dataframe consisting of the exception column, a name
            column, an errorMessage column and optionally a remoteException
            column

        config: A configuration file in the format as specified by the
            config.proto.
    """
    def __init__(self, df, config):
        """
        Preconditions: config has field error_code_matcher not None
        """
        self.df = df
        self.informative_columns = config.informative_column
        self.initialize_informative_errors(config)
        self.output_column_name = config.error_code_matcher.output_column_name


    def initialize_informative_errors(self, config):
        """
        Populates the default informative errors using the informative_errors protobuf

        Args:
            ignore_error_list: a list of errors to explicitly blacklist from the
            the list of informative errors
        """
        errors = []
        # find all enum descriptors in error_code_matcher protobuf
        for field in config.error_code_matcher.DESCRIPTOR.fields:
            if field.enum_type:
                # minor gymnastics to find value of attribute without actually knowing its name
                ignore_errs_attr = getattr(config.error_code_matcher, field.name)
                ignore_errs = [field.enum_type.values[enum].name for enum in ignore_errs_attr]

                for err_name in field.enum_type.values_by_name:
                    if err_name not in ignore_errs:
                        errors.append(err_name)
        self.informative_errors = errors


    def match_informative_errors(self):
        """
        Main heavy lifting to find specific ERRORs to match to

        Note, in the event that multiple errors codes exist in the error
        message, the first error message that occurs in self.informative_errors
        is matched to (this should not happen under normal circumstances)

        On Return:
            Updates the dataframe such that a new column, 'ERRCODE' denotes
            the error code of the exception, if one such exists.
        """
        col = []

        for _, row in self.df.iterrows():
            messages = []
            # Gather information from only columns that store strings of exception traces
            for column in self.informative_columns:
                # columns like "exception" are strings
                if isinstance(row[column], str):
                    messages.append(row[column])
                # columns like "remoteException" are lists of strings
                elif isinstance(row[column], list):
                    for sub_message in row[column]:
                        if isinstance(sub_message, str):
                            messages.append(sub_message)

            no_error_matched = True
            # Check if any of the columns have a match for any of the errors
            for err in self.informative_errors:
                if any([re.search(err, message) for message in messages]):
                    col.append(err)
                    no_error_matched = False
                    break

            # In the case no match has been made, append a None
            if no_error_matched:
                col.append(None)

        self.df[self.output_column_name] = col
