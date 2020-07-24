"""Module for Classification of Error Stack Traces.

Heavy lifting is done by regular expression matching and KMeans
"""
import datetime
import re

import config
from human_readable_tokenizer import process_stack_trace
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score
from stack_trace_tokenizer import error_tokenize


class Classifier:
  """Classifier that for the various computations for the classifying errors."""

  def __init__(self, df):
    """Initialize dataframe necessary for classifier.

    Args:
      df: dataframe for classification algorithm.
    """
    self.dataframe = df

  def error_code_match(self):
    """Initial pattern matching to find specific ERRORs.

    On Return:
      Updates the dataframe such that a new column, 'ERRCODE' denotes
        the error code of the exception, if one such exists.
    """
    col = []

    for _, row in self.dataframe.iterrows():
      # The possibly useful columns are exception, remoteException, errorMessage
      vals = [row['exception']] + list(row['remoteException'])
      if row['errorMessage'] is not None:
        vals.append(row['errorMessage'])

      no_error_matched = True
      # Check if any of the columns have a match for any of the errors
      for err in config.ERRORS:
        if any([re.search(err, val) for val in vals]):
          col.append(err)
          no_error_matched = False
          break

      # In the case no match has been made, append a None
      if no_error_matched:
        col.append(None)

    self.dataframe['ERRCODE'] = col

  def cluster_errors(self):
    """Clusters errors based on the english error codes as found in 'exception'.

    Preconditions:
      Assumes that the dataframe populates the 'ERRCODE' field (I.E. error_code_match)
        has already run

    On Return:
      Updates the best k as the number of best clusters and adds a column 'CLUSTERCODE'
        for each exception where clustercode is the cluster in which the exception belongs
        to if applicable.
    """
    to_cluster = self.dataframe[self.dataframe['ERRCODE'].isna()]
    term_freq = CountVectorizer(tokenizer=error_tokenize).fit_transform(
        to_cluster['exception'])
    normalized = preprocessing.normalize(term_freq)

    sil = []
    labels = []
    for k in range(config.MIN_CLUSTER, config.MAX_CLUSTER):
      k_cluster = KMeans(n_clusters=k).fit(normalized)
      sil.append(
          silhouette_score(normalized, k_cluster.labels_, metric='euclidean'))
      labels.append(k_cluster.labels_)

    best_labels = labels[sil.index(max(sil))]

    self.dataframe.loc[self.dataframe['ERRCODE'].isna(),
                       'CLUSTERCODE'] = best_labels

  def generate_message(self):
    """Processes the dataframe such that a new column, 'ERRMSG'.

    This column contains the human readable stack trace message 
      from the exception column.
    """
    self.dataframe['ERRMSG'] = process_stack_trace(self.dataframe['exception'])

  def compute_results(self):
    """Computes classification results using error code matching and clustering."""
    self.error_code_match()
    self.generate_message()
    self.cluster_errors()

  def report_results(self):
    """Prints the results in a friendly format.

    Contains the columns Error Code / Error Message, Count
    Writes this result to a table in BQ with the format resultSummary + date

    Preconditions:
      Assumes that compute_results has run
    """
    # Prints the unique Error Codes and their counts
    error_dataframe = self.dataframe['ERRCODE'].value_counts().to_frame()
    error_dataframe = error_dataframe.rename(columns={'ERRCODE': 'COUNT'})

    clusters = self.dataframe['CLUSTERCODE'].dropna().unique()
    np.sort(clusters)
    counts = self.dataframe['CLUSTERCODE'].value_counts().to_frame()
    col = []
    for cluster in clusters:
      col.append(self.dataframe[self.dataframe['CLUSTERCODE'] ==
                                cluster].iloc[0]['exception'])
    counts.rename(index=dict(zip(clusters, col)), inplace=True)
    counts.rename(columns={'CLUSTERCODE': 'COUNT'}, inplace=True)

    concatenated = pd.concat([error_dataframe, counts])
    print(concatenated)

    date = str(datetime.date.today())
    date = date.replace('-', '_')
    table_name = config.TABLE_NAME + date
    concatenated.reset_index(level=0, inplace=True)
    concatenated.rename(columns={'index': 'ERROR_TYPE'}, inplace=True)
    concatenated.to_gbq(table_name, config.PROJECT_NAME)
