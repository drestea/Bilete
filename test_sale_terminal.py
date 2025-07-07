import serial
import time

def crc16(data: bytes) -> bytes:
    crc = 0x0000
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x8005) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc.to_bytes(2, 'little')  # LSB first

def build_sale_message(amount: float, currency="RON", currency_code="946", unique_id="000000000001"):
    amount_str = str(int(round(amount * 100))).zfill(12).encode()
    cashback = b"000000000000"

    payload = bytearray()
    payload += b'\xA0\x00\x01\x02'                     # A000 = Sale
    payload += b'\xA0\x01\x0C' + amount_str            # A001 = Amount (12 digits)
    payload += b'\xA0\x02\x03' + currency.encode()     # A002 = Currency ("RON")
    payload += b'\xA0\x03\x03' + currency_code.encode()# A003 = Currency code ("946")
    payload += b'\xA0\x08\x0C' + unique_id.encode()    # A008 = Unique ID
    payload += b'\xA0\x07\x0C' + cashback              # A007 = Cashback (0)

    msg = bytearray()
    msg.append(0x02)  # STX
    msg += len(payload).to_bytes(2, 'big')  # Length MSB-LSB
    msg += payload
    msg.append(0x03)  # ETX
    msg += crc16(msg[1:])  # CRC pe [LEN+PAYLOAD+ETX], fără STX

    return msg

def test_sale(port="COM9", amount=12.34):
    with serial.Serial(port, 115200, timeout=2) as ser:
        print("👉 Trimitem ENQ (\\x05)...")
        ser.write(b'\x05')
        ack = ser.read(1)
        if ack != b'\x06':
            print("❌ N-am primit ACK după ENQ, ci:", ack)
            return
        print("✅ ACK primit. Trimitem comanda SALE...")
        msg = build_sale_message(amount)
        ser.write(msg)
        ack2 = ser.read(1)
        if ack2 != b'\x06':
            print("❌ N-am primit ACK după mesaj, ci:", ack2)
            return
        print("✅ ACK primit după mesaj. Așteptăm răspuns de la terminal...")
        time.sleep(1.5)
        rasp = ser.read(512)
        print("📦 Răspuns brut:", rasp)

if __name__ == "__main__":
    test_sale(port="COM9", amount=12.34)