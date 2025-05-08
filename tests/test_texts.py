import pytest
from unittest.mock import patch


from texts import getWaitText, start_generation_text, wait_texts, help_text


def test_get_wait_text_zero_case():
    result = getWaitText(0)
    assert result == start_generation_text


@patch('texts.choice')
def test_get_wait_text_non_zero_case(mock_choice):
    mock_choice.return_value = wait_texts[0]
    for num in [1, 2, 5]:
        result = getWaitText(num)
        assert result in wait_texts
    mock_choice.assert_called_with(wait_texts)


def test_module_level_variables_coverage():
    assert isinstance(wait_texts, list)
    assert len(wait_texts) == 3
    assert isinstance(help_text, str)
    assert len(help_text) > 100
