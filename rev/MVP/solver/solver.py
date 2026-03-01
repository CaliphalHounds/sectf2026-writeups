import struct
from Crypto.Cipher import AES


with open('mvp.exe', 'rb') as f:
    pe_data = f.read()

dos_header = pe_data[:64]

e_lfanew = struct.unpack('<I', dos_header[0x3c:0x40])[0]

cert_table_offset = e_lfanew + 24 + 112 + 32

cert_rva = struct.unpack('<I', pe_data[cert_table_offset:cert_table_offset+4])[0]
cert_size = struct.unpack('<I', pe_data[cert_table_offset+4:cert_table_offset+8])[0]

certificate = pe_data[cert_rva:cert_rva+cert_size]

dll = certificate[0x5b0:]

cipher = AES.new(b'caliphal_labs!!!!!!!!!!!!!!!!!!!', AES.MODE_CBC, b'mvpmvpmvpmvpmvpm')
dll = cipher.decrypt(dll)

with open('dll.dll', 'wb') as file:
    file.write(dll)