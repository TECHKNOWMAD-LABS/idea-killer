"""Tests for LLMClient."""

import pytest
from pytest_mock import MockerFixture

from ideakiller.llm import LLMClient


@pytest.fixture
def llm() -> LLMClient:
    return LLMClient()


async def test_ollama_used_when_available(mocker: MockerFixture, llm: LLMClient) -> None:
    mocker.patch.object(llm, "_probe_ollama", return_value=True)
    mock_ollama = mocker.patch.object(llm, "_ollama_complete", return_value='{"ok": true}')

    result = await llm.complete("test prompt")

    assert result == '{"ok": true}'
    mock_ollama.assert_called_once_with("test prompt")


async def test_ollama_unavailable_falls_back_to_anthropic(
    mocker: MockerFixture, llm: LLMClient
) -> None:
    mocker.patch.object(llm, "_probe_ollama", return_value=False)
    mock_anthropic = mocker.patch.object(
        llm, "_anthropic_complete", return_value='{"fallback": true}'
    )

    result = await llm.complete("test")

    assert result == '{"fallback": true}'
    mock_anthropic.assert_called_once()


async def test_ollama_failure_falls_back_to_anthropic(
    mocker: MockerFixture, llm: LLMClient
) -> None:
    mocker.patch.object(llm, "_probe_ollama", return_value=True)
    mocker.patch.object(llm, "_ollama_complete", side_effect=RuntimeError("timeout"))
    mock_anthropic = mocker.patch.object(
        llm, "_anthropic_complete", return_value='{"fallback": true}'
    )

    result = await llm.complete("test")

    assert result == '{"fallback": true}'
    mock_anthropic.assert_called_once()
    assert llm._ollama_available is False


async def test_anthropic_no_api_key_raises(mocker: MockerFixture, llm: LLMClient) -> None:
    mocker.patch.object(llm, "_probe_ollama", return_value=False)
    mocker.patch("os.environ.get", return_value=None)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        await llm.complete("test")


async def test_probe_cached_after_first_call(mocker: MockerFixture, llm: LLMClient) -> None:
    probe_mock = mocker.patch.object(llm, "_probe_ollama", return_value=False)
    mocker.patch.object(llm, "_anthropic_complete", return_value="resp")

    await llm.complete("first")
    await llm.complete("second")

    # _probe_ollama should only be called once (result is cached)
    probe_mock.assert_called_once()
