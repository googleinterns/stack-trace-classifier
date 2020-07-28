"""Module for K-Means Clustering of data points."""
from preprocessor import Preprocessor
import proto.config_pb2 as config_pb2
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score
from tokenizer import Tokenizer


class KMeansClusterer:
  """Class for K-Means Clustering of input data."""

  def __init__(self, df, config):
    """Initializes various data required for Clusterer.

    Args:
      df: A pandas dataframe consisting of the exception column, a name
        column, an errorMessage column and optionally a remoteException
        column

      config: A configuration file in the format as specified by the
        config.proto.
    """
    self.df = df

    # internal column name for our Preprocessor
    self.internal_column_name = '_internal_preprocessor_output_col_'

    # run the preprocessor
    # (even if no config given preprocessor generates internal column)
    preprocessor = Preprocessor(df, config, self.internal_column_name)
    preprocessor.process_dataframe()

    # get the appropriate tokenization method
    tokenizer = Tokenizer(config)
    if config.clusterer.tokenizer.mode == config_pb2.Tokenizer.TokenizerMode.HUMAN_READABLE:
      self.tokenization_method = tokenizer.human_readable_tokenizer
    elif config.clusterer.tokenizer.mode == config_pb2.Tokenizer.TokenizerMode.STACK_TRACE_LINES:
      self.tokenization_method = tokenizer.stack_trace_line_tokenizer
    # if no valid tokenization mode is chosen, error
    else:
      raise NotImplementedError(
          'No valid tokenization mode in configuration file')

    # get whether or not to use minibatch
    self.mini_batch = config.clusterer.mini_batch

    # get min and max clusters
    self.min_cluster = config.clusterer.min_cluster
    self.max_cluster = config.clusterer.max_cluster

    self.output_column_name = config.clusterer.output_column_name

  def cluster_errors(self):
    """Clusters errors based on the various configurations passed in.

    Preconditions:
      Assumes that Preprocessor has already run and has processed the data

    On Return:
      Adds a column 'CLUSTERCODE' for each exception where clustercode is the cluster in
        which the exception belongs to if applicable.
    """
    # Vectorize the input using CountVectorizer
    term_freq_matrix = CountVectorizer(
        tokenizer=self.tokenization_method).fit_transform(
            self.df[self.internal_column_name])
    # normalize in case of repeats
    normalized_matrix = preprocessing.normalize(term_freq_matrix)

    silhouette_scores = []
    labels = []
    # run K-Means for each k between min_cluster and max_cluster
    # then calculate silhouette score
    for k in range(self.min_cluster, self.max_cluster):
      if self.mini_batch:
        # MiniBatch should only be used on < 1000 sample points
        # in order to achieve good results for large k,
        # we need a large batch_size number
        # 1000 should suffice for all use cases of our current Classifier
        k_cluster = MiniBatchKMeans(n_clusters=k,
                                    batch_size=1000).fit(normalized_matrix)
      else:
        k_cluster = KMeans(n_clusters=k).fit(normalized_matrix)
      silhouette_scores.append(
          silhouette_score(normalized_matrix,
                           k_cluster.labels_,
                           metric='euclidean'))
      labels.append(k_cluster.labels_)

    # label each error using the 'best' silhouette label
    best_labels = labels[silhouette_scores.index(max(silhouette_scores))]
    # convert to string for consistency
    best_labels = list(map(str, best_labels))

    # Label each exception with a cluster tag
    self.df[self.output_column_name] = best_labels
