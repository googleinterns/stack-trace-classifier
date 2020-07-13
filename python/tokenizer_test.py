"""
Unittest module for Tokenizers
"""
import unittest
import proto.config_pb2
from tokenizer import Tokenizer

class TokenizerTest(unittest.TestCase):
    """
    Unit test case suite for our tokenizers in our Tokenizer class
    """

    def setUp(self):
        """
        General setup for configuration files
        """
        # configuration for human readable Tokenizer
        human_readable_config = proto.config_pb2.Config()
        human_readable_config.clusterer.tokenizer.token_min_length = 2
        human_readable_config.clusterer.tokenizer.mode = proto.config_pb2.Tokenizer.TokenizerMode.HUMAN_READABLE
        human_readable_config.clusterer.tokenizer.split_on.extend(['='])
        human_readable_config.clusterer.tokenizer.punctuation.extend([':', '/', '\n', '\t'])
        self.human_readable_tokenizer = Tokenizer(human_readable_config)

        # configuration for stack trace Tokenizer
        stack_trace_config = proto.config_pb2.Config()
        stack_trace_config.clusterer.tokenizer.token_min_length = 0
        stack_trace_config.clusterer.tokenizer.mode = proto.config_pb2.Tokenizer.TokenizerMode.STACK_TRACE_LINES
        self.stack_trace_tokenizer = Tokenizer(stack_trace_config)


    def test_human_readable_tokenizer(self):
        """
        Test suite for human_readable_tokenizer
        """
        # our tokenizer gets rid of sequences of numbers and keeps 'words'
        simple_string = 'subscription id 11444512 failed because it was cancelled'
        simple_tokens = ['subscription', 'id', 'failed', 'because', 'it', 'was', 'cancelled']
        self.assertTrue(self.human_readable_tokenizer.human_readable_tokenizer(simple_string) == simple_tokens)

        # our configured tokenizer also splits on '=',
        # extracting subscription=1114125 to subscription, 1114125 the later of which is removed
        extra_split_test = 'subscription=1114125 failed because of id=1124125 from client=STADIA'
        split_tokens = ['subscription', 'failed', 'because', 'of', 'id', 'from', 'client', 'stadia']
        self.assertTrue(self.human_readable_tokenizer.human_readable_tokenizer(extra_split_test) == split_tokens)


    def test_stack_trace_line_tokenizer(self):
        """
        Test suite for stack_trace_line_tokenizer
        """
        # example stack trace we would want to extract from
        sample_stack_trace = open('testdata/tokenizer/sample_stack_trace.txt').read()
        sample_extracted_lines = [
            'com.google.moneta.purchaseorder.monetizer.PurchaseOrderUsageTransaction.lambda$getMovementCode$0',
            'java.util.Optional.orElseThrow',
            'com.google.moneta.purchaseorder.monetizer.PurchaseOrderUsageTransaction.getMovementCode',
            'com.google.moneta.purchaseorder.monetizer.PurchaseOrderUsageTransaction.createRevenueMovement',
            'com.google.moneta.purchaseorder.monetizer.PurchaseOrderUsageTransaction.addLineItem',
            'com.google.moneta.purchaseorder.monetizer.PurchaseOrderUsageTransaction.addAllLineItems',
            'com.google.moneta.purchaseorder.service.purchaseorder.purchaseorderinternal.ChargeAction.charge'
        ]
        self.assertTrue(self.stack_trace_tokenizer.stack_trace_line_tokenizer(sample_stack_trace) == sample_extracted_lines)


if __name__ == "__main__":
    unittest.main()