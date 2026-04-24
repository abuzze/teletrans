from __future__ import annotations
import random
from thefuzz import fuzz


class QuizSession:
    def __init__(self, words: list[dict], num_questions: int = 5):
        self.questions = random.sample(words, min(num_questions, len(words)))
        self.current_index = 0
        self.score = 0
        self.total = len(self.questions)

    @property
    def is_finished(self) -> bool:
        return self.current_index >= self.total

    @property
    def current_word(self) -> dict | None:
        if self.is_finished:
            return None
        return self.questions[self.current_index]

    def check_answer(self, user_answer: str) -> tuple[bool, str]:
        word = self.current_word
        if word is None:
            return False, ""

        correct = word.get("Deutsch", "")
        # Strip article for comparison (der/die/das)
        correct_clean = _strip_article(correct).lower().strip()
        answer_clean = _strip_article(user_answer).lower().strip()

        ratio = fuzz.ratio(correct_clean, answer_clean)

        self.current_index += 1

        if ratio >= 85:
            self.score += 1
            return True, correct
        else:
            return False, correct

    def get_summary(self) -> str:
        pct = (self.score / self.total * 100) if self.total > 0 else 0
        if pct == 100:
            emoji = "🎉"
        elif pct >= 70:
            emoji = "👍"
        elif pct >= 40:
            emoji = "📚"
        else:
            emoji = "💪"

        return (
            f"{emoji} Quiz beendet!\n\n"
            f"Ergebnis: {self.score}/{self.total} ({pct:.0f}%)\n"
        )


def _strip_article(word: str) -> str:
    for article in ("der ", "die ", "das ", "il ", "la ", "lo ", "l'", "le ", "i ", "gli "):
        if word.lower().startswith(article):
            return word[len(article):]
    return word
