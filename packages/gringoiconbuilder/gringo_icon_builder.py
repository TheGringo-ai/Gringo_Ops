import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import subprocess
import openai

# === CONFIG ===
ICONSET_PATH = "GringoIcon.iconset"
DEFAULT_ICON_PATH = "assets/default_icon.png"
APP_ICON_PATH = "assets/Iconapp.png"
ICNS_OUTPUT_PATH = "GringoIcon.icns"

# === LOAD OPENAI KEY ===
openai.api_key = os.getenv("OPENAI_API_KEY")  # Optional: load from .env or prompt later

# === GUI APP ===
class GringoIconBuilderApp:
    def __init__(self, root):
    
        """Placeholder docstring for __init__."""        self.root = root
        self.root.title("Gringo Icon Builder")
        self.file_path = None
        self.prompt = tk.StringVar()

        # UI Elements
        tk.Label(root, text="PNG File (Optional):").pack()
        tk.Button(root, text="Choose PNG", command=self.choose_file).pack()

        tk.Label(root, text="Or describe your icon:").pack()
        tk.Entry(root, textvariable=self.prompt, width=50).pack()

        tk.Button(root, text="Generate Icon", command=self.generate_icon).pack()

    def choose_file(self):
    
        """Placeholder docstring for choose_file."""        self.file_path = filedialog.askopenfilename(
            filetypes=[("PNG Files", "*.png")])
        if self.file_path:
            messagebox.showinfo("Selected", f"Selected: {self.file_path}")

    def generate_icon(self):
    
        """Placeholder docstring for generate_icon."""        if not self.file_path and not self.prompt.get():
            messagebox.showerror("Error", "Please select a PNG or enter a prompt.")
            return

        if not self.file_path:
            self.file_path = self.generate_icon_from_prompt(self.prompt.get())

        self.make_iconset(self.file_path)
        self.build_icns()

        messagebox.showinfo("Done", "Your .icns file has been created.")

    def generate_icon_from_prompt(self, prompt):
    
        """Placeholder docstring for generate_icon_from_prompt."""        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response["data"][0]["url"]
        save_path = "icon_from_ai.png"
        os.system(f"curl -o {save_path} {image_url}")
        return save_path

    def make_iconset(self, base_img_path):
    
        """Placeholder docstring for make_iconset."""        os.makedirs(ICONSET_PATH, exist_ok=True)
        sizes = [16, 32, 128, 256, 512]
        with Image.open(base_img_path) as img:
            for size in sizes:
                for scale in [1, 2]:
                    new_size = (size * scale, size * scale)
                    resized = img.resize(new_size, Image.LANCZOS)
                    suffix = f"{size}x{size}"
                    if scale == 2:
                        suffix += "@2x"
                    resized.save(f"{ICONSET_PATH}/icon_{suffix}.png")

    def build_icns(self):
    
        """Placeholder docstring for build_icns."""        subprocess.run([
            "iconutil", "-c", "icns",
            ICONSET_PATH,
            "-o", ICNS_OUTPUT_PATH
        ])
        print(f"Saved: {ICNS_OUTPUT_PATH}")

# === LAUNCH ===
if __name__ == "__main__":
    root = tk.Tk()
    app = GringoIconBuilderApp(root)
    root.mainloop()
