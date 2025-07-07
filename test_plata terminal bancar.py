import serial
import time

def crc16(data: bytes) -> bytes:
    # CRC-16/BUYPASS, polinom 0x8005, initial 0x0000
    crc = 0x0000
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if (crc & 0x8000):
                crc = ((crc << 1) ^ 0x8005) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc.to_bytes(2, 'big')

def build_sale_message(amount_bani: float, currency="RON", currency_code="946", unique_id="000000000001"):
    # amount_bani: ex 12.34 -> "000000001234"
    suma_int = int(round(amount_bani * 100))
    suma_str = str(suma_int).zfill(12)
    # Fără cashback
    cashback = "000000000000"
    # Construim payload-ul
    payload = bytearray()
    payload += b'\xA0\x00\x01\x02'  # Tag A000, LEN 1, 02 = Sale
    payload += b'\xA0\x01\x0C' + suma_str.encode()  # Tag A001, LEN 12, suma
    payload += b'\xA0\x02\x03' + currency.encode()  # Tag A002, LEN 3, RON
    payload += b'\xA0\x03\x03' + currency_code.encode()  # Tag A003, LEN 3, 946
    payload += b'\xA0\x08\x0C' + unique_id.encode()  # Tag A008, LEN 12, unique id
    payload += b'\xA0\x07\x0C' + cashback.encode()  # Tag A007, LEN 12, cashback
    # Încapsulăm în pachet complet
    msg = bytearray()
    msg.append(0x02)  # STX
    msg += len(payload).to_bytes(2, 'big')  # Length (MSB, LSB)
    msg += payload
    msg.append(0x03)  # ETX
    msg += crc16(msg[1:])  # CRC pe tot fără STX
    return msg

def test_sale(port="COM9", suma=12.34):
    ser = serial.Serial(port, 115200, timeout=2)
    print("Trimitem ENQ...")
    ser.write(b'\x05')
    ack = ser.read(1)
    if ack != b'\x06':
        print("Nu am primit ACK după ENQ, răspuns:", ack)
        ser.close()
        return
    print("ACK primit. Trimit mesaj de vânzare...")
    msg = build_sale_message(suma)
    ser.write(msg)
    ack2 = ser.read(1)
    if ack2 != b'\x06':
        print("Nu am primit ACK după mesaj, răspuns:", ack2)
        ser.close()
        return
    print("ACK primit după mesaj. Aștept răspuns de la terminal...")
    # Citim răspunsul (poate fi lung, vezi exemplele din doc)
    time.sleep(1)
    rasp = ser.read(256)
    print("Răspuns brut:", rasp)
    ser.close()

if __name__ == "__main__":
    test_sale(port="COM9", suma=12.34)