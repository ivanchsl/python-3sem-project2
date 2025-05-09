import pytest
import aiohttp
import json
from aioresponses import aioresponses
from unittest.mock import AsyncMock, patch


from kandinsky import (
    API,
    APIError,
    IncorrectUseError,
    WrongParametersError,
    FailedRequestError,
    WrongResponseBodyError,
    ImageGenerationError,
)


@pytest.fixture(scope="function")
def mock_session():
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture(scope="function")
def api_client(mock_session):
    return API(api_key="test_key", secret_key="test_secret", session=mock_session)


@pytest.mark.asyncio
async def test_context_manager_uses_provided_session(mock_session):
    async with API(session=mock_session) as api:
        assert api.session is mock_session
        assert not api.session_closing


@pytest.mark.asyncio
async def test_context_manager_creates_and_closes_session():
    async with API(api_key="test", secret_key="test") as api:
        session = api._getSession()
        assert session is not None
        assert api.session_closing
    assert api.session.closed


@pytest.mark.asyncio
async def test_get_session_creates_new(mock_session):
    api = API()
    with patch("aiohttp.ClientSession", return_value=mock_session):
        session = api._getSession()
        assert session is mock_session
        assert api.session_closing


@pytest.mark.asyncio
async def test_get_session_raises_error():
    api = API()
    with patch("aiohttp.ClientSession", side_effect=Exception("Error")):
        with pytest.raises(APIError):
            api._getSession()


@pytest.mark.asyncio
async def test_handle_request_success(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get("https://test.com", status=200, payload={"key": "value"})
            result = await api._handleRequest("GET", 200, "https://test.com")
            assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_handle_request_wrong_status(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get("https://test.com", status=400)
            with pytest.raises(FailedRequestError):
                await api._handleRequest("GET", 200, "https://test.com")


@pytest.mark.asyncio
async def test_handle_request_client_error(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get("https://test.com", exception=aiohttp.ClientError("Error"))
            with pytest.raises(FailedRequestError):
                await api._handleRequest("GET", 200, "https://test.com")


@pytest.mark.asyncio
async def test_handle_request_json_error(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get("https://test.com", status=200, body="invalid")
            with pytest.raises(FailedRequestError):
                await api._handleRequest("GET", 200, "https://test.com")


@pytest.mark.asyncio
async def test_handle_request_unexpected_exception(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get("https://test.com", exception=ValueError("Error"))
            with pytest.raises(APIError):
                await api._handleRequest("GET", 200, "https://test.com")


@pytest.mark.asyncio
async def test_get_model_success(api_client, mock_session):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get(
                "https://api-key.fusionbrain.ai/key/api/v1/pipelines",
                status=200,
                payload=[{"id": "model1"}],
            )
            model_id = await api.getModel()
            assert model_id == "model1"


@pytest.mark.asyncio
async def test_get_model_no_credentials():
    api = API()
    with pytest.raises(IncorrectUseError):
        await api.getModel()


@pytest.mark.asyncio
async def test_get_model_invalid_response(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get(
                "https://api-key.fusionbrain.ai/key/api/v1/pipelines",
                status=200,
                payload={}
            )
            with pytest.raises(WrongResponseBodyError):
                await api.getModel()


@pytest.mark.asyncio
async def test_start_generation_no_credentials():
    api = API()
    with pytest.raises(IncorrectUseError):
        await api.startGeneration("prompt", "style")


@pytest.mark.asyncio
async def test_start_generation_success(api_client):
    with aioresponses() as mock_responses:
        mock_responses.get(
            "https://api-key.fusionbrain.ai/key/api/v1/pipelines",
            status=200,
            payload=[{"id": "model1"}],
        )
        mock_responses.post(
            "https://api-key.fusionbrain.ai/key/api/v1/pipeline/run",
            status=201,
            payload={"uuid": "ans123"},
        )
        async with api_client as api:
            await api.startGeneration("prompt", "style")
            assert "ans123" in api.pending_images


@pytest.mark.asyncio
async def test_start_generation_missing_parameters(api_client):
    async with api_client as api:
        with pytest.raises(WrongParametersError):
            await api.startGeneration("", "style")


@pytest.mark.asyncio
async def test_check_generation_no_credentials():
    api = API()
    with pytest.raises(IncorrectUseError):
        await api.checkGeneration()


@pytest.mark.asyncio
async def test_check_generation_statuses(api_client):
    async with api_client as api:
        api.pending_images = ["ex1", "ex2"]
        with aioresponses() as mock_responses:
            mock_responses.get(
                "https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/ex1",
                payload={"status": "DONE", "result": {"files": ["image1"]}},
            )
            mock_responses.get(
                "https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/ex2",
                payload={"status": "PROCESSING"},
            )
            await api.checkGeneration()
            assert api.ready_images == ["image1"]
            assert api.pending_images == ["ex2"]


@pytest.mark.asyncio
async def test_check_generation_failure(api_client):
    async with api_client as api:
        api.pending_images = ["ex1"]
        with aioresponses() as mock_responses:
            mock_responses.get(
                "https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/ex1",
                payload={"status": "FAIL"},
            )
            with pytest.raises(ImageGenerationError):
                await api.checkGeneration()


@pytest.mark.asyncio
async def test_get_photos(api_client):
    async with api_client as api:
        api.ready_images = ["image1", "image2"]
        result = api.getPhotos()
        assert result == ["image1", "image2"]
        assert api.ready_images == []


@pytest.mark.asyncio
async def test_get_styles_success(api_client):
    with aioresponses() as mock_responses:
        sample_styles = [{"titleEn": "Style1", "name": "Display1"}]
        mock_responses.get(
            "https://cdn.fusionbrain.ai/static/styles/key",
            status=200,
            payload=sample_styles
        )
        async with api_client as api:
            styles = await api._getStyles()
        assert styles == [{"title": "Style1", "display_name": "Display1"}]


@pytest.mark.asyncio
async def test_get_styles_invalid_response(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            mock_responses.get(
                "https://cdn.fusionbrain.ai/static/styles/key",
                status=200,
                payload=[]
            )
            with pytest.raises(WrongResponseBodyError):
                await api._getStyles()
            mock_responses.get(
                "https://cdn.fusionbrain.ai/static/styles/key",
                status=200,
                payload={"error": "bad response"}
            )
            with pytest.raises(WrongResponseBodyError):
                await api._getStyles()


@pytest.mark.asyncio
async def test_get_styles_wrong_keys(api_client):
    with aioresponses() as mock_responses:
        async with api_client as api:
            bad_style = [{"wrongKey": "test"}]
            mock_responses.get(
                "https://cdn.fusionbrain.ai/static/styles/key",
                status=200,
                payload=bad_style
            )
            with pytest.raises(WrongResponseBodyError):
                await api._getStyles()


@pytest.mark.asyncio
async def test_get_style_list(api_client):
    with patch.object(API, "_getStyles", return_value=[{"title": "Style1"}]):
        async with api_client as api:
            styles = await api.getStyleList()
        assert styles == ["Style1"]


@pytest.mark.asyncio
async def test_get_style_by_title(api_client):
    async with api_client as api:
        with patch.object(
            API,
            "_getStyles",
            return_value=[{"title": "Style1", "display_name": "Display1"}]
        ):
            display_name = await api.getStyleByTitle("Style1")
            assert display_name == "Display1"
        with pytest.raises(WrongParametersError):
            await api.getStyleByTitle("Invalid")
