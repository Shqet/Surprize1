from GCodeGenerator import generate_gcode_program
from UploadFile import upload_program_string

prog_num = 123
# gcode = generate_gcode_program(program_number=prog_num, rpm=1500, duration_minutes=0.5)


gcode = """%1
N10 M100 (Log: program started)
N20 G4 F20 (Internal 2-second pause)
N30 M101 (Log: pause complete)
N40 G4 F10 (Internal 1-second pause)
N50 M102 (Log: second pause complete)
N60 M2 (End of program)
M30 (End of file)
"""
# имя в формате O####.ISO
remote_name = f"O{prog_num:04d}.ISO"

msg = upload_program_string(
    host="192.168.0.201",
    program_text=gcode,
    remote_name=remote_name,
    share="env",
    subdir="ISO",     # туда Маяк смотрит для программ
    user="guest",
    password="",
    port=445          # если 445 закрыт, попробуй 139 и is_direct_tcp автоматически станет False
)
print(msg)