import pytest

from domain.script_visual_strategy import VoiceCue
from engines.ssml_compiler import SSMLCompiler
from engines.ssml_validator import SSMLValidator, SSMLValidationResult


def test_compiler_wraps_plain_text_in_speak():
    compiler = SSMLCompiler()
    ssml = compiler.compile("This is a simple sentence.")
    assert ssml == "<speak>This is a simple sentence.</speak>"


def test_compiler_escapes_xml_special_characters():
    compiler = SSMLCompiler()
    ssml = compiler.compile("Stocks & Bonds: When yield < 5% and cost > 2%.")
    assert "&amp;" in ssml
    assert "&lt;" in ssml
    assert "&gt;" in ssml
    assert ssml.startswith("<speak>")
    assert ssml.endswith("</speak>")


def test_compiler_applies_pause_cue():
    compiler = SSMLCompiler()
    cue = VoiceCue(anchor="relief.", pause_after_ms=400)
    text = "On paper, lower EMI looks like relief. Until you calculate the cost."
    ssml = compiler.compile(text, [cue])
    assert 'relief.<break time="400ms"/>' in ssml
    assert ssml.startswith("<speak>")
    assert ssml.endswith("</speak>")


def test_compiler_applies_rate_and_volume_cue():
    compiler = SSMLCompiler()
    cue = VoiceCue(anchor="real cost", rate=94, volume_db=2)
    text = "Until you calculate the real cost of the loan."
    ssml = compiler.compile(text, [cue])
    assert '<prosody rate="94%" volume="+2dB">real cost</prosody>' in ssml


def test_compiler_applies_pronunciation_sub():
    compiler = SSMLCompiler()
    cue = VoiceCue(anchor="₹50,000", pronunciation="fifty thousand rupees")
    text = "You save ₹50,000 every year."
    ssml = compiler.compile(text, [cue])
    assert '<sub alias="fifty thousand rupees">₹50,000</sub>' in ssml


def test_compiler_applies_section_mark():
    compiler = SSMLCompiler()
    ssml = compiler.compile("First sentence.", section_mark="intent_01_start")
    assert '<mark name="intent_01_start"/>' in ssml


def test_compiler_handles_multiple_cues_in_order():
    compiler = SSMLCompiler()
    cues = [
        VoiceCue(anchor="relief.", pause_after_ms=400),
        VoiceCue(anchor="real cost", rate=94, volume_db=2),
        VoiceCue(anchor="₹50,000", pronunciation="fifty thousand rupees"),
    ]
    text = "On paper, lower EMI looks like relief. You save ₹50,000, until you calculate the real cost."
    ssml = compiler.compile(text, cues, section_mark="scene_01")

    assert '<mark name="scene_01"/>' in ssml
    assert 'relief.<break time="400ms"/>' in ssml
    assert '<sub alias="fifty thousand rupees">₹50,000</sub>' in ssml
    assert '<prosody rate="94%" volume="+2dB">real cost</prosody>' in ssml


def test_validator_accepts_compiled_ssml():
    compiler = SSMLCompiler()
    validator = SSMLValidator()

    cues = [
        VoiceCue(anchor="relief.", pause_after_ms=400),
        VoiceCue(anchor="real cost", rate=94, volume_db=2),
        VoiceCue(anchor="₹50,000", pronunciation="fifty thousand rupees"),
    ]
    text = "On paper, lower EMI looks like relief. You save ₹50,000, until you calculate the real cost."
    ssml = compiler.compile(text, cues, section_mark="scene_01")

    result = validator.validate(ssml)
    assert result.is_valid is True
    assert result.errors == []


def test_validator_rejects_malformed_xml():
    validator = SSMLValidator()
    result = validator.validate("<speak>Unclosed break: <break time='300ms'></speak>")
    assert result.is_valid is False
    assert any("XML Parse Error" in err for err in result.errors)


def test_validator_rejects_non_speak_root():
    validator = SSMLValidator()
    result = validator.validate("<document>Hello world</document>")
    assert result.is_valid is False
    assert any("Root element must be <speak>" in err for err in result.errors)


def test_validator_rejects_emphasis_tag_for_neural():
    validator = SSMLValidator()
    result = validator.validate("<speak>This is <emphasis level='strong'>important</emphasis>.</speak>")
    assert result.is_valid is False
    assert any("<emphasis> tag is not supported" in err for err in result.errors)


def test_validator_rejects_prosody_pitch_attribute_for_neural():
    validator = SSMLValidator()
    result = validator.validate("<speak>This is <prosody pitch='+2st'>high pitch</prosody>.</speak>")
    assert result.is_valid is False
    assert any("pitch attribute is forbidden" in err for err in result.errors)


def test_validator_rejects_forbidden_tags():
    validator = SSMLValidator()
    result = validator.validate("<speak><voice name='Joe'>Speaking in voice</voice></speak>")
    assert result.is_valid is False
    assert any("Forbidden or unsupported" in err for err in result.errors)


def test_validator_rejects_unbound_namespaces():
    validator = SSMLValidator()
    result = validator.validate("<speak><amazon:domain name='news'>News reading</amazon:domain></speak>")
    assert result.is_valid is False
    assert any("XML Parse Error" in err for err in result.errors)


def test_validator_checks_break_time_boundaries():
    validator = SSMLValidator()
    # 5000ms is outside the safe range (50ms - 3000ms)
    result = validator.validate("<speak>Wait <break time='5000ms'/> now.</speak>")
    assert result.is_valid is False
    assert any("out of safe range" in err for err in result.errors)


def test_validator_accepts_valid_standalone_marks():
    validator = SSMLValidator()
    ssml = '<speak><mark name="event_start"/>Hello <mark name="event_end"/>world.</speak>'
    result = validator.validate(ssml)
    assert result.is_valid is True
    assert result.errors == []


def test_compiler_applies_pause_before_ms():
    compiler = SSMLCompiler()
    cue = VoiceCue(anchor="the real cost", pause_before_ms=300)
    text = "Until you calculate the real cost of the loan."
    ssml = compiler.compile(text, [cue])
    assert '<break time="300ms"/>the real cost' in ssml
    assert SSMLValidator().validate(ssml).is_valid is True


def test_compiler_applies_pause_before_and_after_ms():
    compiler = SSMLCompiler()
    cue = VoiceCue(anchor="thirty years", pause_before_ms=250, pause_after_ms=450)
    text = "Banks stretch your loan tenure to thirty years. The monthly burden drops."
    ssml = compiler.compile(text, [cue])
    assert '<break time="250ms"/>thirty years<break time="450ms"/>' in ssml
    assert SSMLValidator().validate(ssml).is_valid is True


def test_compiler_applies_rate_percent_and_cue_id():
    compiler = SSMLCompiler()
    cue = VoiceCue(cue_id="cue_reveal", anchor="explodes", rate_percent=94, volume_db=2)
    text = "Total interest explodes over time."
    ssml = compiler.compile(text, [cue])
    assert '<mark name="cue_reveal"/>' in ssml
    assert '<prosody rate="94%" volume="+2dB">explodes</prosody>' in ssml
    assert SSMLValidator().validate(ssml).is_valid is True


def test_voice_cue_model_syncs_rate_and_rate_percent():
    cue1 = VoiceCue(anchor="word", rate_percent=96)
    assert cue1.rate == 96
    assert cue1.rate_percent == 96

    cue2 = VoiceCue(anchor="word", rate=95)
    assert cue2.rate == 95
    assert cue2.rate_percent == 95


def test_compiler_with_all_supported_fields_validates():
    compiler = SSMLCompiler()
    cue = VoiceCue(
        cue_id="cue_01",
        anchor="₹50,000",
        pause_before_ms=300,
        pause_after_ms=400,
        rate_percent=95,
        volume_db=2,
        pronunciation="fifty thousand rupees",
    )
    text = "You end up losing ₹50,000 in additional fees."
    ssml = compiler.compile(text, [cue])
    assert '<mark name="cue_01"/>' in ssml
    assert '<break time="300ms"/>' in ssml
    assert '<prosody rate="95%" volume="+2dB">' in ssml
    assert '<sub alias="fifty thousand rupees">₹50,000</sub>' in ssml
    assert '<break time="400ms"/>' in ssml
    val = SSMLValidator().validate(ssml)
    assert val.is_valid is True, f"Validation failed: {val.errors}"


def test_compiler_applies_global_rate_and_nested_cue_overrides():
    compiler = SSMLCompiler(default_rate=96)
    cue = VoiceCue(cue_id="cue_reveal", anchor="tenfold", rate_percent=94, volume_db=2)
    text = "The systemic deficit grows tenfold over the decade."
    ssml = compiler.compile(text, [cue], section_mark="scene_03_start")

    # Global envelope
    assert '<prosody rate="96%">' in ssml
    assert '<mark name="scene_03_start"/>' in ssml
    # Local override
    assert '<prosody rate="94%" volume="+2dB">tenfold</prosody>' in ssml

    val = SSMLValidator().validate(ssml)
    assert val.is_valid is True, f"Validation failed: {val.errors}"


def test_compiler_reads_polly_global_rate_env_var(monkeypatch):
    monkeypatch.setenv("POLLY_GLOBAL_RATE", "96")
    compiler = SSMLCompiler()
    assert compiler.default_rate == 96

    text = "A simple plain sentence with global pacing."
    ssml = compiler.compile(text)
    assert '<prosody rate="96%">A simple plain sentence with global pacing.</prosody>' in ssml
    assert SSMLValidator().validate(ssml).is_valid is True
