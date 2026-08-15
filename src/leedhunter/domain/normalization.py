"""
Persian / Unicode normalization utilities

Persian is a first-class language in LeedHunter.
This module provides explicit normalization while preserving original values.

NEVER destroy the original observed source value.
Always preserve both observed_value and canonical_value.
"""

import re
import unicodedata


class PersianNormalizer:
    """
    Normalizer for Persian/Arabic text

    Handles:
    - Arabic Yeh (ي) → Persian Yeh (ی)
    - Arabic Kaf (ك) → Persian Kaf (ک)
    - Unicode normalization
    - ZWNJ (Zero Width Non-Joiner)
    - Whitespace normalization
    - Digit normalization (Persian, Arabic, Latin)
    - Mixed-script strings
    """

    # Persian digits: ۰۱۲۳۴۵۶۷۸۹
    PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"

    # Arabic digits: ٠١٢٣٤٥٦٧٨٩
    ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"

    # Latin digits: 0123456789
    LATIN_DIGITS = "0123456789"

    # Character mappings
    CHAR_MAPPINGS = {
        # Arabic Yeh → Persian Yeh
        "ي": "ی",  # ي → ی
        # Arabic Kaf → Persian Kaf
        "ك": "ک",  # ك → ک
        # Arabic Alef with Hamza Above → Arabic Alef
        "أ": "ا",  # أ → ا
        # Arabic Alef with Hamza Below → Arabic Alef
        "إ": "ا",  # إ → ا
        # Arabic Teh Marbuta → Arabic Heh
        "ة": "ه",  # ة → ه
    }

    def __init__(self, preserve_original: bool = True):
        """
        Initialize normalizer

        Args:
            preserve_original: If True, original values are preserved in output
        """
        self.preserve_original = preserve_original

    def normalize(self, text: str) -> str:
        """
        Normalize Persian/Arabic text

        This is the main normalization method that applies all transformations.
        """
        if not text:
            return text

        # Step 1: Unicode normalization (NFC)
        text = unicodedata.normalize("NFC", text)

        # Step 2: Apply character mappings
        for old_char, new_char in self.CHAR_MAPPINGS.items():
            text = text.replace(old_char, new_char)

        # Step 3: Normalize ZWNJ (Zero Width Non-Joiner)
        text = self._normalize_zwnj(text)

        # Step 4: Normalize whitespace
        text = self._normalize_whitespace(text)

        # Step 5: Normalize digits
        text = self._normalize_digits(text)

        return text

    def normalize_preserving_original(self, text: str) -> tuple[str, str]:
        """
        Normalize text while preserving original

        Returns:
            Tuple of (original, normalized)
        """
        original = text
        normalized = self.normalize(text)
        return (original, normalized)

    def _normalize_zwnj(self, text: str) -> str:
        """
        Normalize Zero Width Non-Joiner (ZWNJ)

        ZWNJ is used in Persian to control ligature formation.
        We normalize it to ensure consistent representation.
        """
        # Replace multiple ZWNJs with single ZWNJ
        text = re.sub(r"‌+", "‌", text)

        # Remove ZWNJ at start and end of words
        text = re.sub(r"‌(?=\s)", "", text)
        text = re.sub(r"(?<=\s)‌", "", text)

        return text

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace

        Handles:
        - Multiple spaces → single space
        - Various Unicode spaces → regular space
        - Leading/trailing whitespace
        """
        # Replace various Unicode spaces with regular space
        text = re.sub(r"[\s   -​  　]", " ", text)

        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Trim
        text = text.strip()

        return text

    def _normalize_digits(self, text: str) -> str:
        """
        Normalize digits to Latin

        Converts Persian and Arabic digits to Latin digits.
        """
        result = []
        for char in text:
            if char in self.PERSIAN_DIGITS:
                # Convert Persian digit to Latin
                result.append(self.LATIN_DIGITS[self.PERSIAN_DIGITS.index(char)])
            elif char in self.ARABIC_DIGITS:
                # Convert Arabic digit to Latin
                result.append(self.LATIN_DIGITS[self.ARABIC_DIGITS.index(char)])
            else:
                result.append(char)
        return "".join(result)

    def normalize_domain(self, domain: str) -> str:
        """
        Normalize domain name

        Handles:
        - Lowercase
        - Remove www. prefix
        - Remove trailing slash
        - Persian/Arabic characters (convert to ASCII if possible)
        """
        if domain is None:
            return None

        domain = domain.lower().strip()

        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]

        # Remove trailing slash
        domain = domain.rstrip("/")

        # Normalize Persian/Arabic characters
        domain = self.normalize(domain)

        return domain

    def normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number

        Handles:
        - Persian/Arabic digits → Latin digits
        - Remove spaces, dashes, parentheses
        - Normalize Iranian phone numbers
        """
        if phone is None:
            return None

        # Normalize digits first
        phone = self._normalize_digits(phone)

        # Remove all non-digit characters except +
        phone = re.sub(r"[^\d+]", "", phone)

        # Handle Iranian phone numbers
        if phone.startswith("+98"):
            phone = "0" + phone[3:]
        elif phone.startswith("0098"):
            phone = "0" + phone[4:]
        elif phone.startswith("98") and len(phone) > 10:
            phone = "0" + phone[2:]

        return phone

    def normalize_email(self, email: str) -> str:
        """
        Normalize email address

        Handles:
        - Lowercase
        - Persian/Arabic characters in local part
        - Trim whitespace
        """
        if email is None:
            return None

        email = email.lower().strip()

        # Split into local and domain parts
        if "@" in email:
            local, domain = email.rsplit("@", 1)
            # Normalize domain
            domain = self.normalize_domain(domain)
            email = f"{local}@{domain}"

        return email

    def normalize_username(self, username: str) -> str:
        """
        Normalize username (Instagram, LinkedIn, etc.)

        Handles:
        - Lowercase
        - Remove @ prefix
        - Trim whitespace
        """
        if username is None:
            return None

        username = username.lower().strip()

        # Remove @ prefix
        if username.startswith("@"):
            username = username[1:]

        return username

    def is_persian(self, text: str) -> bool:
        """
        Check if text contains Persian characters

        Persian Unicode range: U+0600 to U+06FF
        Additional Persian range: U+FB50 to U+FDFF
        Additional Persian range: U+FE70 to U+FEFF
        """
        persian_pattern = re.compile(r"[؀-ۿﭐ-﷿ﹰ-﻿]")
        return bool(persian_pattern.search(text))

    def is_mixed_script(self, text: str) -> bool:
        """
        Check if text contains mixed scripts (e.g., Persian + Latin)
        """
        has_persian = self.is_persian(text)
        has_latin = bool(re.search(r"[a-zA-Z]", text))
        return has_persian and has_latin

    def extract_persian_text(self, text: str) -> str:
        """
        Extract only Persian characters from text
        """
        persian_pattern = re.compile(r"[؀-ۿﭐ-﷿ﹰ-﻿\s]")
        return "".join(persian_pattern.findall(text))

    def extract_latin_text(self, text: str) -> str:
        """
        Extract only Latin characters from text
        """
        latin_pattern = re.compile(r"[a-zA-Z\s]")
        return "".join(latin_pattern.findall(text))


# Global normalizer instance
_normalizer: PersianNormalizer | None = None


def get_normalizer() -> PersianNormalizer:
    """Get the global normalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = PersianNormalizer()
    return _normalizer


def normalize_text(text: str) -> str:
    """Convenience function for text normalization"""
    return get_normalizer().normalize(text)


def normalize_domain(domain: str) -> str:
    """Convenience function for domain normalization"""
    return get_normalizer().normalize_domain(domain)


def normalize_phone(phone: str) -> str:
    """Convenience function for phone normalization"""
    return get_normalizer().normalize_phone(phone)


def normalize_email(email: str) -> str:
    """Convenience function for email normalization"""
    return get_normalizer().normalize_email(email)


def normalize_username(username: str) -> str:
    """Convenience function for username normalization"""
    return get_normalizer().normalize_username(username)
