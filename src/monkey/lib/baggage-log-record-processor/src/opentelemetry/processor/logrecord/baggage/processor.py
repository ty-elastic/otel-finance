from typing import Callable

from opentelemetry import context
from opentelemetry.baggage import get_all as get_all_baggage
from opentelemetry.sdk import _logs as logs
from opentelemetry.sdk._logs.export import LogExporter

# A BaggageKeyPredicate is a function that takes a baggage key and returns a boolean
BaggageKeyPredicateT = Callable[[str], bool]

# A BaggageKeyPredicate that always returns True, allowing all baggage keys to be added to spans
ALLOW_ALL_BAGGAGE_KEYS: BaggageKeyPredicateT = lambda _: True  # noqa: E731

class BaggageLogRecordProcessor(logs.LogRecordProcessor):
    """
    The BaggageLogRecordProcessor reads entries stored in Baggage
    from the parent context and adds the baggage entries' keys and
    values to the span as attributes on span start.

    Add this span processor to a log provider.

    Keys and values added to Baggage will appear on subsequent LogRecords
    for a trace within this service.

    ⚠ Warning ⚠️

    Do not put sensitive information in Baggage.

    """

    def __init__(self, baggage_key_predicate: BaggageKeyPredicateT) -> None:
        self._baggage_key_predicate = baggage_key_predicate
        self._shutdown = False

    def emit(
        self, log_data: logs.LogData
    ) -> None:
        if self._shutdown:
            # Processor is already shutdown, ignoring call
            return
        baggage = get_all_baggage(context.get_current())
        for key, value in baggage.items():
            if self._baggage_key_predicate(key):
                log_data.log_record.attributes[key] = value
                
    def shutdown(self):
        self._shutdown = True
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:  # pylint: disable=no-self-use
        return True