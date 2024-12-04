import re
import unicodedata
from typing import List, Callable


class MovieData:
    def __init__(self):
        self.title = None
        self.release_date = None
        self.country_of_origin = []
        self.flags_of_origin = []
        self.directors = []
        self.writers = []
        self.cast = []
        self.languages = []
        self.flags_of_language = []
        self.subtitles = []
        self.flags_of_subtitles = []
        self.genres = []
        self.tags = []
        self.synopsis = None
        self.curiosities = None

    def to_dict(self):
        return {
            "title": self.title,
            "release_date": self.release_date,
            "country_of_origin": self.country_of_origin,
            "flags_of_origin": self.flags_of_origin,
            "directors": self.directors,
            "writers": self.writers,
            "cast": self.cast,
            "languages": self.languages,
            "flags_of_language": self.flags_of_language,
            "subtitles": self.subtitles,
            "flags_of_subtitles": self.flags_of_subtitles,
            "genres": self.genres,
            "tags": self.tags,
            "synopsis": self.synopsis,
            "curiosities": self.curiosities,
        }


class FieldDefinition:
    def __init__(
        self,
        field: str,
        labels: List[str],
        regex: List[str],
        process: Callable,
        is_multiline: bool = False,
    ):
        self.field = field
        self.labels = labels
        self.regex = [re.compile(r) for r in regex]
        self.process = process
        self.is_multiline = is_multiline


def is_emoji(character: str) -> bool:
    if unicodedata.category(character) == 'So':  # 'So' é a categoria para símbolos e outros
        return True
    if ord(character) in range(0x1F1E6, 0x1F1FF):  # Bandera (letras A-Z e combinações de bandeiras)
        return True
    return False


def process_title(match, data, buffer=None):
    data.title = match.group(1).strip()
    if match.group(2):
        data.release_date = match.group(2)


def process_country_of_origin(match, data, buffer=None):
    countries = [c.strip() for c in match.group(1).split("|") if c.strip()]
    data.country_of_origin = []
    data.flags_of_origin = []
    for country in countries:
        flags = "".join([char for char in country if is_emoji(char)])
        if flags:
            data.flags_of_origin.append(flags)
        country_name = "".join([char for char in country if not is_emoji(char)]).strip()
        if country_name.startswith("#"):
            country_name = country_name[1:]
        if country_name:
            data.country_of_origin.append(country_name)


def process_directors(match, data, buffer=None):
    names = [d.strip() for d in match.group(1).split("#") if d.strip()]
    if "Direção/Roteiro" in match.group(0):
        data.directors.extend(names)
        data.writers.extend(names)
    else:
        data.directors.extend(names)


def process_writers(match, data, buffer=None):
    writers = [w.strip() for w in match.group(1).split("#") if w.strip()]
    data.writers.extend(writers)


def process_cast(match, data, buffer=None):
    data.cast = [c.strip() for c in match.group(1).split("#") if c.strip()]


def process_languages(match, data, buffer=None):
    languages = [l.strip() for l in match.group(1).split("|") if l.strip()]
    data.languages = []
    data.flags_of_language = []
    for language in languages:
        flags = "".join([char for char in language if is_emoji(char)])
        if flags:
            data.flags_of_language.append(flags)
        language_name = (
            "".join([char for char in language if not is_emoji(char)])
            .replace("#", "")
            .strip()
        )
        if language_name:
            data.languages.append(language_name)


def process_subtitles(match, data, buffer=None):
    subtitles = [s.strip() for s in match.group(1).split("|") if s.strip()]
    data.subtitles = []
    data.flags_of_subtitles = []
    for subtitle in subtitles:
        flags = "".join([char for char in subtitle if is_emoji(char)])
        if flags:
            data.flags_of_subtitles.append(flags)
        subtitle_language = (
            "".join([char for char in subtitle if not is_emoji(char)])
            .replace("#", "")
            .strip()
        )
        if subtitle_language:
            data.subtitles.append(subtitle_language)


def process_genres(match, data, buffer=None):
    data.genres = [g.strip() for g in match.group(1).split("#") if g.strip()]


def process_multiline(match, data, buffer):
    if match.group(1) and match.group(1).strip():
        buffer.append(match.group(1).strip())


field_definitions = [
    FieldDefinition(
        "title",
        ["📺", "Título:"],
        [r"^.*?(?:📺|Título:)\s*(.*?)(?:\s*[-—:]?\s*#(\d{4})y?)?$"],
        process_title,
    ),
    FieldDefinition(
        "country_of_origin",
        ["País de Origem:", "📍 País de Origem:", "Pais de Origem:"],
        [r"^.*?Pa[íi]s de Origem:\s*(.*)$"],
        process_country_of_origin,
    ),
    FieldDefinition(
        "directors",
        ["Direção:", "Diretor:", "👑 Direção:", "👑 Direção/Roteiro:"],
        [r"^.*?(?:Direção|Diretor|Direção\/Roteiro):\s*(.*)$"],
        process_directors,
    ),
    FieldDefinition(
        "writers",
        ["Roteiro:", "Roteirista:", "Roteiristas:", "✏️ Roteirista:", "✏️ Roteiristas:"],
        [r"^.*?(?:Roteiro|Roteirista|Roteiristas):\s*(.*)$"],
        process_writers,
    ),
    FieldDefinition(
        "cast", ["Elenco:", "✨ Elenco:"], [r"^.*?Elenco:\s*(.*)$"], process_cast
    ),
    FieldDefinition(
        "languages",
        ["Idioma:", "Idiomas:", "📣 Idiomas:", "💬 Idiomas:"],
        [r"^.*?(?:Idiomas?|Idioma):\s*(.*)$"],
        process_languages,
    ),
    FieldDefinition(
        "subtitles",
        ["Legenda:", "Legendado:", "💬 Legendado:"],
        [r"^.*?(?:Legenda|Legendado):\s*(.*)$"],
        process_subtitles,
    ),
    FieldDefinition(
        "genres",
        ["Gênero:", "Gêneros:", "🎭 Gêneros:"],
        [r"^.*?(?:Gêneros?|Gênero):\s*(.*)$"],
        process_genres,
    ),
    FieldDefinition(
        "synopsis",
        ["Sinopse", "🗣 Sinopse:", "🗣 Sinopse"],
        [r"^.*?(?:Sinopse|🗣 Sinopse)[:：]?\s*(.*)$"],
        lambda match, data, buffer: process_multiline(match, data, buffer),
        is_multiline=True,
    ),
    FieldDefinition(
        "curiosities",
        ["Curiosidades:", "💡 Curiosidades:"],
        [r"^.*?Curiosidades[:：]?\s*(.*)$"],
        lambda match, data, buffer: process_multiline(match, data, buffer),
        is_multiline=True,
    ),
]


def parse_message_content(content: str) -> MovieData:
    lines = [line.strip() for line in content.split("\n")]

    data_info = MovieData()
    multiline_buffer = []
    current_field = None

    end_of_field_markers = [
        "▶",
        "▶️",
        "Para outros conteúdos",
        "💡 Curiosidades:",
        "🥇 Prêmios:",
        "🥈 Prêmios:",
        "Prêmios:",
        "Clique Para Entrar",
        "🚨 Para outros conteúdos",
        "📣 Idiomas:",
        "💬 Legendado:",
        "📣",
        "💬",
        "#",
        "✨ Elenco:",
    ]

    def line_starts_with_label(line: str, labels: List[str]) -> bool:
        return any(re.match(f"^.*?{re.escape(label)}", line) for label in labels)

    for line in lines:
        if not line:
            continue

        if current_field:
            is_new_field = any(
                line_starts_with_label(line, field_def.labels)
                for field_def in field_definitions
            )
            is_end_of_field = any(
                line_starts_with_label(line, [marker])
                for marker in end_of_field_markers
            )
            if is_new_field or is_end_of_field:
                setattr(data_info, current_field, " ".join(multiline_buffer).strip())
                current_field = None
                multiline_buffer = []
                if is_new_field:
                    continue
            else:
                multiline_buffer.append(line)
                continue

        if line.startswith("#"):
            tags = [t.strip() for t in line.split("#") if t.strip()]
            data_info.tags.extend(tags)
            continue

        for field_def in field_definitions:
            for regex in field_def.regex:
                match = regex.match(line)
                if match:
                    field_def.process(match, data_info, multiline_buffer)
                    if field_def.is_multiline:
                        current_field = field_def.field
                        multiline_buffer = []
                        if match.group(1) and match.group(1).strip():
                            multiline_buffer.append(match.group(1).strip())
                    break
            if current_field:
                break

    if current_field:
        setattr(data_info, current_field, " ".join(multiline_buffer).strip())

    return data_info
