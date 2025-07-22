import socket
import struct
import threading
import time
import shutil
import os
from datetime import datetime

class MachineClient:
    def __init__(self, server_ip="192.168.0.201", server_port=23321, keepalive_limit=12,
                 reconnect_delay=5, archives_limit_mb=5, log_dir="."):
        self.server_ip = server_ip
        self.server_port = server_port
        self.keepalive_limit = keepalive_limit
        self.reconnect_delay = reconnect_delay
        self.archives_limit_mb = archives_limit_mb
        self.log_dir = log_dir

        self.sock = None
        self.g_packetcnt = 0
        self.alive_packets_from_server = 0
        self.running = False
        self.listener_thread = None
        self.log_file = None

        self.signal_map = {
            0: "Сброс ЧПУ",
            1: "Маховик",
            2: "Режим работы ЧПУ",
            3: "Готовность ЧПУ",
            # Добавляй остальные сигналы по необходимости
        }

    def connect(self):
        try:
            self.sock = socket.create_connection((self.server_ip, self.server_port), timeout=5)
            print(f"[INFO] Соединение с {self.server_ip}:{self.server_port} установлено.")
            return True
        except socket.error as e:
            print(f"[ERROR] Не удалось подключиться: {e}")
            return False

    def perform_handshake(self):
        try:
            data = self.sock.recv(4)
            if len(data) < 4:
                raise RuntimeError("Получено недостаточно данных при рукопожатии.")

            server_value = struct.unpack("i", data)[0]
            print(f"[INFO] Получено число от сервера: {server_value}")
            if server_value < 2:
                raise ValueError(f"Некорректное значение от сервера: {server_value}")

            signature = struct.pack("2i", 0, 1)
            sent = self.sock.send(signature)
            if sent != 8:
                raise RuntimeError("Ошибка при отправке сигнатуры.")

            print("[INFO] Сигнатура [0, 1] отправлена серверу.")
            return True
        except Exception as e:
            print(f"[ERROR] Handshake не удался: {e}")
            return False

    def open_log_file(self):
        filename = os.path.join(self.log_dir, f"passport_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dmp")
        self.log_file = open(filename, "w", encoding="utf-8")
        print(f"[INFO] Лог файл открыт: {filename}")

    def check_disk_space(self):
        total, used, free = shutil.disk_usage(self.log_dir)
        free_mb = free / (1024 * 1024)
        if free_mb < self.archives_limit_mb:
            self.log(f"[WARNING] Недостаточно места на диске: {free_mb:.2f} MB осталось.")
            return False
        return True

    def log(self, text):
        print(text)
        if self.log_file:
            self.log_file.write(text + "\n")
            self.log_file.flush()

    def parse_passport_header(self, data):
        if len(data) < 14:
            self.log("[ERROR] Заголовок слишком короткий.")
            return None
        signature, ptype, timestamp, length, chksum = struct.unpack("<HHI I H", data[:14])
        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        return {
            "signature": signature,
            "type": ptype,
            "timestamp": timestamp,
            "time_str": time_str,
            "length": length,
            "chksum": chksum
        }

    def handle_server_messages(self):
        try:
            self.open_log_file()
            while self.running:
                if not self.check_disk_space():
                    self.log("[ERROR] Архивирование прекращено из-за нехватки места.")
                    break

                header_data = self.sock.recv(14)
                if not header_data:
                    self.log("[WARNING] Сервер закрыл соединение.")
                    break

                header = self.parse_passport_header(header_data)
                if not header:
                    break

                payload_len = header["length"] - 14
                payload = b""
                while len(payload) < payload_len:
                    chunk = self.sock.recv(payload_len - len(payload))
                    if not chunk:
                        self.log("[WARNING] Разрыв при чтении payload.")
                        break
                    payload += chunk

                self.process_passport_packet(header, payload)

        except socket.error as e:
            self.log(f"[ERROR] Ошибка в потоке приёма: {e}")
        finally:
            if self.log_file:
                self.log_file.close()
                self.log_file = None
                print("[INFO] Лог файл закрыт.")
            self.close()

    def process_passport_packet(self, header, payload):
        ptype = header["type"]
        time_str = header["time_str"]
        out = ""

        if ptype == 0xFFFF:  # PASSPORT_IAMALIVE
            self.alive_packets_from_server += 1
            self.g_packetcnt = (self.g_packetcnt + 1) % 256
            self.sock.send(struct.pack("B", self.g_packetcnt))
            out = f"[KEEPALIVE] {time_str} Ответ отправлен. Счётчик: {self.g_packetcnt}"
            print(out, end="\r", flush=True)
            return  # Не пишем в лог

        # Обработка остальных пакетов
        if ptype == 0:
            text = payload[2:].decode("koi8-r", errors="ignore").strip()
            out = f"{time_str} OPEN {text}"
        elif ptype == 1:
            text = payload[2:].decode("koi8-r", errors="ignore").strip()
            out = f"{time_str} CLOSE {text}"
        elif ptype == 2:
            id_val = struct.unpack("<H", payload[2:4])[0]
            text = payload[6:].decode("koi8-r", errors="ignore").strip()
            out = f"{time_str} DATADESCRIPTION {id_val} {text}"
        elif ptype == 3:
            id_val, dtype, step, zip_ = struct.unpack("<H H H H", payload[2:10])
            dtype_str = f"TEXT(7)" if dtype == 7 else f"INT({dtype})"
            out = f"{time_str} DATATYPE {id_val} {dtype_str} step={step} zip={zip_}"
        elif ptype == 4:
            id_val = struct.unpack("<H", payload[2:4])[0]
            name = self.signal_map.get(id_val, f"Signal {id_val}")
            if len(payload) > 6:
                try:
                    text = payload[6:].decode("koi8-r").strip()
                    out = f"{time_str} DATA {id_val} {name} = {text}"
                except UnicodeDecodeError:
                    nums = struct.iter_unpack("<I", payload[6:])
                    numbers = " ".join(str(n[0]) for n in nums)
                    out = f"{time_str} DATA {id_val} {name} = {numbers}"
            else:
                out = f"{time_str} DATA {id_val} {name}"
        elif ptype == 5:
            id_val = struct.unpack("<H", payload[2:4])[0]
            out = f"{time_str} DATAOVERFLOW {id_val}"
        elif ptype == 6:
            out = f"{time_str} --- DATABEGIN ---"
        elif ptype == 7:
            out = f"{time_str} --- DATAEND ---"
        elif ptype == 8:
            out = f"{time_str} DATASUSPEND"
        elif ptype == 9:
            out = f"{time_str} DATARESUME"
        elif ptype == 10:
            id_val = struct.unpack("<H", payload[2:4])[0]
            text = payload[6:].decode("koi8-r", errors="ignore").strip()
            out = f"{time_str} DATAFILENAME {id_val} {text}"
        elif ptype == 11:
            text = payload[2:].decode("koi8-r", errors="ignore").strip()
            out = f"{time_str} COMMENTARY {text}"
        elif ptype == 12:
            out = f"{time_str} ABORT"
        elif ptype == 13:
            text = payload[2:].decode("koi8-r", errors="ignore").strip()
            out = f"{time_str} EVENT {text}"
        else:
            out = f"{time_str} UNKNOWN TYPE {ptype}"

        self.log(out)

    def start_listener(self):
        self.listener_thread = threading.Thread(target=self.handle_server_messages, daemon=True)
        self.listener_thread.start()

    def run(self):
        self.running = True
        while self.running:
            if not self.connect():
                time.sleep(self.reconnect_delay)
                continue

            if not self.perform_handshake():
                self.close()
                time.sleep(self.reconnect_delay)
                continue

            self.start_listener()
            self.listener_thread.join()
            print(f"[INFO] Попытка переподключения через {self.reconnect_delay} сек...")
            time.sleep(self.reconnect_delay)

    def close(self):
        if self.sock:
            print("[INFO] Закрытие соединения.")
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self.sock.close()
            self.sock = None
