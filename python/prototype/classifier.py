"""
Module for Classification of Error Stack Traces
Heavy lifting is done by regular expression matching and KMeans
"""
from string import punctuation
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
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


class Classifier:
    """
    Classifier that for the various computations for the classification of
    errors given by a dataframe of exceptions
    """
    def __init__(self, df):
        """
        To create a Classifier, one must provide the proper pandas dataframe
        gathered from bigquery
        """
        self.dataframe = df


    def error_code_match(self):
        """
        Initial pattern matching to find specific ERRORs specified in the
        configuration file

        On Return:
            Updates the dataframe such that a new column, 'ERRCODE' denotes
            the error code of the exception, if one such exists.
        """
        col = []

        for _, row in self.dataframe.iterrows():
            # The possibly useful columns are exception, remoteException and errorMessage
            vals = [row['exception']] + list(row['remoteException'])
            if row['errorMessage'] is not None:
                vals.append(row['errorMessage'])

            flag = True
            # Check if any of the columns have a match for any of the errors
            for err in config.ERRORS:
                if any([re.search(err, val) for val in vals]):
                    col.append(err)
                    flag = False
                    break

            # In the case no match has been made, append a None
            if flag:
                col.append(None)

        self.dataframe['ERRCODE'] = col


    def cluster_errors(self):
        """
        Clusters errors based on the english error codes as found in their 'exception'
        columns

        Preconditions:
            Assumes that the dataframe populates the 'ERRCODE' field (I.E. error_code_match)
            has already run

        On Return:
            Updates the best k as the number of best clusters and adds a column 'CLUSTERCODE'
            for each exception where clustercode is the cluster in which the exception belongs
            to if applicable.
        """
        to_cluster = self.dataframe[self.dataframe['ERRCODE'].isna()]
        term_freq = CountVectorizer(tokenizer=error_tokenize).fit_transform(to_cluster['exception'])
        normalized = preprocessing.normalize(term_freq)

        sil = []
        labels = []
        for k in range(config.MIN_CLUSTER, config.MAX_CLUSTER):
            k_cluster = KMeans(n_clusters=k).fit(normalized)
            sil.append(silhouette_score(normalized, k_cluster.labels_, metric='euclidean'))
            labels.append(k_cluster.labels_)

        best_labels = labels[sil.index(max(sil))]

        self.dataframe.loc[self.dataframe['ERRCODE'].isna(), 'CLUSTERCODE'] = best_labels


    def generate_message(self):
        """
        Processes the dataframe such that a new column, 'ERRMSG' contains
        the human readable stack trace message from the exception column
        """
        self.dataframe['ERRMSG'] = process_stack_trace(self.dataframe['exception'])


    def compute_results(self):
        """
        Computes classification results using error code matching and clustering
        """
        self.error_code_match()
        self.generate_message()
        self.cluster_errors()


    def report_results(self):
        """
        Prints the results in a friendly format, Error Code / Error Message, Count
        """
        # Prints the unique Error Codes and their counts
        error_dataframe = self.dataframe['ERRCODE'].value_counts().to_frame()
        error_dataframe = error_dataframe.rename(columns={'ERRCODE': 'COUNT'})
        print(error_dataframe)

        clusters = self.dataframe['CLUSTERCODE'].dropna().unique()
        np.sort(clusters)
        counts = self.dataframe['CLUSTERCODE'].value_counts().to_frame()
        col = []
        for cluster in clusters:
            col.append(
                self.dataframe[self.dataframe['CLUSTERCODE'] == cluster].iloc[0]['exception'][:50])
        counts = counts.rename(index=dict(zip(clusters, col)))
        counts = counts.rename(columns={'CLUSTERCODE': 'COUNT'})
        print(counts)
