# file: push_program_string_smb.py
from io import BytesIO
from smb.SMBConnection import SMBConnection

DEFAULT_UP = "null.iso"   # ← имя дефолтной УП из machine.cfg

def _ensure_path(conn: SMBConnection, share: str, path: str):
    """Создаёт цепочку каталогов (если их нет)."""
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            conn.createDirectory(share, cur)
        except Exception:
            # уже существует — ок
            pass

def normalize_gcode(gcode: str) -> bytes:
    """
    Приводим переводы строк к LF и кодировку к ASCII.
    Если есть не-ASCII символы, они будут отброшены (errors='ignore').
    """
    text = gcode.replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("ascii", errors="ignore")

def upload_program_string(
    host: str = "192.168.0.201",
    program_text: str = "",
    remote_name: str = "O0001.ISO",
    share: str = "env",
    subdir: str = "ISO",
    user: str = "guest",
    password: str = "",
    port: int = 445,
    my_name: str = "client",
    remote_name_for_auth: str = "majak",
):
    """
    Отправляет текст программы в \\host\share\subdir,
    записывает как remote_name и дублирует как null.iso (дефолтный файл).
    """
    is_direct = (port == 445)
    conn = SMBConnection(
        user, password,
        my_name=my_name,
        remote_name=remote_name_for_auth,
        use_ntlm_v2=True,
        is_direct_tcp=is_direct
    )
    if not conn.connect(host, port):
        raise RuntimeError(f"SMB connect to {host}:{port} failed")

    try:
        _ensure_path(conn, share, subdir)
        data = normalize_gcode(program_text)
        remote_path = f"{subdir}/{remote_name}".lstrip("/")
        default_path = f"{subdir}/{DEFAULT_UP}"

        # записываем как основное имя
        conn.storeFile(share, remote_path, BytesIO(data))
        # дублируем как null.iso
        conn.storeFile(share, default_path, BytesIO(data))

        return (
            f"Загружено: \\\\{host}\\{share}\\{remote_path} "
            f"и продублировано как \\\\{host}\\{share}\\{default_path} "
            f"({len(data)} байт)"
        )
    finally:
        conn.close()
