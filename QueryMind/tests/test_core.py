import unittest
from clarification.detector import detect_ambiguity
from clarification.resolver import merge_clarifications
from evaluation.metrics import binary_metrics
from llm.structured_output import parse_json_object
from schema.profiler import profile_schema

class QueryMindUnitTests(unittest.TestCase):
    def test_ambiguous_ranking(self):
        self.assertTrue(detect_ambiguity("Show top students")["needs_clarification"])

    def test_clear_question(self):
        self.assertFalse(detect_ambiguity("Show students with marks above 80")["needs_clarification"])

    def test_merge_clarifications(self):
        result = merge_clarifications("Show top students", [{"question": "Rank by?", "answer": "marks"}])
        self.assertIn("marks", result["resolved_question"])

    def test_parse_json_fenced(self):
        self.assertEqual(parse_json_object('```json\\n{"sql":"SELECT 1"}\\n```')["sql"], "SELECT 1")

    def test_metrics(self):
        result = binary_metrics(3, 1, 1)
        self.assertAlmostEqual(result["precision"], 0.75)
        self.assertAlmostEqual(result["recall"], 0.75)

    def test_profile_schema(self):
        result = profile_schema({"tables": {"students": {"row_count": 4, "columns": [{"name": "id"}]}}})
        self.assertEqual(result["total_rows"], 4)

if __name__ == "__main__":
    unittest.main()
