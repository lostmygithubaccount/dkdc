#!/usr/bin/env bash

cd tests/scenarios
python -c "from utilities.helpers.app_insights_helpers import log_test_results_from_python_unit_test; log_test_results_from_python_unit_test('$1', $2, $3, ${4:-True}, ${5:-True}, None, None, ${6:-{\}})"
