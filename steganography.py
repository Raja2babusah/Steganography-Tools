import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import argparse

def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return ''.join([format(i, "08b") for i in data])
    elif isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode(image_name, secret_data, n_bits=2):
    image = cv2.imread(image_name)
    n_bytes = image.shape[0] * image.shape[1] * 3 * n_bits // 8
    if len(secret_data) > n_bytes:
        raise ValueError("Insufficient bytes, need a bigger image or less data.")
    
    secret_data += "====="
    binary_secret_data = to_bin(secret_data)
    data_index = 0
    data_len = len(binary_secret_data)
    
    for bit in range(1, n_bits + 1):
        for row in image:
            for pixel in row:
                r, g, b = to_bin(pixel)
                if data_index < data_len:
                    pixel[0] = int(r[:-bit] + binary_secret_data[data_index], 2)
                    data_index += 1
                if data_index < data_len:
                    pixel[1] = int(g[:-bit] + binary_secret_data[data_index], 2)
                    data_index += 1
                if data_index < data_len:
                    pixel[2] = int(b[:-bit] + binary_secret_data[data_index], 2)
                    data_index += 1
                if data_index >= data_len:
                    break
    return image

def decode(image_name, n_bits=1):
    image = cv2.imread(image_name)
    binary_data = ""
    
    for bit in range(1, n_bits + 1):
        for row in image:
            for pixel in row:
                r, g, b = to_bin(pixel)
                binary_data += r[-bit] + g[-bit] + b[-bit]
    
    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = "".join([chr(int(byte, 2)) for byte in all_bytes])
    decoded_data = decoded_data.split("=====")[0]
    return decoded_data

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.bmp;*.jpg")])
    return file_path

def encode_message():
    image_path = select_image()
    if not image_path:
        return
    secret_message = text_entry.get()
    if not secret_message:
        messagebox.showerror("Error", "Please enter a message to encode")
        return
    
    try:
        encoded_image = encode(image_path, secret_message)
        output_path = image_path.split(".")[0] + "encoded.png"
        cv2.imwrite(output_path, encoded_image)
        messagebox.showinfo("Success", f"Encoded image saved as {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def decode_message():
    image_path = select_image()
    if not image_path:
        return
    
    try:
        decoded_text = decode(image_path)
        messagebox.showinfo("Decoded Message", decoded_text)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_gui():
    root = tk.Tk()
    root.title("Image Steganography")
    root.geometry("400x300")

    label = tk.Label(root, text="Enter text to encode:")
    label.pack(pady=5)

    global text_entry
    text_entry = tk.Entry(root, width=50)
    text_entry.pack(pady=5)

    encode_button = tk.Button(root, text="Encode Message", command=encode_message)
    encode_button.pack(pady=10)

    decode_button = tk.Button(root, text="Decode Message", command=decode_message)
    decode_button.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Steganography encoder/decoder")
    parser.add_argument("-e", "--encode", help="Encode the given text into an image")
    parser.add_argument("-d", "--decode", help="Decode a hidden message from an image")
    parser.add_argument("-b", "--n-bits", help="Number of least significant bits to use", type=int, default=2)
    parser.add_argument("-g", "--gui", help="Launch the GUI", action="store_true")
    args = parser.parse_args()

    if args.gui:
        run_gui()
    elif args.encode:
        text = input("Enter the message to encode: ")
        encoded_image = encode(args.encode, text, args.n_bits)
        output_path = args.encode.split(".")[0] + "_encoded.png"
        cv2.imwrite(output_path, encoded_image)
        print(f"Encoded image saved as {output_path}")
    elif args.decode:
        message = decode(args.decode, args.n_bits)
        print(f"Decoded message: {message}")
    else:
        parser.print_help()