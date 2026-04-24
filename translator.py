from __future__ import annotations
import json
import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Du bist ein Italienisch-Deutsch Übersetzer und Sprachexperte.
Der Benutzer schickt dir ein Wort oder eine kurze Phrase — entweder auf Italienisch oder auf Deutsch.
Erkenne automatisch die Sprache und übersetze in die jeweils andere Sprache.

Du antwortest AUSSCHLIESSLICH mit einem JSON-Objekt (kein anderer Text) im folgenden Format:

{
  "italiano": "das italienische Wort/Phrase (mit Artikel bei Substantiven)",
  "deutsch": "die deutsche Übersetzung (mit Artikel bei Substantiven)",
  "richtung": "IT→DE" oder "DE→IT",
  "categoria": "Kategorie: Sostantivo/Verbo/Aggettivo/Avverbio/Preposizione/Congiunzione/Frase",
  "genere_it": "maschile/femminile/- (bei Nicht-Substantiven)",
  "genere_de": "maskulin/feminin/neutrum/- (bei Nicht-Substantiven)",
  "plurale_it": "Pluralform auf Italienisch (oder - falls nicht anwendbar)",
  "plurale_de": "Pluralform auf Deutsch (oder - falls nicht anwendbar)",
  "esempio_it": "Ein Beispielsatz auf Italienisch",
  "esempio_de": "Der gleiche Beispielsatz auf Deutsch"
}

Regeln:
- Erkenne automatisch ob die Eingabe Italienisch oder Deutsch ist
- Bei Substantiven immer den bestimmten Artikel angeben (il/la/lo/die/der/das)
- Bei Verben die Grundform (Infinitiv) angeben
- Der Beispielsatz soll einfach und alltagstauglich sein
- Bei Phrasen: categoria = "Frase"
- Antworte NUR mit dem JSON, kein zusätzlicher Text"""


def translate_word(word: str) -> dict | None:
    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": word.strip()}],
        )
        text = message.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]  # remove ```json line
            text = text.rsplit("```", 1)[0]  # remove closing ```
            text = text.strip()
        return json.loads(text)
    except (json.JSONDecodeError, anthropic.APIError, IndexError) as e:
        print(f"Translation error: {e}")
        return None
