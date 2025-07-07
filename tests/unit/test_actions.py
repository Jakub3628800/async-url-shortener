import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from shortener.actions import (
    check_db_up,
    get_url_target,
    get_all_short_urls,
    create_url_target,
    update_url_target,
    delete_url_target,
    UrlNotFoundException,
    UrlValidationError
)
from starlette.exceptions import HTTPException


class TestCheckDbUp:
    @pytest.mark.asyncio
    async def test_check_db_up_success(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await check_db_up(mock_session)

        assert result is True
        mock_session.execute.assert_called_once()
        mock_result.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_db_up_failure_no_result(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await check_db_up(mock_session)

        assert result is False

    @pytest.mark.asyncio
    async def test_check_db_up_exception(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock(side_effect=Exception("Database connection error"))

        result = await check_db_up(mock_session)

        assert result is False


class TestGetUrlTarget:
    @pytest.mark.asyncio
    async def test_get_url_target_success(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar.return_value = "https://example.com"
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await get_url_target("test_key", mock_session)

        assert result == "https://example.com"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_url_target_not_found(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(UrlNotFoundException) as exc_info:
            await get_url_target("nonexistent", mock_session)

        assert "not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_url_target_empty_string(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError) as exc_info:
            await get_url_target("", mock_session)

        assert "cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_url_target_whitespace_only(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError):
            await get_url_target("   ", mock_session)

    @pytest.mark.asyncio
    async def test_get_url_target_database_error(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(UrlNotFoundException):
            await get_url_target("test_key", mock_session)


class TestGetAllShortUrls:
    @pytest.mark.asyncio
    async def test_get_all_short_urls_success(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()

        mock_record1 = MagicMock()
        mock_record1.url_key = "key1"
        mock_record1.target = "https://example1.com"

        mock_record2 = MagicMock()
        mock_record2.url_key = "key2"
        mock_record2.target = "https://example2.com"

        mock_result.fetchall.return_value = [mock_record1, mock_record2]
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await get_all_short_urls(mock_session)

        expected = [
            {"short_url": "key1", "target_url": "https://example1.com"},
            {"short_url": "key2", "target_url": "https://example2.com"}
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_all_short_urls_empty_database(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await get_all_short_urls(mock_session)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_short_urls_database_error(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(HTTPException) as exc_info:
            await get_all_short_urls(mock_session)

        assert exc_info.value.status_code == 500


class TestCreateUrlTarget:
    @pytest.mark.asyncio
    async def test_create_url_target_success(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock(return_value=None)

        result = await create_url_target("test_key", "https://example.com", mock_session)

        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_url_target_duplicate_key(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock(side_effect=IntegrityError("", "", ""))
        mock_session.rollback = AsyncMock(return_value=None)

        result = await create_url_target("existing_key", "https://example.com", mock_session)

        assert result is False
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_url_target_empty_short_url(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError) as exc_info:
            await create_url_target("", "https://example.com", mock_session)

        assert "Short URL cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_url_target_empty_target_url(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError) as exc_info:
            await create_url_target("test_key", "", mock_session)

        assert "Target URL cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_url_target_database_error(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = Exception("Database error")
        mock_session.rollback.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await create_url_target("test_key", "https://example.com", mock_session)

        assert exc_info.value.status_code == 500
        mock_session.rollback.assert_called_once()


class TestUpdateUrlTarget:
    @pytest.mark.asyncio
    async def test_update_url_target_success(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        result = await update_url_target("test_key", "https://new-example.com", mock_session)

        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_url_target_not_found(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        result = await update_url_target("nonexistent", "https://example.com", mock_session)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_url_target_empty_short_url(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError) as exc_info:
            await update_url_target("", "https://example.com", mock_session)

        assert "Short URL cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_url_target_empty_target_url(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError) as exc_info:
            await update_url_target("test_key", "", mock_session)

        assert "Target URL cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_url_target_database_error(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = Exception("Database error")
        mock_session.rollback.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await update_url_target("test_key", "https://example.com", mock_session)

        assert exc_info.value.status_code == 500
        mock_session.rollback.assert_called_once()


class TestDeleteUrlTarget:
    @pytest.mark.asyncio
    async def test_delete_url_target_success(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        result = await delete_url_target("test_key", mock_session)

        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_url_target_not_found(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        result = await delete_url_target("nonexistent", mock_session)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_url_target_empty_short_url(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(UrlValidationError) as exc_info:
            await delete_url_target("", mock_session)

        assert "Short URL cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_delete_url_target_database_error(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = Exception("Database error")
        mock_session.rollback.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await delete_url_target("test_key", mock_session)

        assert exc_info.value.status_code == 500
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_url_target_rowcount_none(self):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.rowcount = None
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        result = await delete_url_target("test_key", mock_session)

        assert result is False
