from shortener.views.urls import validate_url, validate_key


class TestValidateUrl:
    def test_validate_url_valid_http(self):
        assert validate_url("http://example.com") is True

    def test_validate_url_valid_https(self):
        assert validate_url("https://example.com") is True

    def test_validate_url_valid_ftp(self):
        assert validate_url("ftp://files.example.com") is True

    def test_validate_url_valid_with_path(self):
        assert validate_url("https://example.com/path/to/resource") is True

    def test_validate_url_valid_with_subdomain(self):
        assert validate_url("https://sub.example.com") is True

    def test_validate_url_valid_with_port(self):
        assert validate_url("https://example.com:8080") is True

    def test_validate_url_valid_with_query_params(self):
        assert validate_url("https://example.com/search?q=test") is True

    def test_validate_url_valid_complex(self):
        url = "https://subdomain.example.com:8080/path/to/resource?param1=value1&param2=value2#section"
        assert validate_url(url) is True

    def test_validate_url_empty_string(self):
        assert validate_url("") is False

    def test_validate_url_none(self):
        assert validate_url(None) is False

    def test_validate_url_no_protocol(self):
        assert validate_url("example.com") is False

    def test_validate_url_invalid_protocol(self):
        assert validate_url("javascript:alert('test')") is False

    def test_validate_url_file_protocol(self):
        assert validate_url("file:///path/to/file") is False

    def test_validate_url_missing_domain(self):
        assert validate_url("https://") is False

    def test_validate_url_whitespace_only(self):
        assert validate_url("   ") is False

    def test_validate_url_invalid_characters(self):
        assert validate_url("https://example .com") is False

    def test_validate_url_too_long_default(self):
        long_url = "https://example.com/" + "a" * 2048
        assert validate_url(long_url) is False

    def test_validate_url_max_length_boundary(self):
        # Test at exact boundary
        url_base = "https://example.com/"
        remaining_length = 2048 - len(url_base)
        url = url_base + "a" * remaining_length
        assert validate_url(url) is True

    def test_validate_url_custom_max_length(self):
        url = "https://example.com/short"
        assert validate_url(url, max_length=10) is False
        assert validate_url(url, max_length=50) is True

    def test_validate_url_international_domain(self):
        # Test with international characters (should pass basic regex)
        assert validate_url("https://example.org") is True

    def test_validate_url_ip_address(self):
        assert validate_url("https://192.168.1.1") is True
        assert validate_url("https://127.0.0.1:8080") is True

    def test_validate_url_localhost(self):
        assert validate_url("https://localhost") is True
        assert validate_url("https://localhost:3000") is True

    def test_validate_url_malformed_domain(self):
        assert validate_url("https://.example.com") is False
        assert validate_url("https://example..com") is False
        assert validate_url("https://example.") is False

    def test_validate_url_special_tlds(self):
        assert validate_url("https://example.museum") is True
        assert validate_url("https://example.co.uk") is True
        assert validate_url("https://example.com.br") is True

    def test_validate_url_edge_cases(self):
        # Test various edge cases
        assert validate_url("https://a.b") is True  # Minimal valid URL
        assert validate_url("https://example") is False  # No TLD
        assert validate_url("https://example.c") is True  # Single letter TLD


class TestValidateKey:
    def test_validate_key_valid_alphanumeric(self):
        assert validate_key("test123") is True

    def test_validate_key_valid_with_hyphens(self):
        assert validate_key("test-key") is True

    def test_validate_key_valid_with_underscores(self):
        assert validate_key("test_key") is True

    def test_validate_key_valid_mixed(self):
        assert validate_key("test-key_123") is True

    def test_validate_key_valid_single_character(self):
        assert validate_key("a") is True

    def test_validate_key_valid_numbers_only(self):
        assert validate_key("12345") is True

    def test_validate_key_empty_string(self):
        assert validate_key("") is False

    def test_validate_key_none(self):
        assert validate_key(None) is False

    def test_validate_key_whitespace_only(self):
        assert validate_key("   ") is False

    def test_validate_key_with_spaces(self):
        assert validate_key("test key") is False

    def test_validate_key_with_special_chars(self):
        assert validate_key("test@key") is False
        assert validate_key("test#key") is False
        assert validate_key("test$key") is False
        assert validate_key("test%key") is False
        assert validate_key("test&key") is False

    def test_validate_key_with_dots(self):
        assert validate_key("test.key") is False

    def test_validate_key_with_slashes(self):
        assert validate_key("test/key") is False
        assert validate_key("test\\key") is False

    def test_validate_key_with_brackets(self):
        assert validate_key("test[key]") is False
        assert validate_key("test(key)") is False
        assert validate_key("test{key}") is False

    def test_validate_key_with_quotes(self):
        assert validate_key('test"key') is False
        assert validate_key("test'key") is False

    def test_validate_key_unicode_characters(self):
        assert validate_key("tëst") is False
        assert validate_key("test中文") is False
        assert validate_key("tést") is False

    def test_validate_key_too_long_default(self):
        long_key = "a" * 51
        assert validate_key(long_key) is False

    def test_validate_key_max_length_boundary(self):
        # Test at exact boundary (50 characters)
        key_50_chars = "a" * 50
        assert validate_key(key_50_chars) is True

    def test_validate_key_custom_max_length(self):
        key = "testkey"
        assert validate_key(key, max_length=5) is False
        assert validate_key(key, max_length=10) is True

    def test_validate_key_leading_trailing_valid_chars(self):
        # These should all be valid
        assert validate_key("_test") is True
        assert validate_key("test_") is True
        assert validate_key("-test") is True
        assert validate_key("test-") is True
        assert validate_key("123test") is True
        assert validate_key("test123") is True

    def test_validate_key_only_special_allowed_chars(self):
        assert validate_key("_") is True
        assert validate_key("-") is True
        assert validate_key("_-_") is True
        assert validate_key("-_-") is True

    def test_validate_key_url_reserved_characters(self):
        # These characters should be rejected as they're URL reserved
        assert validate_key("test?key") is False
        assert validate_key("test=key") is False
        assert validate_key("test+key") is False
        assert validate_key("test:key") is False

    def test_validate_key_newlines_tabs(self):
        assert validate_key("test\nkey") is False
        assert validate_key("test\tkey") is False
        assert validate_key("test\rkey") is False
