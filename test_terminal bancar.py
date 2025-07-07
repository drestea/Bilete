import serial

ser = serial.Serial('COM9', 115200, timeout=2)
ser.write(b'\x05')  # ENQ
response = ser.read(1)
print(response)  # Ar trebui să vezi b'\x06' dacă terminalul răspunde
ser.close()