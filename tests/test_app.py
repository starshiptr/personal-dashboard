from streamlit.testing.v1 import AppTest


def test_app_boots():
    at = AppTest.from_file("app.py").run(timeout=30)
    assert not at.exception


def test_budget_delta_goes_negative_when_over():
    from logic import budget_delta
    assert budget_delta(14033, 10000) == "-₹4,033 over"
    assert budget_delta(9000, 10000) == "₹1,000 left"