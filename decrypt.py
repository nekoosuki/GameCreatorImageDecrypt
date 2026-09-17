import os

def decrypt_gc_png(data: bytearray) -> bytes:
    file_len = len(data)
    if file_len < 3:
        return bytes(data)

    # 1. 恢复文件头 (交换 index 1 和 2)
    data[1], data[2] = data[2], data[1]

    # 2. 计算正中间脏字节的位置
    fake_byte_pos = (file_len - 1) // 2

    # 3. 剔除脏字节
    return bytes(data[:fake_byte_pos] + data[fake_byte_pos + 1:])


def decrypt_png(input_file_path: str, output_file_path: str) -> None:
    with open(input_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = decrypt_gc_png(bytearray(encrypted_data))

    with open(output_file_path, 'wb') as output_file:
        output_file.write(bytes(decrypted_data))

def decrypt_all_png_in_folder(folder_path: str, output_folder: str) -> None:
    """遍历文件夹中的所有 PNG 文件并进行解密"""
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    
    os.makedirs(output_folder, exist_ok=True)
    
    for png_file in png_files:
        input_file = os.path.join(folder_path, png_file)
        output_file = os.path.join(output_folder, f"decrypted_{png_file}")
        print(f"开始解密文件: {input_file}")
        decrypt_png(input_file, output_file)
        print(f"解密完成: {output_file}")

if __name__ == '__main__':
    input_folder = '.'  # 替换为你的输入文件夹路径
    output_folder = '.'  # 替换为你的输出文件夹路径

    decrypt_all_png_in_folder(input_folder, output_folder)
