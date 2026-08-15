"""
Tests for Persian normalization in database operations
"""

from leedhunter.domain.normalization import (
    normalize_domain,
    normalize_email,
    normalize_phone,
    normalize_text,
    normalize_username,
)


class TestPersianNormalizationIntegration:
    """Test Persian normalization integration with database operations"""

    def test_normalize_persian_entity_name(self):
        """Test normalizing Persian entity names"""
        # Arabic Yeh → Persian Yeh
        name = "سيب"
        normalized = normalize_text(name)
        assert "ی" in normalized
        assert normalized != name  # Should be different

    def test_normalize_persian_domain(self):
        """Test normalizing Persian domains"""
        domain = "مثال.com"
        normalized = normalize_domain(domain)
        assert normalized == "مثال.com"  # Domain should remain as-is if no normalization needed

    def test_normalize_persian_phone(self):
        """Test normalizing Persian phone numbers"""
        # Persian digits
        phone = "۰۹۱۲۱۲۳۴۵۶۷"
        normalized = normalize_phone(phone)
        assert normalized == "09121234567"

        # Arabic digits
        phone = "٠٩١٢١٢٣٤٥٦٧"
        normalized = normalize_phone(phone)
        assert normalized == "09121234567"

    def test_normalize_persian_email(self):
        """Test normalizing Persian emails"""
        email = "تست@مثال.com"
        normalized = normalize_email(email)
        assert "@" in normalized
        assert normalized == "تست@مثال.com"

    def test_normalize_persian_username(self):
        """Test normalizing Persian usernames"""
        username = "@نام_کاربری"
        normalized = normalize_username(username)
        assert not normalized.startswith("@")
        assert "نام_کاربری" in normalized

    def test_normalize_mixed_script(self):
        """Test normalizing mixed Persian/Latin text"""
        text = "شرکت Example"
        normalized = normalize_text(text)
        assert "شرکت" in normalized
        assert "Example" in normalized

    def test_normalize_persian_digits(self):
        """Test normalizing Persian digits to Latin"""
        # Persian digits
        text = "۱۲۳۴۵"
        normalized = normalize_text(text)
        assert normalized == "12345"

        # Arabic digits
        text = "١٢٣٤٥"
        normalized = normalize_text(text)
        assert normalized == "12345"

    def test_normalize_zwnj(self):
        """Test ZWNJ normalization"""
        # ZWNJ in Persian text
        text = "می‌روم"
        normalized = normalize_text(text)
        # Should preserve ZWNJ but normalize multiple ZWNJs
        assert len(normalized) > 0

    def test_normalize_whitespace(self):
        """Test whitespace normalization"""
        text = "  سلام   دنیا  "
        normalized = normalize_text(text)
        assert normalized == "سلام دنیا"

    def test_normalize_arabic_characters(self):
        """Test normalizing Arabic characters to Persian"""
        # Arabic Yeh → Persian Yeh
        text = "سيب"
        normalized = normalize_text(text)
        assert "ی" in normalized

        # Arabic Kaf → Persian Kaf
        text = "كتاب"
        normalized = normalize_text(text)
        assert "ک" in normalized

    def test_normalize_preserves_original(self):
        """Test that normalization preserves original text"""
        original = "سيب"
        normalized = normalize_text(original)
        # Original should remain unchanged
        assert original == "سيب"
        # Normalized should be different
        assert normalized != original

    def test_normalize_idempotent(self):
        """Test that normalization is idempotent"""
        text = "سيب"
        normalized1 = normalize_text(text)
        normalized2 = normalize_text(normalized1)
        assert normalized1 == normalized2

    def test_normalize_empty_string(self):
        """Test normalizing empty string"""
        assert normalize_text("") == ""
        assert normalize_domain("") == ""
        assert normalize_phone("") == ""
        assert normalize_email("") == ""
        assert normalize_username("") == ""

    def test_normalize_none(self):
        """Test normalizing None"""
        # These should handle None gracefully
        assert normalize_text(None) is None
        assert normalize_domain(None) is None
        assert normalize_phone(None) is None
        assert normalize_email(None) is None
        assert normalize_username(None) is None

    def test_normalize_complex_persian_text(self):
        """Test normalizing complex Persian text with mixed content"""
        text = "شرکت واردات خودرو در مازندران"
        normalized = normalize_text(text)
        assert "شرکت" in normalized
        assert "واردات" in normalized
        assert "خودرو" in normalized
        assert "مازندران" in normalized

    def test_normalize_persian_with_numbers(self):
        """Test normalizing Persian text with numbers"""
        text = "شعبه ۱۲۳"
        normalized = normalize_text(text)
        assert "شعبه" in normalized
        assert "123" in normalized  # Persian digits should be normalized

    def test_normalize_domain_with_www(self):
        """Test normalizing domain with www prefix"""
        domain = "WWW.مثال.COM"
        normalized = normalize_domain(domain)
        assert normalized == "مثال.com"

    def test_normalize_phone_with_country_code(self):
        """Test normalizing phone with country code"""
        phone = "+98 912 123 4567"
        normalized = normalize_phone(phone)
        assert normalized == "09121234567"

    def test_normalize_email_case_insensitive(self):
        """Test normalizing email case insensitivity"""
        email = "Test@EXAMPLE.COM"
        normalized = normalize_email(email)
        assert normalized == "test@example.com"
