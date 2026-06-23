from unittest.mock import patch
from src.reviewer import review_diff


class TestReviewDiff:
    def test_unknown_provider_raises_error(self):
        try:
            review_diff("diff", "unknown", None, "", "constructive")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "unknown" in str(e).lower()

    @patch("src.reviewer.openai_review")
    def test_openai_provider(self, mock_review):
        mock_review.return_value = "Looks good!"
        result = review_diff("diff", "openai", "sk-test", "gpt-4", "constructive")
        assert result == "Looks good!"
        mock_review.assert_called_once_with("diff", "gpt-4", "sk-test", "constructive")

    def test_openai_without_key_raises_error(self):
        try:
            review_diff("diff", "openai", None, "", "constructive")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "API key" in str(e).lower()

    @patch("src.reviewer.anthropic_review")
    def test_anthropic_provider(self, mock_review):
        mock_review.return_value = "Good code!"
        result = review_diff("diff", "anthropic", "sk-ant-test", "claude-3", "strict")
        assert result == "Good code!"

    def test_anthropic_without_key_raises_error(self):
        try:
            review_diff("diff", "anthropic", None, "", "strict")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "API key" in str(e).lower()

    @patch("src.reviewer.ollama_review")
    def test_ollama_provider(self, mock_review):
        mock_review.return_value = "Nice work!"
        result = review_diff("diff", "ollama", None, "codellama", "concise")
        assert result == "Nice work!"
        mock_review.assert_called_once_with("diff", "codellama", "http://localhost:11434", "concise")
