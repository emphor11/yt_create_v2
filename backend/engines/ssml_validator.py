from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SSMLValidationResult:
    """Result of an SSML validation check."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)


class SSMLValidator:
    """
    Strict Whitelist Validator for Amazon Polly Neural SSML.
    
    Verifies that:
    1. The document is well-formed XML.
    2. The root tag is <speak>.
    3. Only permitted tags are present (<speak>, <break>, <prosody>, <sub>, <mark>).
    4. Prohibited Neural tags and attributes (e.g. <emphasis>, <prosody pitch>) are rejected.
    5. Attribute values adhere to safe operational boundaries.
    """

    ALLOWED_TAGS: set[str] = {
        "speak",
        "break",
        "prosody",
        "sub",
        "mark",
    }

    ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
        "speak": set(),
        "break": {"time", "strength"},
        "prosody": {"rate", "volume"},
        "sub": {"alias"},
        "mark": {"name"},
    }

    def validate(self, ssml_text: str) -> SSMLValidationResult:
        """
        Validates an SSML string. Returns an SSMLValidationResult.
        """
        if not ssml_text or not ssml_text.strip():
            return SSMLValidationResult(is_valid=False, errors=["Empty or blank SSML content."])

        clean_text = ssml_text.strip()

        # 1. Parse XML structure
        try:
            root = ET.fromstring(clean_text)
        except ET.ParseError as exc:
            return SSMLValidationResult(
                is_valid=False,
                errors=[f"XML Parse Error: {exc}"],
            )

        errors: list[str] = []

        # 2. Check root element
        if root.tag != "speak":
            errors.append(f"Root element must be <speak>, found <{root.tag}>.")

        # 3. Traverse all nodes and validate tags and attributes
        for elem in root.iter():
            tag = elem.tag.lower()
            if tag not in self.ALLOWED_TAGS:
                if tag == "emphasis":
                    errors.append("<emphasis> tag is not supported by Amazon Polly Neural voices.")
                else:
                    errors.append(f"Forbidden or unsupported SSML tag <{tag}> for Neural voices.")
                continue

            allowed_attrs = self.ALLOWED_ATTRIBUTES.get(tag, set())
            for attr_name, attr_val in elem.attrib.items():
                attr_clean = attr_name.lower()
                if attr_clean not in allowed_attrs:
                    if tag == "prosody" and attr_clean == "pitch":
                        errors.append("<prosody> pitch attribute is forbidden for Amazon Polly Neural voices.")
                    else:
                        errors.append(f"Forbidden attribute '{attr_name}' on <{tag}>.")
                    continue

                # Attribute value checks
                val_error = self._validate_attribute_value(tag, attr_clean, str(attr_val))
                if val_error:
                    errors.append(val_error)

        return SSMLValidationResult(
            is_valid=(len(errors) == 0),
            errors=errors,
        )

    def _validate_attribute_value(self, tag: str, attr: str, val: str) -> str | None:
        """Validates specific attribute value formats and ranges."""
        val_clean = val.strip()

        if tag == "break" and attr == "time":
            # e.g. '350ms' or '1.5s'
            match = re.match(r"^(\d+)(ms|s)$", val_clean)
            if not match:
                return f"Invalid <break> time value '{val}'. Expected format like '350ms' or '1s'."
            num, unit = int(match.group(1)), match.group(2)
            ms = num if unit == "ms" else num * 1000
            if ms < 50 or ms > 3000:
                return f"<break> time {val} out of safe range (50ms to 3000ms)."

        elif tag == "prosody" and attr == "rate":
            # e.g. '95%' or keyword
            keywords = {"x-slow", "slow", "medium", "fast", "x-fast", "default"}
            if val_clean not in keywords:
                match = re.match(r"^(\d+)%$", val_clean)
                if not match:
                    return f"Invalid <prosody> rate '{val}'. Expected percentage like '95%'."
                rate = int(match.group(1))
                if rate < 50 or rate > 150:
                    return f"<prosody> rate {rate}% out of safe range (50% to 150%)."

        elif tag == "prosody" and attr == "volume":
            # e.g. '+2dB', '-1dB', or keyword
            keywords = {"silent", "x-soft", "soft", "medium", "loud", "x-loud", "default"}
            if val_clean not in keywords:
                match = re.match(r"^[+-]?\d+dB$", val_clean)
                if not match:
                    return f"Invalid <prosody> volume '{val}'. Expected format like '+2dB' or keyword."

        elif tag == "mark" and attr == "name":
            if not val_clean:
                return "<mark> name cannot be empty."

        elif tag == "sub" and attr == "alias":
            if not val_clean:
                return "<sub> alias cannot be empty."

        return None
