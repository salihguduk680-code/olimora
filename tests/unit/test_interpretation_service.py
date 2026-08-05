from app.modules.interpretation.service import _extract_output_text


def test_extract_output_text_from_responses_api_shape() -> None:
    assert _extract_output_text(
        {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "  Athena yanıtı  "}],
                }
            ]
        }
    ) == "Athena yanıtı"
