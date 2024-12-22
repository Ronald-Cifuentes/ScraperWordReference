import requests
from bs4 import BeautifulSoup
import json
import os


class ScraperWordReference:
    def __init__(self, filename="dictionary.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def get_means_wordreference(self, word):
        """Extrae las definiciones de una palabra desde WordReference."""
        url = f"https://www.wordreference.com/definicion/{word}"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "es-ES,es;q=0.9",
            "cookie": "llang=esesi",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            definitions = []
            entries = soup.select("#otherDicts .trans.esp")
            for entry in entries:
                for li in entry.find_all("li"):
                    definition = li.get_text(" ", strip=True)
                    definitions.append(self._clean_text(definition))

            if not definitions:
                return []
            return definitions
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud HTTP: {e}")
            return []
        except Exception as e:
            print(f"Error al procesar el HTML: {e}")
            return []

    def _clean_text(self, text):
        """Limpia el texto eliminando caracteres especiales y asegurando espacios correctos."""
        return (
            text.replace("\n", " ")
            .replace("\t", " ")
            .replace("\u00a0", " ")
            .replace("  ", " ")
        )

    def read_dictionary(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def write_word(self, word, definitions):
        data = self.read_dictionary()
        if word in data:
            existing_means = set(data[word].get("means", []))
            new_definitions = [d for d in definitions if d not in existing_means]
            if new_definitions:
                data[word]["means"].extend(new_definitions)
                print(f"Nuevas definiciones añadidas a la palabra '{word}'.")
            else:
                print(
                    f"No se encontraron nuevas definiciones para la palabra '{word}'."
                )
        else:
            data[word] = {"means": definitions}
            print("Palabra añadida exitosamente.")

        self._write_to_file(data)

    def fetch_and_save_word(self, word):
        definitions = self.get_means_wordreference(word)
        if definitions:
            self.write_word(word, definitions)

    def fetch_and_save_words_from_file(self, filepath, start_word=None):
        if not os.path.exists(filepath):
            print(f"El archivo '{filepath}' no existe.")
            return

        with open(filepath, "r", encoding="utf-8") as file:
            words = file.read().splitlines()

        start_index = 0
        if start_word:
            try:
                start_index = words.index(start_word)
            except ValueError:
                print(f"La palabra '{start_word}' no se encontró en el archivo.")
                return

        for word in words[start_index:]:
            print(f"Procesando palabra: {word}")
            self.fetch_and_save_word(word)

    def _write_to_file(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# Uso del programa
if __name__ == "__main__":
    manager = ScraperWordReference()
    word_file = "diccionario_espanol.txt"

    # Especifica desde qué palabra comenzar (opcional)
    start_word = "a"  # Cambiar a la palabra deseada o dejar como None
    manager.fetch_and_save_words_from_file(word_file, start_word=start_word)
