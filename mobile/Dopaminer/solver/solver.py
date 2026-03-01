files = ['1.jpeg', '2.jpeg', '3.jpeg', '4.3gp']

for file_name in files:
    with open('uploads/' + file_name, "rb") as file_r:
        file = file_r.read()
    
    if ".jpeg" in file_name:
        file = b"\xff\xd8\xff" + file[3:]
    
    with open(file_name, "wb") as file_w:
        file_w.write(file)