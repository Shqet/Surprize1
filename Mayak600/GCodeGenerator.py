def generate_gcode_program(program_number=1, rpm=1500, duration_minutes=3):
    """
    Генерирует G-код программу для станка Маяк 600 с минимально необходимыми командами.

    :param program_number: номер программы (1–9999), будет выведен как Oxxxx
    :param rpm: скорость вращения шпинделей в об/мин (100–4000)
    :param duration_minutes: время вращения в минутах (0.1–60)
    :return: строка с G-код программой
    :raises ValueError: если параметры выходят за допустимые пределы
    """
    if not (1 <= program_number <= 9999):
        raise ValueError("Номер программы должен быть от 1 до 9999.")
    if not (100 <= rpm <= 4000):
        raise ValueError("Скорость rpm должна быть от 100 до 4000 об/мин.")
    if not (0.1 <= duration_minutes <= 60):
        raise ValueError("Время duration_minutes должно быть от 0.1 до 60 минут.")

    duration_ms = int(duration_minutes * 60 * 1000)
    prog_num_str = f"O{program_number:04d}"

    gcode = f"""%
{prog_num_str}
G21
G90
G17
M3 S{rpm}
M4 S{rpm}
G4 P5000
G4 P{duration_ms}
M5
M30
%"""
    return gcode



if __name__ == "__main__":
    gcode_program = generate_gcode_program(rpm=1500, duration_minutes=1)
    print(gcode_program)