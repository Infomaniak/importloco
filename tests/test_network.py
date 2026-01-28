"""Tests for network operations."""

import tempfile
from unittest.mock import Mock, patch, MagicMock

import pytest
import requests

from import_loco.core.exceptions import LocoNetworkError
from import_loco.core.loco.loco_network import (
    fetch_archive,
    fetch_tags,
    _create_endpoint,
    _get_default_query_params,
    _download_archive,
)


class TestCreateEndpoint:
    """Tests for _create_endpoint function."""

    def test_create_endpoint_without_params(self):
        """Test creating endpoint URL without query parameters."""
        url = _create_endpoint("/tags")
        assert url == "https://localise.biz/api/tags"

    def test_create_endpoint_with_params(self):
        """Test creating endpoint URL with query parameters."""
        params = {"key": "test-key", "filter": "ios"}
        url = _create_endpoint("/export/archive/strings.zip", params)
        
        assert url.startswith("https://localise.biz/api/export/archive/strings.zip?")
        assert "key=test-key" in url
        assert "filter=ios" in url

    def test_create_endpoint_with_none_params(self):
        """Test creating endpoint URL with None params."""
        url = _create_endpoint("/tags", None)
        assert url == "https://localise.biz/api/tags"
        assert "?" not in url


class TestGetDefaultQueryParams:
    """Tests for _get_default_query_params function."""

    def test_get_default_query_params_with_all_values(self):
        """Test getting query params with all values provided."""
        params = _get_default_query_params("ios,common", "test-key-123")
        
        assert params["fallback"] == "en"
        assert params["order"] == "id"
        assert params["charset"] == "utf8"
        assert params["filter"] == "ios,common"
        assert params["key"] == "test-key-123"

    def test_get_default_query_params_filters_none_values(self):
        """Test that None values are filtered out."""
        params = _get_default_query_params(None, "test-key")
        
        # None values should be filtered out
        assert "filter" not in params
        assert params["key"] == "test-key"
        assert params["fallback"] == "en"


class TestDownloadArchive:
    """Tests for _download_archive function."""

    @patch("import_loco.core.loco.loco_network.urlretrieve")
    def test_download_archive_success(self, mock_urlretrieve):
        """Test successful archive download."""
        mock_urlretrieve.return_value = ("/tmp/archive.zip", None)
        
        result = _download_archive("https://example.com/archive.zip")
        
        assert result == "/tmp/archive.zip"
        mock_urlretrieve.assert_called_once_with("https://example.com/archive.zip")

    @patch("import_loco.core.loco.loco_network.urlretrieve")
    def test_download_archive_failure(self, mock_urlretrieve):
        """Test archive download failure."""
        mock_urlretrieve.side_effect = Exception("Network error")
        
        with pytest.raises(LocoNetworkError) as exc_info:
            _download_archive("https://example.com/archive.zip")
        
        assert "Failed to download archive" in str(exc_info.value)


class TestFetchArchive:
    """Tests for fetch_archive function."""

    @patch("import_loco.core.loco.loco_network._download_archive")
    def test_fetch_archive_success(self, mock_download):
        """Test successful archive fetch."""
        mock_download.return_value = "/tmp/downloaded.zip"
        
        result = fetch_archive("strings.zip", "ios", "test-key")
        
        assert result == "/tmp/downloaded.zip"
        mock_download.assert_called_once()
        
        # Check that the endpoint was constructed correctly
        call_args = mock_download.call_args[0][0]
        assert "export/archive/strings.zip" in call_args
        assert "key=test-key" in call_args
        assert "filter=ios" in call_args

    @patch("import_loco.core.loco.loco_network._download_archive")
    def test_fetch_archive_with_multiple_filters(self, mock_download):
        """Test fetching archive with multiple filters."""
        mock_download.return_value = "/tmp/archive.zip"
        
        result = fetch_archive("strings.zip", "ios,common,!android", "test-key")
        
        assert result == "/tmp/archive.zip"
        call_args = mock_download.call_args[0][0]
        assert "ios,common,!android" in call_args or "ios%2Ccommon%2C%21android" in call_args


class TestFetchTags:
    """Tests for fetch_tags function."""

    @patch("import_loco.core.loco.loco_network.requests.get")
    def test_fetch_tags_success(self, mock_get):
        """Test successful tags fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["ios", "android", "common", "web"]
        mock_get.return_value = mock_response
        
        result = fetch_tags("test-key-123")
        
        assert result == ["ios", "android", "common", "web"]
        mock_get.assert_called_once()
        
        # Check headers
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "Loco test-key-123"

    @patch("import_loco.core.loco.loco_network.requests.get")
    def test_fetch_tags_non_200_status(self, mock_get):
        """Test tags fetch with non-200 status code."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fetch_tags("test-key")
        
        assert result is None

    @patch("import_loco.core.loco.loco_network.requests.get")
    def test_fetch_tags_network_error(self, mock_get):
        """Test tags fetch with network error."""
        mock_get.side_effect = requests.RequestException("Connection timeout")
        
        with pytest.raises(LocoNetworkError) as exc_info:
            fetch_tags("test-key")
        
        assert "Failed to fetch tags" in str(exc_info.value)

    @patch("import_loco.core.loco.loco_network.requests.get")
    def test_fetch_tags_with_timeout(self, mock_get):
        """Test that fetch_tags includes timeout parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        fetch_tags("test-key")
        
        # Verify timeout was specified
        call_kwargs = mock_get.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 30
