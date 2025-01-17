"""Configuration module used by classifier.py."""
import re
import nltk

TABLE_NAME = 'debuginfo.resultsSummary'

PROJECT_NAME = 'payments-purchaseorder'

LINE_FILTERS = [re.compile(r'\tat'), re.compile(r'Suppressed')]

LINE_MATCHES = [re.compile(r':')]

ERRORS = [
    r'SERVER_INTERRUPTED',
    r'SERVER_PERSISTENCE_ERROR',
    r'SERVER_ERROR_SET_IN_RESPONSE_BY_ACTION',
    r'SERVER_ERROR_NOT_SEEDED_GUICE_EXCEPTION',
    r'SERVER_NOT_A_TRANSACTION_ACTION_EXCEPTION',
    r'SERVER_MESSAGE_INSTANTIATION_EXCEPTION',
    r'SERVER_NOT_IMPLEMENTED_EXCEPTION',
    r'SERVER_EXPERIMENT_DIVERSION_FAILURE',
    r'SERVER_EXPERIMENT_OVERRIDE_FAILURE',
    r'SERVER_REMOTE_FRAMEWORK_ERROR',
    r'SERVER_TIMEOUT_ERROR',
    r'SERVER_RESPONSE_CAN_NOT_BE_THE_DEFAULT_INSTANCE',
    r'SERVER_INVALID_AUTH_CONTEXT',
    r'STORAGE_LIFECYCLE_CHANGE_NOT_ALLOWED',
    r'STORAGE_INVALID_STATE',
    r'STORAGE_UNIT_OF_WORK_NOT_SEEDED',
    r'STORAGE_STATS_COLLECTION_FAILED',
    r'STORAGE_DEADLINE_EXCEEDED',
    r'STORAGE_SETTING_F1_SNAPSHOT_TIMESTAMP_IS_DISALLOWED',
    r'STORAGE_PAGINATED_DISALLOWED_IN_CHILD_REQUEST',
    r'STORAGE_STALE_LOCK_TIMESTAMP',
    r'STORAGE_DATA_CONSTRAINT_VIOLATION',
    r'STORAGE_LEGACY_ENTITY_NOT_FOUND',
    r'STORAGE_BATCH_READ_WRITE_MIX_NOT_ALLOWED',
    r'STORAGE_BATCH_INCONSISTENT_CHILD_PAGINATION_TIMESTAMPS',
    r'STORAGE_BATCH_PARENT_UNIT_OF_WORK_INVALID',
    r'STORAGE_PAGINATED_DISALLOWED_WITHOUT_SNAPSHOT_TIMESTAMP',
    # SERVER_UNEXPECTED_EXCEPTION is uninformative,
    # thus we have removed it from our list of errors
    # r'SERVER_UNEXPECTED_EXCEPTION',
    r'RPC.CANCELLED',
    r'RPC.UNKNOWN',
    r'RPC.INVALID_ARGUMENT',
    r'RPC.DEADLINE_EXCEEDED',
    r'RPC.NOT_FOUND',
    r'RPC.ALREADY_EXISTS',
    r'RPC.PERMISSION_DENIED',
    r'RPC.UNAUTHENTICATED',
    r'RPC.RESOURCE_EXHAUSTED',
    r'RPC.FAILED_PRECONDITION',
    r'RPC.ABORTED',
    r'RPC.OUT_OF_RANGE',
    r'RPC.UNIMPLEMENTED',
    r'RPC.INTERNAL',
    r'RPC.UNAVAILABLE',
    r'RPC.DATA_LOSS'
]

STACK_LINE_FILTERS = [
    # filters for 'general' classes and frameworks
    re.compile(r'com.google.apps.framework'),
    re.compile(r'com.google.moneta.api2.framework'),
    re.compile(r'com.google.common.util'),
    re.compile(r'com.google.net.rpc3'),
    re.compile(r'java.util'),
    re.compile(r'java.lang'),
    # remove anonymous classes
    re.compile(r'\$')
]

MIN_CLUSTER = 2
MAX_CLUSTER = 20

WORDS = frozenset(nltk.corpus.words.words())
