import subprocess
import re

def get_hackrf_serial_numbers():
    try:
        result = subprocess.run(["hackrf_info"], capture_output=True, text=True, check=True)
        output = result.stdout

        # Находим все серийные номера
        serials = re.findall(r"Serial number:\s*([0-9a-fA-F]{32})", output)
        return serials

    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении hackrf_info:", e)
        return []
    except FileNotFoundError:
        print("Утилита hackrf_info не найдена. Убедитесь, что HackRF Tools установлены и добавлены в PATH.")
        return []

# Пример использования
if __name__ == "__main__":
    serials = get_hackrf_serial_numbers()
    print("Найдено устройств:", len(serials))
    for i, s in enumerate(serials):
        print(f"Устройство {i}: Serial = {s}")
