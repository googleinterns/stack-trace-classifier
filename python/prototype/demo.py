"""Demo module for running classifier.py."""
from classifier import Classifier

from google.cloud import bigquery

if __name__ == "__main__":
  # Example of how to use the above code
  client = bigquery.Client()
  # Note: this is tied to my personal credentials
  # which have access to the table YMMV
  QUERY = "SELECT * FROM `payments-purchaseorder.debuginfo.test4`"
  dataframe = client.query(QUERY).result().to_dataframe()
  classifier = Classifier(dataframe)
  classifier.compute_results()
  classifier.report_results()
