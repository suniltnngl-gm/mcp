"""Tests for custom rules engine"""
import pytest
from code_review_toolkit.custom_rules import CustomRule, CustomRuleEngine


def test_custom_rule_creation():
    """Test custom rule can be created"""
    rule = CustomRule(
        name="test-rule",
        pattern=r"print\(",
        severity="low",
        category="style",
        message="Test message",
        suggestion="Test suggestion",
        file_types=[".py"],
        enabled=True
    )
    assert rule.name == "test-rule"
    assert rule.enabled is True
