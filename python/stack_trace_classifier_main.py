"""Demo module for running classification algorithms and summarizer."""
from error_code_matcher import ErrorCodeMatcher
from k_means_clusterer import KMeansClusterer
import pandas_gbq
import proto.big_query_config_pb2 as big_query_config_pb2
import proto.config_pb2 as config_pb2
from summarizer import Summarizer

from absl import app
from absl import flags
from google.cloud import bigquery
from google.protobuf import text_format


def get_input_dataframe_table(project_id, dataset_id, input_table_id, client):
  """Attempts to get an input dataframe utilizing the bigquery configurations.

  Args:
    project_id: project id of the bigquery table we are reading from

    dataset_id: dataset id of the bigquery table we are reading from

    input_table_id: table name of the bigquery table we are reading from

  Returns:
    A dataframe read from the credentials and information provided in args.
  """
  dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
  table_ref = dataset_ref.table(input_table_id)
  table = client.get_table(table_ref)
  return client.list_rows(table).to_dataframe()


def output_dataframe_to_gbq(output_dataframe, project_id, dataset_id,
                            output_table_id):
  """Writes back to big query the results of the summarized dataframe, output_dataframe.

  Args:
    output_dataframe: dataframe we are writing to bigquery

    project_id: project id of the bigquery table we are writing to

    dataset_id: dataset id of the bigquery table we are writing to

    output_table_id: output table name of the bigquery table we are writing to

  On Return:
    Writes the output dataframe to bigquery
  """
  pandas_gbq.to_gbq(output_dataframe,
                    dataset_id + '.' + output_table_id,
                    project_id=project_id)


def run_classification_summary(df, classifier_config):
  """Runs the various classification algorithms outputting a summary dataframe.

  Args:
    df: input dataframe containing the error information we wish to classify and summarize

    classifier_config: configuration file expected to be in the format of config.proto

  Returns:
    pandas dataframe that summarizes the information obtained from the classification algorithms
      run on the input dataframe
  """
  # Running our classifiers
  error_code_matcher = ErrorCodeMatcher(df, classifier_config)
  error_code_matcher.match_informative_errors()
  k_means_classifier = KMeansClusterer(df, classifier_config)
  k_means_classifier.cluster_errors()

  # Running the summarizer
  summarizer = Summarizer(df, classifier_config)
  return summarizer.generate_summary()


FLAGS = flags.FLAGS
flags.DEFINE_string(
    'config', None,
    'configuration file path, expected to be in the format as outlined by config.proto'
)
flags.DEFINE_string(
    'big_query_config', None,
    'big query configuration file path to pass in expected to be in format of big_query_config.proto'
)
flags.mark_flag_as_required('config')
# future flag arguments, i.e. plx workflow client, can go here


def main(argv):
  # Read classifier configurations from proto file passed in
  classifier_config_path = FLAGS.config
  classifier_config = config_pb2.Config()
  classifier_file = open(classifier_config_path, 'r')
  classifier_config = text_format.Parse(classifier_file.read(),
                                        classifier_config)

  if FLAGS.big_query_config:
    # Personal Client, YMMV.
    # In the future, change this to plx workflow client, or BQ service agent
    client = bigquery.Client()
    # Read BQ configurations from proto file passed in
    big_query_config_path = FLAGS.big_query_config
    big_query_config = big_query_config_pb2.BigQueryConfig()
    big_query_file = open(big_query_config_path, 'r')
    big_query_config = text_format.Parse(big_query_file.read(),
                                         big_query_config)
    # BigQuery Schematics
    df = get_input_dataframe_table(big_query_config.project_id,
                                   big_query_config.dataset_id,
                                   big_query_config.input_table_id, client)

    output_df = run_classification_summary(df, classifier_config)
    output_dataframe_to_gbq(output_df, big_query_config.project_id,
                            big_query_config.dataset_id,
                            big_query_config.output_table_id)


if __name__ == "__main__":
  app.run(main)
