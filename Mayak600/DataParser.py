import re, unicodedata

_TRY_ENCODINGS = ("koi8-r", "cp1251", "cp866", "utf-8", "latin1")
# Часто встречающиеся токены/сочетания в EVENT/COMMENTARY
_TOKENS = (
    "Ошибка", "Команда", "Дт", "Чс", "Мн", "Ск",
    "ERROR", "EDIT", "G_", "SYNTAX", "CLOSE", "OPEN"
)

def _token_score(s: str) -> int:
    score = 0
    # Хиты по ключевым словам
    for t in _TOKENS:
        if t in s:
            score += 20
    # Бонус за читаемость
    for ch in s:
        cat = unicodedata.category(ch)
        if 'А' <= ch <= 'я' or ch in "Ёё":
            score += 2
        elif ch.isprintable():
            score += 1
        if cat.startswith('C'):  # control
            score -= 3
    # Штраф за «рамки»
    if re.fullmatch(r"[-—–]+", s):
        score -= 20
    return score

def _best_decode(b: bytes) -> str:
    best = ""
    best_score = -10**9
    for enc in _TRY_ENCODINGS:
        try:
            s = b.decode(enc, errors="ignore").strip()
            sc = _token_score(s)
            if sc > best_score:
                best, best_score = s, sc
        except Exception:
            pass
    return best

_BOX = set("─━│┃┄┅┆┇┈┉┊┋┌┐└┘├┤┬┴┼╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬")

def _clean_segment(s: str) -> str:
    # убрать рамочные символы, длинные «----»
    s = "".join(ch for ch in s if ch not in _BOX).strip()
    s = re.sub(r"^[-—–\s]+|[-—–\s]+$", "", s)
    # убрать лидирующий мусор до первой буквы/цифры/подчёркивания
    s = re.sub(r"^[^\wА-Яа-яЁё]+", "", s)
    return s

def _split_cstrings(payload: bytes) -> list[str]:
    parts = payload.split(b"\x00")
    out = []
    for p in parts:
        if not p:
            continue
        s = _best_decode(p)
        s = _clean_segment(s)
        if s and not re.fullmatch(r"[-—–]+", s):
            out.append(s)
    # склей «Дт-Чс-Мн-Ск» в один сегмент (если распалось)
    if any(x in out for x in ("Дт", "Чс", "Мн", "Ск")):
        merged = []
        buf = []
        for seg in out:
            if seg in ("Дт", "Чс", "Мн", "Ск") or re.fullmatch(r"(Дт|Чс|Мн|Ск)(-[ДтЧсМнСк]+)?", seg):
                buf.append(seg)
            else:
                if buf:
                    merged.append("Дт-Чс-Мн-Ск")
                    buf = []
                merged.append(seg)
        if buf:
            merged.append("Дт-Чс-Мн-Ск")
        out = merged
    return out
