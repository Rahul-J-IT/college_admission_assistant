import pytest
from agent import detect_intent, augment_query

def test_detect_intent():
    assert detect_intent("what are the required documents for VIT?") == "documents"
    assert detect_intent("how to apply step by step?") == "checklist"
    assert detect_intent("tell me about fee structure") == "fees"
    assert detect_intent("what is the deadline for anna university?") == "deadlines"
    assert detect_intent("minimum percentage for BTech") == "eligibility"
    assert detect_intent("hi, how are you?") == "general"

def test_augment_query():
    # If the user asks for a checklist
    q = "how to apply"
    intent = "checklist"
    aug = augment_query(q, intent)
    assert "how to apply" in aug
    assert "step-by-step" in aug.lower()

    # If general intent, should not augment heavily
    intent = "general"
    aug = augment_query("hello", intent)
    assert aug == "hello"
