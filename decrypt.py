import os
from PIL import Image
import numpy as np
from multiprocessing import Pool, Manager
from io import BytesIO

def is_valid_png(data):
    """使用 Pillow 判断文件是否是有效的 PNG 文件"""
    try:
        img = Image.open(BytesIO(data))
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False

def try_decrypt(encrypted_data, candidate_index):
    """尝试用给定的候选位置解密"""
    encrypted_data = np.array(list(encrypted_data), dtype=np.uint8)
    encrypted_data[1], encrypted_data[2] = encrypted_data[2], encrypted_data[1]
    decrypted_data = np.delete(encrypted_data, candidate_index)

    return bytes(decrypted_data)

def brute_force_single_decrypt(args):
    """每个进程解密单个候选位置"""
    encrypted_data, candidate_index, result = args

    decrypted_data = try_decrypt(encrypted_data, candidate_index)
    
    if is_valid_png(decrypted_data):
        result.put(decrypted_data)
        return candidate_index

    return None

def brute_force_decrypt_png(input_file_path, output_file_path):
    """穷举解密 PNG 文件"""
    with open(input_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    ones_indices = [i for i, byte in enumerate(encrypted_data) if byte == 1]
    print(f"找到 {len(ones_indices)} 个候选的 `1` 字节位置，开始尝试解密...")

    with Manager() as manager:
        result = manager.Queue()

        with Pool(processes=os.cpu_count()) as pool:
            results = pool.map(brute_force_single_decrypt, [(encrypted_data, index, result) for index in ones_indices])

        while not result.empty():
            decrypted_data = result.get()
            with open(output_file_path, 'wb') as output_file:
                output_file.write(decrypted_data)
            print(f"解密成功，文件已保存至 {output_file_path}")
            return

    print("未能成功解密 PNG 文件，请检查文件或加密算法。")

def decrypt_all_png_in_folder(folder_path, output_folder):
    """遍历文件夹中的所有 PNG 文件并进行解密"""
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    
    os.makedirs(output_folder, exist_ok=True)
    
    for png_file in png_files:
        input_file = os.path.join(folder_path, png_file)
        output_file = os.path.join(output_folder, f"decrypted_{png_file}")
        print(f"开始解密文件: {input_file}")
        brute_force_decrypt_png(input_file, output_file)
        print(f"解密完成: {output_file}")

if __name__ == '__main__':
    input_folder = '.'  # 替换为你的输入文件夹路径
    output_folder = '.'  # 替换为你的输出文件夹路径

    decrypt_all_png_in_folder(input_folder, output_folder)
