import pytest
from shortener.views.urls import validate_url, validate_key


class TestValidateUrl:
    def test_validate_url_valid_http(self):
        assert validate_url("http://example.com") is True

    def test_validate_url_valid_https(self):
        assert validate_url("https://example.com") is True

    def test_validate_url_valid_ftp(self):
        assert validate_url("ftp://example.com") is True

    def test_validate_url_valid_with_port(self):
        assert validate_url("https://example.com:8080") is True

    def test_validate_url_valid_with_path(self):
        assert validate_url("https://example.com/path/to/resource") is True

    def test_validate_url_valid_with_query(self):
        assert validate_url("https://example.com/path?query=value") is True

    def test_validate_url_valid_with_fragment(self):
        assert validate_url("https://example.com/path#fragment") is True

    def test_validate_url_valid_with_subdomain(self):
        assert validate_url("https://api.example.com") is True

    def test_validate_url_valid_localhost(self):
        assert validate_url("http://localhost") is True

    def test_validate_url_valid_localhost_with_port(self):
        assert validate_url("http://localhost:3000") is True

    def test_validate_url_valid_ip_address(self):
        assert validate_url("http://192.168.1.1") is True

    def test_validate_url_valid_ip_with_port(self):
        assert validate_url("http://192.168.1.1:8080") is True

    def test_validate_url_empty_string(self):
        assert validate_url("") is False

    def test_validate_url_none(self):
        assert validate_url(None) is False

    def test_validate_url_no_scheme(self):
        assert validate_url("example.com") is False

    def test_validate_url_invalid_scheme(self):
        assert validate_url("gopher://example.com") is False

    def test_validate_url_invalid_domain(self):
        assert validate_url("https://") is False

    def test_validate_url_space_in_url(self):
        assert validate_url("https://example.com/path with spaces") is False

    def test_validate_url_max_length_default(self):
        long_url = "https://example.com/" + "a" * 2040
        assert validate_url(long_url) is False

    def test_validate_url_custom_max_length(self):
        url = "https://example.com/short"
        assert validate_url(url, max_length=10) is False
        assert validate_url(url, max_length=50) is True

    def test_validate_url_unicode_domain(self):
        assert validate_url("https://münchen.de") is False

    def test_validate_url_multiple_dots_in_domain(self):
        assert validate_url("https://www.example.co.uk") is True

    def test_validate_url_single_letter_tld(self):
        assert validate_url("https://example.c") is True


class TestValidateKey:
    def test_validate_key_valid_alphanumeric(self):
        assert validate_key("abc123") is True

    def test_validate_key_valid_with_hyphens(self):
        assert validate_key("my-key") is True

    def test_validate_key_valid_with_underscores(self):
        assert validate_key("my_key") is True

    def test_validate_key_valid_mixed(self):
        assert validate_key("my-key_123") is True

    def test_validate_key_valid_uppercase(self):
        assert validate_key("MYKEY") is True

    def test_validate_key_valid_mixed_case(self):
        assert validate_key("MyKey123") is True

    def test_validate_key_empty_string(self):
        assert validate_key("") is False

    def test_validate_key_none(self):
        assert validate_key(None) is False

    def test_validate_key_with_spaces(self):
        assert validate_key("my key") is False

    def test_validate_key_with_dots(self):
        assert validate_key("my.key") is False

    def test_validate_key_with_special_chars(self):
        assert validate_key("my@key") is False

    def test_validate_key_with_forward_slash(self):
        assert validate_key("my/key") is False

    def test_validate_key_with_backslash(self):
        assert validate_key("my\\key") is False

    def test_validate_key_max_length_default(self):
        long_key = "a" * 51
        assert validate_key(long_key) is False

    def test_validate_key_exact_max_length_default(self):
        key = "a" * 50
        assert validate_key(key) is True

    def test_validate_key_custom_max_length(self):
        key = "abcdef"
        assert validate_key(key, max_length=5) is False
        assert validate_key(key, max_length=10) is True

    def test_validate_key_unicode_chars(self):
        assert validate_key("mýkey") is False

    def test_validate_key_emoji(self):
        assert validate_key("key🔑") is False

    def test_validate_key_starting_with_number(self):
        assert validate_key("123key") is True

    def test_validate_key_only_numbers(self):
        assert validate_key("123456") is True

    def test_validate_key_only_hyphens(self):
        assert validate_key("---") is True

    def test_validate_key_only_underscores(self):
        assert validate_key("___") is True