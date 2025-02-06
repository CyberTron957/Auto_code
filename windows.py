import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pyautogui
import random
import time
import pyperclip
from pynput import keyboard
from pynput.keyboard import Controller, Key, Listener
import google.generativeai as genai
import platform


os_name = platform.system()

keyboard_controller = Controller()

class CodeTypingBot:

    def __init__(self):
        self.stop_typing = False
        self.previous_clipboard_content = "" 
        self.humantype = False
        self.speed_frame = None

        self.setup_ui()
        self.setup_keyboard_listener()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Code Typing Bot")
        self.root.geometry("450x570")

        self.model_var = tk.StringVar(value="gemini-1.5-flash")
        self.lang_var = tk.StringVar(value="python")
        self.checkbox_var = tk.IntVar()
        self.speed_var = tk.DoubleVar(value=0.15)  # Add this line


        self.create_widgets()


    def quit_program(self):
        self.stop_typing = True
        messagebox.showinfo("Info", "Program is closing")
        self.root.quit()
        self.root.destroy()

        
    def create_widgets(self):
        instructions= '''1.Open portal and copy the question(ctrl+c)
        2. Wait, the code will type by itself
        3. Press '~' to stop typing.

        *Quit and restart the program if any error'''
        report='''Report bugs at: https://github.com/CyberTron957/Auto_code'''

        ttk.Label(self.root, text="Select Model:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.model_var, values=["gemini-1.5-flash", "gemini-1.5-pro"]).pack(pady=5)

        ttk.Label(self.root, text="Select Language:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.lang_var, values=["python", "java", "C","C++"]).pack(pady=5)

        self.human_type_checkbox = ttk.Checkbutton(self.root, text="Human-like Typing", variable=self.checkbox_var, command=self.toggle_human_typing)
        self.human_type_checkbox.pack(pady=10)
        
        # Create the slider widgets but don't pack them yet
        self.speed_frame = ttk.Frame(self.root)
        self.speed_label = ttk.Label(self.speed_frame, text="Typing Speed:")
        self.speed_slider = ttk.Scale(self.speed_frame, from_=0.01, to=0.25, orient='horizontal', variable=self.speed_var, length=200)
        self.speed_labels = ttk.Label(self.speed_frame, text="Fast                   Medium                   Slow")
        
        ttk.Button(self.root, text="Start", command=self.start_monitoring).pack(pady=10)
        ttk.Button(self.root, text="Stop", command=self.quit_program).pack(pady=10)
        #ttk.Button(self.root, text="Restart", command=self.restart_monitoring).pack(pady=10)
        self.title_label = tk.Label(self.root, text="Instructions:", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=5)
        self.title_label = tk.Label(self.root, text=instructions, font=("Arial", 11))
        self.title_label.pack(pady=10)
        # Replace Label with Text widget for selectable text
        self.instructions_text = tk.Text(self.root, wrap='word', height=1, width=50, font=("Arial", 8))
        self.instructions_text.insert('1.0', report)
        self.instructions_text.config(state='disabled')  # Make the text widget read-only
        self.instructions_text.pack(pady=10)

    def toggle_human_typing(self):
        if self.checkbox_var.get():
            self.speed_frame.pack(pady=5)
            self.speed_label.pack()
            self.speed_slider.pack()
            self.speed_labels.pack()
            self.humantype = True
        else:
            self.speed_frame.pack_forget()
            self.humantype = False

    def setup_keyboard_listener(self):
        listener = Listener(on_press=self.on_press)
        listener.start()

    def selectApi(self):
        api_keys = [
       "YOUR API KEYS HERE"
    ]
        return random.choice(api_keys)

    def set_humantype(self):
        self.humantype = self.checkbox_var.get() == 1

    def fast_type(self, text):
        for char in text:
            if self.stop_typing:
                return
            if char == '\n':
                keyboard_controller.press(Key.enter)
                keyboard_controller.release(Key.enter)
            else:
                keyboard_controller.press(char)
                keyboard_controller.release(char)
            time.sleep(0.01)

    def type_text_human_like(self, text):
        speed_factor = self.speed_var.get()
        base_delay = 0  # Adjust this value to your preference
        
        for char in text:
            if self.stop_typing:
                return
            pyautogui.typewrite(char, 0.01)
            delay = speed_factor
            time.sleep(random.uniform(base_delay, delay))


    def remove_indents(self, text):
        return "\n".join(line.lstrip() for line in text.splitlines())

    def monitor_clipboard_and_type(self):
        genai.configure(api_key=self.selectApi())
        model = genai.GenerativeModel(
            model_name=self.model_var.get(),
            system_instruction=f"Output ONLY {self.lang_var.get()} code without comments or indentation. Add new lines where necessary.If and only if using java:Do not make the class public  and use Scanner for taking input "
        )

        pyperclip.copy("")
        while not self.stop_typing:
            current_clipboard_content = pyperclip.paste()
            if current_clipboard_content != self.previous_clipboard_content:
                try:
                    response = model.generate_content(current_clipboard_content)
                    no_indent_text = self.remove_indents(response.text)
                    keyboard_controller.press(Key.tab)
                    keyboard_controller.release(Key.tab)
                    time.sleep(0.5)
                    if os_name == 'Darwin':  # macOS
                        modifier_key = 'command'
                    else:  
                        modifier_key = 'ctrl'
                    pyautogui.hotkey(modifier_key, 'a')  
                    time.sleep(2)
                    if self.humantype:
                        self.type_text_human_like(no_indent_text)
                    else:
                        self.fast_type(no_indent_text)

                    if os_name == 'Darwin':  # macOS
                        pyautogui.hotkey('command', 'shift', 'down')
                    else:  # Windows and Linux
                        with keyboard.pressed(Key.ctrl):
                            with keyboard.pressed(Key.shift):
                                keyboard.press(Key.end)
                                keyboard.release(Key.end)
                                
                    time.sleep(0.5)
                    pyautogui.press('backspace') 
                    
                    self.previous_clipboard_content = current_clipboard_content
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
            time.sleep(1)


    def start_monitoring(self):
        self.stop_typing = False
        monitor_thread = threading.Thread(target=self.monitor_clipboard_and_type)
        monitor_thread.daemon = True
        monitor_thread.start()
        messagebox.showinfo("Info", "You can now copy question")

    def stop_typing_text(self):
        self.stop_typing = True
        time.sleep(1)
        self.stop_typing = False


        
    def on_press(self, key):
        try:
            if key.char == '~':
                self.stop_typing_text()
        except AttributeError:
            pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    bot = CodeTypingBot()
    bot.run()
