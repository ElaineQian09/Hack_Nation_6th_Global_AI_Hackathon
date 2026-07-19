import os
import unittest
from unittest.mock import patch

from backend.services import databricks_ai_service as ai


DETAIL_FIXTURE = {
    "facility": {
        "facility_id": "facility-1",
        "name": "Example Hospital",
        "facilityTypeId": "hospital",
        "description": "The facility has a current ICU with ventilator support.",
        "capability": ["ICU", "Emergency"],
        "equipment": ["Ventilator support", "Oxygen line"],
        "procedure": ["Patients are referred elsewhere for oncology care."],
        "specialties": ["internalMedicine", "emergencyMedicine"],
        "capacity": 100,
        "numberDoctors": 25,
    },
    "assessment": {
        "facility_id": "facility-1",
        "facility_name": "Example Hospital",
        "selected_capability": "ICU",
        "trust_score": 88,
        "trust_label": "Trusted",
        "confidence_level": "Medium",
        "claim_present": True,
        "support_signals": ["equipment: Ventilator support"],
        "warning_signals": [],
        "missing_signals": [],
        "reason_summary": "ICU is supported by equipment evidence.",
        "description_text": "The facility has a current ICU with ventilator support.",
        "capability_text": ["ICU", "Emergency"],
        "equipment_text": ["Ventilator support", "Oxygen line"],
        "procedure_text": ["Patients are referred elsewhere for oncology care."],
        "specialties": ["internalMedicine", "emergencyMedicine"],
        "capacity": 100,
        "number_doctors": 25,
    },
}


class AIReviewerTests(unittest.TestCase):
    def test_exact_quote_found_in_string_field(self):
        citation = ai.AICitation(
            source_field="description",
            exact_quote="current ICU with ventilator support",
            relation="supports",
        )

        self.assertTrue(
            ai.citation_exists_in_source(
                citation,
                {"description": "The facility has a current ICU with ventilator support."},
            )
        )

    def test_exact_quote_found_in_list_field(self):
        citation = ai.AICitation(
            source_field="equipment",
            exact_quote="ventilator support",
            relation="supports",
        )

        self.assertTrue(
            ai.citation_exists_in_source(
                citation,
                {"equipment": ["Ventilator support", "Oxygen line"]},
            )
        )

    def test_hallucinated_quote_is_rejected(self):
        citation = ai.AICitation(
            source_field="equipment",
            exact_quote="ECMO machine",
            relation="supports",
        )

        self.assertFalse(
            ai.citation_exists_in_source(
                citation,
                {"equipment": ["Ventilator support", "Oxygen line"]},
            )
        )

    def test_supported_verdict_downgraded_when_every_citation_invalid(self):
        review = ai.AIReviewModel(
            verdict="supported",
            confidence="high",
            explanation="The model claims support.",
            citations=[
                ai.AICitation(
                    source_field="equipment",
                    exact_quote="ECMO machine",
                    relation="supports",
                )
            ],
            missing_information=[],
            warnings=[],
        )

        validated = ai.validate_ai_review(review, {"equipment": ["Ventilator support"]})

        self.assertEqual(validated.verdict, "insufficient_data")
        self.assertEqual(validated.confidence, "low")
        self.assertEqual(validated.citations, [])
        self.assertEqual(len(validated.rejected_citations), 1)
        self.assertTrue(any("downgraded" in warning for warning in validated.warnings))

    def test_missing_serving_endpoint_handled_without_model_call(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(ai, "get_facility_detail", return_value=DETAIL_FIXTURE):
                response = ai.generate_ai_summary("facility-1", "ICU")

        self.assertFalse(response["available"])
        self.assertEqual(response["verdict"], "insufficient_data")
        self.assertIn("SERVING_ENDPOINT", response["warnings"][0])

    def test_malformed_model_json_handled_without_stack_trace(self):
        with patch.dict(os.environ, {"SERVING_ENDPOINT": "validator-model"}, clear=True):
            with patch.object(ai, "get_facility_detail", return_value=DETAIL_FIXTURE):
                with patch.object(ai, "query_databricks_endpoint", return_value="not json"):
                    response = ai.generate_ai_summary("facility-1", "ICU")

        self.assertFalse(response["available"])
        self.assertEqual(response["verdict"], "insufficient_data")
        self.assertIn("malformed JSON", response["explanation"])


if __name__ == "__main__":
    unittest.main()
