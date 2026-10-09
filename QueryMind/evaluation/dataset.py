"""Starter evaluation set; expand to at least 50 reviewed cases before reporting metrics."""
TEST_CASES = [
    {"question": "List all students", "expected_sql_contains": "students", "ambiguous": False},
    {"question": "Show top students", "expected_sql_contains": "students", "ambiguous": True},
    {"question": "Count departments", "expected_sql_contains": "COUNT", "ambiguous": False},
    {"question": "Show students with marks above 80", "expected_sql_contains": "marks", "ambiguous": False},
    {"question": "Show student names with department names", "expected_sql_contains": "departments", "ambiguous": False},
]
