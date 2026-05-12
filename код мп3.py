from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, Listbox, Scrollbar, messagebox
from playsound import playsound
import os
import threading

class mp_3_player():
    def __init__(self, root):
        self.root = root
        self.root.title("ghost player")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.root.configure(bg="skyblue")
        self.root.resizable(False, False)

        self.current_song = ""
        self.is_playing = False
        self.songs = []
        self.current_index = 0

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="🎵 Музыкальный плеер",
                         font=("Arial", 16, "bold"), fg="#2196F3")
        title.pack(pady=10)

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.song_list = Listbox(list_frame, yscrollcommand=scrollbar.set,
                                 font=("Arial", 11), selectbackground="#2196F3")
        self.song_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.song_list.yview)
        self.song_list.bind('<<ListboxSelect>>', self.on_song_select)

        # Кнопки управления
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="📁 Добавить папку", command=self.add_folder,
                  bg="skyblue", fg="black", bd =0, font=("Arial", 11), width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📁 Добавить файлы", command=self.add_files,
                  bg="skyblue", fg="black", bd =0, font=("Arial", 11), width=14).pack(side=tk.LEFT, padx=5)

        player_frame = tk.Frame(self.root)
        player_frame.pack(pady=10)

        tk.Button(player_frame, text="⏮", command=self.prev_song,
                  font=("Arial", 16), width=3, height=2, bg="skyblue",activeforeground= "cornflower blue", bd= 1).pack(side=tk.LEFT, padx=5)
        tk.Button(player_frame, text="▶", command=self.play_pause,
                  font=("Arial", 20), width=3, height=2, bg="skyblue", fg="black",activeforeground= "cornflower blue", bd= 0).pack(side=tk.LEFT, padx=5)
        tk.Button(player_frame, text="⏭", command=self.next_song,
                  font=("Arial", 16), width=3, height=2, bg="skyblue",activeforeground= "cornflower blue", bd= 1).pack(side=tk.LEFT, padx=5)
        tk.Button(player_frame, text="⏹", command=self.stop_song,
                  font=("Arial", 16), width=3, height=2, bg="skyblue", fg="black",activeforeground= "cornflower blue", bd= 0).pack(side=tk.LEFT, padx=5)



        self.status_label = tk.Label(self.root, text="Готов к работе",
                                     font=("Arial", 12), fg="green")
        self.status_label.pack(pady=10)


    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for file in os.listdir(folder):
                if file.lower().endswith(('.mp3', '.wav')):
                    self.songs.append(os.path.join(folder, file))
                    self.song_list.insert(tk.END, os.path.basename(file))

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav")])
        for file in files:
            self.songs.append(file)
            self.song_list.insert(tk.END, os.path.basename(file))

    def on_song_select(self, event):
        selection = self.song_list.curselection()
        if selection:
            self.current_index = selection[0]
            self.current_song = self.songs[self.current_index]

    def play_pause(self):
        if not self.current_song:
            self.next_song()
            return

        if self.is_playing:
            # Останавливаем в отдельном потоке
            threading.Thread(target=self.stop_song, daemon=True).start()
        else:
            threading.Thread(target=self.play_song, daemon=True).start()


    def play_pause(self):
        if not self.current_song:
            self.next_song()
            return

        if self.is_playing:
            # Останавливаем в отдельном потоке
            threading.Thread(target=self.stop_song, daemon=True).start()
        else:
            threading.Thread(target=self.play_song, daemon=True).start()

    def play_song(self):
        try:
            self.is_playing = True
            self.status_label.config(text=f"▶ {os.path.basename(self.current_song)}")
            self.root.after(0, lambda: self.status_label.config(fg="green"))
            playsound(self.current_song, block=False)
            self.is_playing = False
            self.root.after(0, lambda: self.status_label.config(text="Завершено", fg="orange"))
        except Exception as e:
            self.is_playing = False
            self.root.after(0, lambda: self.status_label.config(text=f"Ошибка: {str(e)}", fg="red"))

    def stop_song(self):
        self.is_playing = False
        self.status_label.config(text="⏹ Остановлено", fg="red")

    def next_song(self):
        if self.current_index < len(self.songs) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.current_song = self.songs[self.current_index]
        self.song_list.selection_clear(0, tk.END)
        self.song_list.selection_set(self.current_index)
        self.play_pause()

    def prev_song(self):
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.songs) - 1
        self.current_song = self.songs[self.current_index]
        self.song_list.selection_clear(0, tk.END)
        self.song_list.selection_set(self.current_index)
        self.play_pause()



if __name__ == "__main__":
    root = tk.Tk()
    app = mp_3_player(root)
    root.mainloop()




