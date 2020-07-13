"""
Demo module for running classification algorithms and summarizer.
"""
import argparse
from google.cloud import bigquery
from google.protobuf import text_format
import pandas_gbq
import proto.config_pb2
import proto.big_query_config_pb2
from k_means_clusterer import KMeansClusterer
from error_code_matcher import ErrorCodeMatcher
from summarizer import Summarizer

def get_input_dataframe_table(project_id, dataset_id, input_table_id):
    """
    Attempts to get an input dataframe utilizing the bigquery configurations
    """
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    table_ref = dataset_ref.table(input_table_id)
    table = client.get_table(table_ref)
    return client.list_rows(table).to_dataframe()


def output_dataframe_to_gbq(output_dataframe, project_id, dataset_id, output_table_id):
    """
    Writes back to big query the results of hte summarized dataframe, output_dataframe
    """
    pandas_gbq.to_gbq(output_dataframe, dataset_id + '.' + output_table_id, project_id=project_id)


if __name__ == "__main__":
    # future CLI args can go here following the same format
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--config',
        nargs=1,
        type=str,
        required=True,
        help='configuration file path, expected to be in the format as outlined in config.proto'
    )
    arg_parser.add_argument(
        '--bigquery_config',
        nargs=1,
        type=str,
        help='bigquery configuration file path to pass in expected to be in format of big_query_config.proto'
    )

    args = arg_parser.parse_args()

    # Read classifier configurations from proto file passed in
    classifier_config_path = args.config[0]
    classifier_config = proto.config_pb2.Config()
    classifier_file = open(classifier_config_path, 'r')
    classifier_config = text_format.Parse(classifier_file.read(), classifier_config)

    if args.bigquery_config:
        # Personal Client, YMMV.
        # TODO: Change this to plx workflow client, or BQ service agent
        client = bigquery.Client()
        # Read BQ configurations from proto file passed in
        bigquery_config_path = args.bigquery_config[0]
        bigquery_config = proto.big_query_config_pb2.BigQueryConfig()
        bigquery_file = open(bigquery_config_path, 'r')
        bigquery_config = text_format.Parse(bigquery_file.read(), bigquery_config)
        # BigQuery Schematics
        df = get_input_dataframe_table(bigquery_config.project_id, bigquery_config.dataset_id, bigquery_config.input_table_id)

        # Running our classifiers
        error_code_matcher = ErrorCodeMatcher(df, classifier_config)
        error_code_matcher.match_informative_errors()
        k_means_classifier = KMeansClusterer(df, classifier_config)
        k_means_classifier.cluster_errors()

        # Running the summarizer
        summarizer = Summarizer(df, classifier_config)
        output_df = summarizer.generate_summary()
        output_dataframe_to_gbq(output_df, bigquery_config.project_id, bigquery_config.dataset_id, bigquery_config.output_table_id)
