from types import SimpleNamespace

import pytest

from app.modules.interpretation.service import (
    _daily_sign_prompt,
    _extract_output_text,
    _parse_daily_output,
)


def test_extract_output_text_from_responses_api_shape() -> None:
    assert (
        _extract_output_text(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "  Athena yanıtı  "}],
                    }
                ]
            }
        )
        == "Athena yanıtı"
    )


def test_parses_structured_daily_output() -> None:
    result = _parse_daily_output(
        '{"main_theme":" Tema ","relationships":"İlişki","work_money":"İş","caution":"Dikkat"}'
    )
    assert result == {
        "main_theme": "Tema",
        "relationships": "İlişki",
        "work_money": "İş",
        "caution": "Dikkat",
    }


def test_rejects_daily_output_with_missing_section() -> None:
    with pytest.raises(KeyError):
        _parse_daily_output('{"main_theme":"Tema"}')


def test_daily_sign_prompt_contains_date_sign_and_previous_reading() -> None:
    chart_preview = SimpleNamespace(
        positions=[SimpleNamespace(name="moon", sign="leo", degree_in_sign=12.4)]
    )
    prompt = _daily_sign_prompt(
        sign="pisces",
        reading_date="2026-08-10",
        transit_chart=chart_preview,
        previous_reading="Dünün ana teması",
    )

    assert "2026-08-10" in prompt
    assert "pisces" in prompt
    assert "Dünün ana teması" in prompt
