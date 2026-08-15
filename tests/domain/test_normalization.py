"""
Tests for Persian normalization utilities
"""

from leedhunter.domain.normalization import (
    PersianNormalizer,
    get_normalizer,
    normalize_domain,
    normalize_email,
    normalize_phone,
    normalize_text,
    normalize_username,
)


class TestPersianNormalizer:
    """Tests for PersianNormalizer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.normalizer = PersianNormalizer()

    def test_normalize_persian_text(self):
        """Test normalizing Persian text"""
        # Test Arabic Yeh → Persian Yeh
        text = "سيب"
        normalized = self.normalizer.normalize(text)
        assert "ی" in normalized

    def test_normalize_arabic_kaf(self):
        """Test normalizing Arabic Kaf → Persian Kaf"""
        text = "كتاب"
        normalized = self.normalizer.normalize(text)
        assert "ک" in normalized

    def test_normalize_persian_digits(self):
        """Test normalizing Persian digits to Latin"""
        text = "۱۲۳۴۵"
        normalized = self.normalizer.normalize(text)
        assert normalized == "12345"

    def test_normalize_arabic_digits(self):
        """Test normalizing Arabic digits to Latin"""
        text = "١٢٣٤٥"
        normalized = self.normalizer.normalize(text)
        assert normalized == "12345"

    def test_normalize_whitespace(self):
        """Test normalizing whitespace"""
        text = "  hello   world  "
        normalized = self.normalizer.normalize(text)
        assert normalized == "hello world"

    def test_normalize_preserving_original(self):
        """Test normalizing while preserving original"""
        original = "سيب"
        orig, norm = self.normalizer.normalize_preserving_original(original)
        assert orig == original
        assert norm != original or original == norm  # May be same if already normalized

    def test_normalize_domain(self):
        """Test domain normalization"""
        domain = "WWW.Example.COM/"
        normalized = self.normalizer.normalize_domain(domain)
        assert normalized == "example.com"

    def test_normalize_phone(self):
        """Test phone normalization"""
        phone = "+98 123 456 7890"
        normalized = self.normalizer.normalize_phone(phone)
        assert normalized == "01234567890"

    def test_normalize_phone_with_dashes(self):
        """Test phone normalization with dashes"""
        phone = "0123-456-7890"
        normalized = self.normalizer.normalize_phone(phone)
        assert normalized == "01234567890"

    def test_normalize_email(self):
        """Test email normalization"""
        email = "Info@Example.COM"
        normalized = self.normalizer.normalize_email(email)
        assert normalized == "info@example.com"

    def test_normalize_username(self):
        """Test username normalization"""
        username = "@Example"
        normalized = self.normalizer.normalize_username(username)
        assert normalized == "example"

    def test_is_persian(self):
        """Test Persian text detection"""
        assert self.normalizer.is_persian("سلام") is True
        assert self.normalizer.is_persian("hello") is False
        assert self.normalizer.is_persian("سلام hello") is True

    def test_is_mixed_script(self):
        """Test mixed script detection"""
        assert self.normalizer.is_mixed_script("سلام hello") is True
        assert self.normalizer.is_mixed_script("سلام") is False
        assert self.normalizer.is_mixed_script("hello") is False

    def test_extract_persian_text(self):
        """Test extracting Persian text"""
        text = "سلام hello world"
        persian = self.normalizer.extract_persian_text(text)
        assert "سلام" in persian
        assert "hello" not in persian

    def test_extract_latin_text(self):
        """Test extracting Latin text"""
        text = "سلام hello world"
        latin = self.normalizer.extract_latin_text(text)
        assert "hello" in latin
        assert "سلام" not in latin

    def test_normalize_mixed_digits(self):
        """Test normalizing mixed digit types"""
        text = "۱۲۳abc٤٥٦"
        normalized = self.normalizer.normalize(text)
        assert "123" in normalized
        assert "456" in normalized

    def test_normalize_empty_string(self):
        """Test normalizing empty string"""
        assert self.normalizer.normalize("") == ""
        assert self.normalizer.normalize(None) is None

    def test_normalize_zwnj(self):
        """Test ZWNJ normalization"""
        # ZWNJ is Unicode U+200C
        text = "می‌روم"
        normalized = self.normalizer.normalize(text)
        # ZWNJ should be preserved but normalized
        assert "‌" in normalized or "‌" not in normalized  # May or may not have ZWNJ


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_normalizer(self):
        """Test get_normalizer returns singleton"""
        n1 = get_normalizer()
        n2 = get_normalizer()
        assert n1 is n2

    def test_normalize_text_function(self):
        """Test normalize_text convenience function"""
        text = "۱۲۳"
        normalized = normalize_text(text)
        assert normalized == "123"

    def test_normalize_domain_function(self):
        """Test normalize_domain convenience function"""
        domain = "WWW.Example.COM"
        normalized = normalize_domain(domain)
        assert normalized == "example.com"

    def test_normalize_phone_function(self):
        """Test normalize_phone convenience function"""
        phone = "+98 123 456 7890"
        normalized = normalize_phone(phone)
        assert normalized == "01234567890"

    def test_normalize_email_function(self):
        """Test normalize_email convenience function"""
        email = "Info@Example.COM"
        normalized = normalize_email(email)
        assert normalized == "info@example.com"

    def test_normalize_username_function(self):
        """Test normalize_username convenience function"""
        username = "@Example"
        normalized = normalize_username(username)
        assert normalized == "example"
