import pytest
from sentinel.worker.alert_engine import evaluate_error_count, evaluate_error_rate


def test_evaluate_error_count_below_threshold():
    assert evaluate_error_count(count=5, threshold=10) is False


def test_evaluate_error_count_above_threshold():
    assert evaluate_error_count(count=15, threshold=10) is True


def test_evaluate_error_rate_below_threshold():
    assert evaluate_error_rate(rate=0.5, threshold=1.0) is False


def test_evaluate_error_rate_above_threshold():
    assert evaluate_error_rate(rate=2.0, threshold=1.0) is True
