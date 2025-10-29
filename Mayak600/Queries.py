# pip install pymodbus==3.5.3
import asyncio
from datetime import datetime
from pymodbus.client import AsyncModbusTcpClient

# ==== CONFIG: подставь адреса регистров из вашей карты обмена ====
PLC_IP = "192.168.0.201"
PLC_PORT = 23
UNIT_ID = 1
POLL_MS = 500  # период опроса, мс

# Если значения в 32-бит float (обычно так для позиций/скоростей),
# то каждый параметр занимает ДВА 16-битных регистра подряд (Hi/Lo или Lo/Hi).
# Укажи base-адрес старшего слова и порядок слов.
REG = {
    "X_pos":   {"addr": 5000, "type": "float32", "word_order": "HI_LO"},
    "Y_pos":   {"addr": 5002, "type": "float32", "word_order": "HI_LO"},
    "Z_pos":   {"addr": 5004, "type": "float32", "word_order": "HI_LO"},
    # "A_pos": {"addr": 5006, "type": "float32", "word_order": "HI_LO"},  # опционально

    "F_cmd":   {"addr": 5200, "type": "float32", "word_order": "HI_LO"},
    "F_act":   {"addr": 5202, "type": "float32", "word_order": "HI_LO"},

    "S_cmd":   {"addr": 2100, "type": "float32", "word_order": "HI_LO"},
    "S_act":   {"addr": 2102, "type": "float32", "word_order": "HI_LO"},

    # Примеры для кадра/режима, если есть:
    # "BlockNo": {"addr": 7000, "type": "uint16"},
    # "Mode":    {"addr": 7001, "type": "uint16"},  # 0=STOP,1=AUTO,2=JOG, и т.п.
}

# ===== helpers =====
# ===== helpers =====
import struct
from numbers import Number

def words_to_float32(hi, lo, order="HI_LO"):
    if order == "HI_LO":
        packed = struct.pack(">HH", hi, lo)
    else:  # "LO_HI"
        packed = struct.pack(">HH", lo, hi)
    return struct.unpack(">f", packed)[0]

def words_to_uint32(hi, lo, order="HI_LO"):
    return (hi << 16) | lo if order == "HI_LO" else (lo << 16) | hi

def safe_fmt(v, fmt="{:.3f}", default="—"):
    """Форматирует только числа, иначе отдаёт строку/дефолт."""
    if isinstance(v, Number):
        try:
            return fmt.format(v)
        except Exception:
            return str(v)
    return default if v is None else str(v)

async def read_param(client, addr, type_, word_order="HI_LO"):
    if type_ in ("float32", "uint32"):
        rr = await client.read_holding_registers(addr=addr, count=2, unit=UNIT_ID)
        if rr.isError():
            raise RuntimeError(rr)
        hi, lo = rr.registers[0], rr.registers[1]
        if type_ == "float32":
            return words_to_float32(hi, lo, word_order)
        else:
            return words_to_uint32(hi, lo, word_order)
    elif type_ == "uint16":
        rr = await client.read_holding_registers(addr=addr, count=1, unit=UNIT_ID)
        if rr.isError():
            raise RuntimeError(rr)
        return rr.registers[0]
    else:
        raise ValueError(f"Unsupported type {type_}")

async def poll():
    client = AsyncModbusTcpClient(PLC_IP, port=PLC_PORT)
    await client.connect()
    try:
        while True:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            out = {"ts": ts}
            for name, meta in REG.items():
                try:
                    val = await read_param(client, meta["addr"], meta["type"], meta.get("word_order","HI_LO"))
                    out[name] = val
                except Exception as e:
                    out[name] = f"ERR:{e.__class__.__name__}"
            # форматированный вывод одной строкой
            x = safe_fmt(out.get("X_pos"), "{:.3f}")
            y = safe_fmt(out.get("Y_pos"), "{:.3f}")
            z = safe_fmt(out.get("Z_pos"), "{:.3f}")

            f_act = safe_fmt(out.get("F_act"), "{:.1f}")
            f_cmd = safe_fmt(out.get("F_cmd"), "{:.1f}")

            s_act = safe_fmt(out.get("S_act"), "{:.0f}")
            s_cmd = safe_fmt(out.get("S_cmd"), "{:.0f}")

            print(f'{out["ts"]} | X={x}  Y={y}  Z={z} | F={f_act} (cmd {f_cmd}) | S={s_act} rpm (cmd {s_cmd})')

            await asyncio.sleep(POLL_MS/1000)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(poll())
