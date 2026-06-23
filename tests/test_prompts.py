from src.prompts import get_system_prompt


class TestGetSystemPrompt:
    def test_constructive_style(self):
        prompt = get_system_prompt("constructive")
        assert "constructive" in prompt.lower()

    def test_strict_style(self):
        prompt = get_system_prompt("strict")
        assert "strict" in prompt.lower()

    def test_concise_style(self):
        prompt = get_system_prompt("concise")
        assert "brief" in prompt.lower() or "concise" in prompt.lower()

    def test_unknown_style_defaults_to_constructive(self):
        prompt = get_system_prompt("unknown")
        assert "constructive" in prompt.lower()
