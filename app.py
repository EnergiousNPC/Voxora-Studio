
import tkinter as tk
import threading
import time
import pygame
import shutil
import soundfile as sf
import numpy as np
import sys
import ctypes

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "VoxoraStudio.Desktop"
    )
import customtkinter as ctk
from pathlib import Path
from supertonic import TTS
from tkinter import filedialog, messagebox
from tkinter import ttk

# Main application window
tts = None
last_audio_path = None

# Audio player initialization
pygame.mixer.init()

# Audio player state
playback_paused = False
playback_position = 0.0
audio_duration = 0.0
is_updating_progress = False

# Application directories
APP_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)

RESOURCE_DIR = Path(
    getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
)

MODEL_DIR = APP_DIR / "models" / "supertonic-3"
AUDIO_DIR = APP_DIR / "audio"
TEMP_DIR = APP_DIR / "temp"

AUDIO_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

def load_tts():
    global tts

    if tts is None:
        tts = TTS(
            model="supertonic-3",
            model_dir=str(MODEL_DIR),
            auto_download=False
        )

    return tts

# Voxora Studio - Midnight Blue Theme
BG = "#0B1220"
PANEL = "#111C2E"
INPUT_BG = "#1E2D43"

TEXT = "#F1F5F9"
MUTED = "#94A3B8"

ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"

SUCCESS = "#16A085"
DANGER = "#E05260"
SECONDARY = "#334155"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Voxora Studio")
root.iconbitmap(str(APP_DIR / "VoxoraStudio.ico"))
print("Voxora icon loaded:", APP_DIR / "VoxoraStudio.ico")
root.geometry("1000x850")
root.minsize(800, 600)
root.configure(fg_color=BG)

def handle_minimize(event):
    if root.state() == "iconic":
        if hasattr(root, "_dropdown_popup"):
            root._dropdown_popup.withdraw()

root.bind("<Unmap>", handle_minimize, add="+")

# Modern dropdown styling
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TCombobox",
    fieldbackground=INPUT_BG,
    background=SECONDARY,
    foreground=TEXT,
    arrowcolor=TEXT,
    bordercolor=INPUT_BG,
    lightcolor=INPUT_BG,
    darkcolor=INPUT_BG,
    padding=8,
    font=("Segoe UI", 10)
)

style.map(
    "TCombobox",
    fieldbackground=[("readonly", INPUT_BG)],
    foreground=[("readonly", TEXT)],
    background=[("readonly", SECONDARY)]
)



# Application Header
header = ctk.CTkFrame(
    root,
    fg_color="transparent",
    corner_radius=0
)
header.pack(fill="x", padx=35, pady=(25, 20))

# App title
ctk.CTkLabel(
    header,
    text="VOXORA STUDIO",
    font=("Segoe UI", 30, "bold"),
    text_color=TEXT
).pack(anchor="w")

# Subtitle
ctk.CTkLabel(
    header,
    text="AI Voice Generation Studio  •  Powered by Supertonic 3",
    font=("Segoe UI", 12),
    text_color=MUTED
).pack(anchor="w", pady=(3, 0))

# Header accent line
ctk.CTkFrame(
    root,
    height=2,
    fg_color=ACCENT,
    corner_radius=2
).pack(fill="x", padx=35, pady=(0, 18))

# Main content panel
main = ctk.CTkFrame(
    root,
    fg_color=PANEL,
    corner_radius=18,
    border_width=1,
    border_color="#26364D"
)
main.pack(fill="both", expand=True, padx=35, pady=(0, 25))

ctk.CTkLabel(
    main,
    text="Your Narration",
    font=("Segoe UI", 18, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=25, pady=(25, 12))

# Script editor
PLACEHOLDER = "Enter your movie or series explanation script here..."

script_box = ctk.CTkTextbox(
    main,
    height=160,
    font=("Segoe UI", 14),
    fg_color=INPUT_BG,
    text_color=MUTED,
    border_width=1,
    border_color="#3B82F6",
    corner_radius=14,
    wrap="word"
)

script_box.pack(fill="both", expand=False, padx=20, pady=(0, 18))

script_box.insert("1.0", PLACEHOLDER)

def on_script_focus_in(event):
    if script_box.get("1.0", "end-1c") == PLACEHOLDER:
        script_box.delete("1.0", "end")
        script_box.configure(text_color=TEXT)

def on_script_focus_out(event):
    if not script_box.get("1.0", "end-1c").strip():
        script_box.delete("1.0", "end")
        script_box.insert("1.0", PLACEHOLDER)
        script_box.configure(text_color=MUTED)

script_box.bind("<FocusIn>", on_script_focus_in)
script_box.bind("<FocusOut>", on_script_focus_out)

# Footer

# Voice and generation settings
settings = ctk.CTkFrame(
    main,
    fg_color="#152238",
    corner_radius=18,
    border_width=1,
    border_color="#334766"
)

settings.pack(fill="x", padx=25, pady=18, ipady=8)
settings.grid_columnconfigure(0, minsize=175)
settings.grid_columnconfigure(1, minsize=175)
settings.grid_columnconfigure(2, minsize=250)
settings.grid_columnconfigure(3, minsize=130)

def create_custom_dropdown(parent, variable, values, width=160):
    root_window = parent.winfo_toplevel()

    button = ctk.CTkFrame(
        parent,
        width=width,
        height=40,
        corner_radius=10,
        fg_color=INPUT_BG,
        border_width=1,
        border_color="#334766"
    )
    button.pack_propagate(False)

    value_label = ctk.CTkLabel(
        button,
        text=variable.get(),
        font=("Segoe UI", 12),
        text_color=TEXT,
        anchor="w"
    )
    value_label.pack(side="left", fill="both", expand=True, padx=(12, 0))

    arrow_label = ctk.CTkLabel(
        button,
        text="▼",
        width=32,
        font=("Segoe UI", 11),
        text_color=MUTED
    )
    arrow_label.pack(side="right", padx=(0, 5))

    def on_hover(event):
        button.configure(fg_color=SECONDARY)

    def on_leave(event):
        button.configure(fg_color=INPUT_BG)

    for widget in (button, value_label, arrow_label):
        widget.bind("<Enter>", on_hover)
        widget.bind("<Leave>", on_leave)

    popup = ctk.CTkToplevel(root_window)
    root_window._dropdown_popup = popup
    popup.withdraw()
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(fg_color=PANEL)

    menu_frame = ctk.CTkFrame(
        popup,
        fg_color=PANEL,
        corner_radius=12,
        border_width=1,
        border_color="#334766"
    )
    menu_frame.pack(fill="both", expand=True, padx=1, pady=1)

    def close_menu():
        popup.withdraw()


    def close_on_outside_click(event):
        if not popup.winfo_viewable():
            return

    # Keep the menu open when clicking inside the popup
        if event.widget.winfo_toplevel() == popup:
            return

    # Keep the menu open when clicking anywhere on its dropdown button
        x1 = button.winfo_rootx()
        y1 = button.winfo_rooty()
        x2 = x1 + button.winfo_width()
        y2 = y1 + button.winfo_height()

        if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
             return

        close_menu()


    root_window.bind_all(
        "<Button-1>",
        close_on_outside_click,
        add="+"
    )

    def select_option(value):
        variable.set(value)
        value_label.configure(text=value)
        close_menu()

    for value in values:
        option = ctk.CTkButton(
            menu_frame,
            text=value,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color=ACCENT,
            text_color=TEXT,
            font=("Segoe UI", 12),
            anchor="w",
            command=lambda v=value: select_option(v)
        )
        option.pack(fill="x", padx=5, pady=3)

    def toggle_menu():
        if popup.winfo_viewable():
           close_menu()
           return

        if root_window.state() == "iconic":
           return

        popup.update_idletasks()

        menu_height = len(values) * 40 + 12
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()

        if y + menu_height > popup.winfo_screenheight() - 10:
            y = button.winfo_rooty() - menu_height

        popup.geometry(
            f"{width}x{menu_height}+{x}+{y}"
        )

        popup.deiconify()
        popup.lift()
        popup.focus_force()

    button.bind("<Button-1>", lambda event: toggle_menu())
    value_label.bind("<Button-1>", lambda event: toggle_menu())
    arrow_label.bind("<Button-1>", lambda event: toggle_menu())

    popup.bind("<Escape>", lambda event: close_menu())

    return button

# Language selection
ctk.CTkLabel(
    settings,
    text="LANGUAGE",
    font=("Segoe UI", 11, "bold"),
    text_color=MUTED
).grid(row=0, column=0, sticky="w", padx=(18, 10), pady=(15, 8))

language_var = tk.StringVar(value="English")

language_box = create_custom_dropdown(
    settings,
    language_var,
    ["English", "Hindi"],
    width=160
)

language_box.grid(
    row=1,
    column=0,
    sticky="w",
    padx=(18, 10),
    pady=(0, 18)
)

voice_names = {
    "Sophia": "F1",
    "Emma": "F2",
    "Olivia": "F3",
    "Isabella": "F4",
    "Amelia": "F5",
    "Alex": "M1",
    "Daniel": "M2",
    "James": "M3",
    "Ethan": "M4",
    "Noah": "M5"
}

# Voice selection
ctk.CTkLabel(
    settings,
    text="VOICE",
    font=("Segoe UI", 11, "bold"),
    text_color=MUTED
).grid(row=0, column=1, sticky="w", padx=(18, 10), pady=(15, 8))

voice_var = tk.StringVar(value="Alex")
voice_box = create_custom_dropdown(
    settings,
    voice_var,
    list(voice_names.keys()),
    width=160
)

voice_box.grid(row=1, column=1, sticky="w", padx=(18, 10), pady=(0, 18))

# Speed control
ctk.CTkLabel(
    settings,
    text="SPEECH SPEED",
    font=("Segoe UI", 11, "bold"),
    text_color=MUTED
).grid(row=0, column=2, sticky="w", padx=(18, 10), pady=(15, 8))

# Speed control
# Speed control
speed_var = tk.DoubleVar(value=1.0)

speed_frame = ctk.CTkFrame(
    settings,
    fg_color="transparent",
    width=245,
    height=45
)

speed_frame.grid(
    row=1,
    column=2,
    sticky="w",
    padx=(18, 5),
    pady=(0, 18)
)

speed_frame.grid_propagate(False)

speed_value_label = ctk.CTkLabel(
    speed_frame,
    text="1.00×",
    font=("Segoe UI", 13, "bold"),
    text_color=TEXT,
    width=60
)

speed_value_label.pack(side="right", padx=(5, 0))

speed_scale = ctk.CTkSlider(
    speed_frame,
    from_=0.7,
    to=1.3,
    number_of_steps=12,
    variable=speed_var,
    width=160,
    height=22,
    progress_color=ACCENT,
    button_color=ACCENT,
    button_hover_color=ACCENT_HOVER
)

speed_scale.pack(side="left")

# Update the displayed speed whenever the value changes
def update_speed(*args):
    speed_value_label.configure(
        text=f"{speed_var.get():.2f}×"
    )

speed_var.trace_add("write", update_speed)

# Quality steps
ctk.CTkLabel(
    settings,
    text="QUALITY",
    font=("Segoe UI", 11, "bold"),
    text_color=MUTED
).grid(row=0, column=3, sticky="w", padx=(18, 10), pady=(15, 8))

steps_var = tk.StringVar(value="8")
steps_box = create_custom_dropdown(
    settings,
    steps_var,
    ["4", "8", "12"],
    width=110
)

steps_box.grid(
    row=1,
    column=3,
    sticky="w",
    padx=(18, 10),
    pady=(0, 18)
)


# Generation status
status_var = tk.StringVar(value="Ready to generate")

status_label = ctk.CTkLabel(
    main,
    textvariable=status_var,
    text_color=MUTED,
    font=("Segoe UI", 11),
    anchor="w"
)

status_label.pack(
    anchor="w",
    padx=20,
    pady=(10, 5)
)

# Audio playback functions
def play_audio():
    global playback_paused, playback_position, audio_duration

    if not last_audio_path:
        messagebox.showwarning(
            "No Audio",
            "Please generate audio first."
        )
        return

    try:
        if playback_paused:
            pygame.mixer.music.unpause()
            playback_paused = False

        else:
            pygame.mixer.music.load(last_audio_path)
            pygame.mixer.music.play()
            playback_position = 0.0
            audio_duration = get_audio_duration(last_audio_path)

        status_var.set("Playing audio...")

    except Exception as e:
        messagebox.showerror("Playback Error", str(e))


def pause_audio():
    global playback_paused

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        playback_paused = True
        status_var.set("Playback paused.")


def toggle_playback():
    if playback_paused:
        play_audio()
        play_button.configure(text="Ⅱ  Pause")
    elif pygame.mixer.music.get_busy():
        pause_audio()
        play_button.configure(text="▶  Play")
    else:
        play_audio()
        play_button.configure(text="Ⅱ  Pause")

def seek_audio(value):
    global playback_position

    if not last_audio_path or audio_duration <= 0:
        return

    if is_updating_progress:
        return

    if not pygame.mixer.music.get_busy():
        return

    try:
        new_position = float(value) * audio_duration

        pygame.mixer.music.set_pos(new_position)
        playback_position = new_position

    except Exception as e:
        print("Seeking error:", e)


def stop_audio():
    global playback_paused, playback_position

    pygame.mixer.music.stop()
    playback_paused = False
    playback_position = 0.0
    status_var.set("Playback stopped.")

def set_audio_path(path):
    global last_audio_path, audio_duration
    global playback_position, playback_paused

    last_audio_path = path
    audio_duration = get_audio_duration(path)

    playback_position = 0.0
    playback_paused = False

    elapsed_label.configure(text="00:00")
    duration_label.configure(text=format_time(audio_duration))
    progress_var.set(0.0)
    play_button.configure(text="▶  Play")

    player_frame.pack(
    fill="x",
    padx=20,
    pady=(10, 10),
    before=footer_label
)

def get_audio_duration(path):
    return sf.info(path).duration
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def update_playback_progress():
    global playback_position, is_updating_progress, playback_paused

    if pygame.mixer.music.get_busy() and not playback_paused:
        position = pygame.mixer.music.get_pos() / 1000

        if position >= 0:
            playback_position = min(position, audio_duration)

            elapsed_label.configure(
                text=format_time(playback_position)
            )

            duration_label.configure(
                text=format_time(audio_duration)
            )

            if audio_duration > 0:
                is_updating_progress = True
                progress_var.set(playback_position / audio_duration)
                is_updating_progress = False

    elif not playback_paused and playback_position > 0:
        playback_position = 0.0
        play_button.configure(text="▶  Play")
        elapsed_label.configure(text="00:00")
        progress_var.set(0.0)
        status_var.set("Playback finished.")

    root.after(100, update_playback_progress)

def save_audio():
    if not last_audio_path:
        messagebox.showwarning(
            "No Preview",
            "Please generate audio first."
        )
        return

    save_path = filedialog.asksaveasfilename(
        parent=root,
        title="Save Approved Audio",
        initialdir=str(AUDIO_DIR),
        initialfile="narration.wav",
        defaultextension=".wav",
        filetypes=[("WAV Audio", "*.wav")]
    )

    if not save_path:
        return

    try:
        pygame.mixer.music.stop()
        shutil.copy2(last_audio_path, save_path)
        status_var.set("Audio saved successfully!")

    except Exception as e:
        messagebox.showerror("Save Error", str(e))
# Generate button
def generate_audio():
    global last_audio_path

    text = script_box.get("1.0", "end-1c").strip()
    

    if not text or text == PLACEHOLDER:
        messagebox.showwarning("Missing Script", "Please enter your narration first.")
        return

    # Read UI settings on the main thread
    language = "en" if language_var.get() == "English" else "hi"
    voice = voice_names[voice_var.get()]
    speed = speed_var.get()
    steps = int(steps_var.get())

    output_path = str(TEMP_DIR / f"preview_{threading.get_ident()}_{int(time.time() * 1000)}.wav")

    # Ask where to save before starting the worker
    

    generate_button.configure(state="disabled")
    status_var.set("Generating audio... Please wait.")

    def worker():
        try:
            engine = load_tts()

            wav, duration = engine.synthesize(
                text,
                voice_style=engine.get_voice_style(voice),
                total_steps=steps,
                speed=speed,
                max_chunk_length=250,
                silence_duration=0.4,
                lang=language
            )

            wav = np.squeeze(wav)
            sf.write(output_path, wav, engine.sample_rate)

            root.after(0, lambda: set_audio_path(output_path))

            audio_duration = sf.info(output_path).duration

            root.after(0, lambda: status_var.set(
            f"Audio saved! Duration: {audio_duration:.1f} seconds"
            ))

        except Exception as e:
            root.after(0, lambda err=str(e): messagebox.showerror(
                "Generation Error", err
            ))
            root.after(0, lambda: status_var.set("Generation failed."))

        finally:
            root.after(0, lambda: generate_button.configure(state="normal"))

    threading.Thread(target=worker, daemon=True).start()
    
generate_button = ctk.CTkButton(
    main,
    text="Generate Audio",
    command=generate_audio,
    font=("Segoe UI", 13, "bold"),
    width=200,
    height=44,
    corner_radius=10,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="white"
)

generate_button.pack(
    anchor="w",
    padx=20,
    pady=(5, 10)
)


# Audio Player Panel
player_frame = ctk.CTkFrame(
    main,
    fg_color=PANEL,
    corner_radius=12
)

player_frame.pack(
    fill="x",
    padx=20,
    pady=(10, 10)
)

player_title = ctk.CTkLabel(
    player_frame,
    text="AUDIO PLAYER",
    font=("Segoe UI", 11, "bold"),
    text_color=MUTED
)

player_title.pack(
    anchor="w",
    padx=18,
    pady=(14, 8)
)

# Playback progress
progress_var = tk.DoubleVar(value=0.0)

progress_slider = ctk.CTkSlider(
    player_frame,
    from_=0,
    to=1,
    variable=progress_var,
    command=seek_audio,
    progress_color=ACCENT,
    button_color=ACCENT,
    button_hover_color=ACCENT_HOVER,
    height=16
)

progress_slider.pack(
    fill="x",
    padx=18,
    pady=(5, 5)
)

# Playback time labels
time_frame = ctk.CTkFrame(
    player_frame,
    fg_color="transparent"
)

time_frame.pack(
    fill="x",
    padx=18,
    pady=(0, 12)
)

elapsed_label = ctk.CTkLabel(
    time_frame,
    text="00:00",
    font=("Segoe UI", 11),
    text_color=TEXT
)

elapsed_label.pack(side="left")

duration_label = ctk.CTkLabel(
    time_frame,
    text="00:00",
    font=("Segoe UI", 11),
    text_color=MUTED
)

duration_label.pack(side="right")

# Player controls
controls_frame = ctk.CTkFrame(
    player_frame,
    fg_color="transparent"
)

controls_frame.pack(
    fill="x",
    padx=18,
    pady=(0, 10),
    before=progress_slider
)

# Play/Pause button
play_button = ctk.CTkButton(
    controls_frame,
    text="▶  Play",
    command=toggle_playback,
    width=120,
    height=38,
    corner_radius=8,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    font=("Segoe UI", 12, "bold")
)

play_button.pack(side="left")

# Save audio button
save_button = ctk.CTkButton(
    controls_frame,
    text="↓  Save Audio",
    command=save_audio,
    width=120,
    height=38,
    corner_radius=8,
    fg_color=SECONDARY,
    hover_color="#475569",
    font=("Segoe UI", 12, "bold")
)

save_button.pack(side="right")
player_frame.pack_forget()

# Footer
# Footer
footer_label = tk.Label(
    main,
    text="LOCAL ENGINE  •  NO API REQUIRED",
    font=("Segoe UI", 9, "bold"),
    bg=PANEL,
    fg=ACCENT
)

footer_label.pack(
    anchor="w",
    padx=20,
    pady=(10, 20)
)
# Clean up temporary audio when closing
def on_closing():
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()

        for file in TEMP_DIR.glob("preview_*.wav"):
            try:
                file.unlink()
            except OSError:
                pass

    except Exception as e:
        print("Cleanup error:", e)

    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

# Start application
root.after(100, update_playback_progress)
root.mainloop()