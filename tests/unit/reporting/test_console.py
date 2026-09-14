from app.reporting.models import TestReport as ReportModel


def test_report_decision_for_rejected_null_hypothesis():
	report = ReportModel("angle", "Angle test", 2.0, 1.64, 0.05, True)

	assert report.decision == "REJECT H0"


def test_report_decision_for_non_rejected_null_hypothesis():
	report = ReportModel("angle", "Angle test", 0.5, 1.64, 0.05, False)

	assert report.decision == "DO NOT REJECT H0"
