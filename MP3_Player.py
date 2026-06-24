import os
import threading
import tkinter as tk
from tkinter import Scrollbar, Listbox, filedialog, messagebox
import ctypes


class mp_3_player():
    def __init__(self, root):
        self.root = root
        self.root.title("ghost player")
        # Увеличили ширину окна до 700, чтобы поместилась боковая панель
        self.root.geometry("700x520")
        self.root.resizable(False, False)
        self.root.configure(bg="skyblue")

        self.current_song = ""
        self.is_playing = False
        self.is_paused = False
        self.songs = []
        self.current_index = 0

        self.setup_ui()

    def mci_send(self, command):
        buffer = ctypes.create_string_buffer(255)
        ctypes.windll.winmm.mciSendStringA(command.encode('utf-8'), buffer, 255, 0)
        return buffer.value.decode('utf-8', errors='ignore')

    def setup_ui(self):
        # ---------------------------------------------------------
        # 1. БОКОВАЯ ПАНЕЛЬ (SIDEBAR)
        # ---------------------------------------------------------
        # Прижимаем к левому краю, растягиваем по вертикали (fill=tk.Y)
        self.sidebar = tk.Frame(self.root, bg="#1E293B", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)  # Запрещает панели сжиматься под размер внутренних кнопок

        # Элементы внутри боковой панели
        sidebar_title = tk.Label(self.sidebar, text="Меню / Инфо",
                                 font=("Arial", 12, "bold"), fg="white", bg="#1E293B")
        sidebar_title.pack(pady=20)

        # Пример кнопки внутри боковой панели
        tk.Button(self.sidebar, text="⚙ Настройки", bg="#334155", fg="white",
                  bd=0, font=("Arial", 10), cursor="hand2", width=18, height=2).pack(pady=10)

        # Пример текстовой метки для будущей информации
        info_label = tk.Label(self.sidebar, text="Здесь может быть\nинформация о треке\nили эквалайзер",
                              font=("Arial", 9), fg="#94A3B8", bg="#1E293B", justify=tk.CENTER)
        info_label.pack(side=tk.BOTTOM, pady=20)

        # ---------------------------------------------------------
        # 2. ГЛАВНАЯ ПАНЕЛЬ (ОСНОВНОЙ КОНТЕНТ ПЛЕЕРА)
        # ---------------------------------------------------------
        # Занимает всё оставшееся пространство справа
        main_content = tk.Frame(self.root, bg="skyblue")
        main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Заголовок плеера (теперь внутри main_content)
        title = tk.Label(main_content, text="🎵 Ghost player 🎵",
                         font=("Arial", 16, "bold"), fg="#2196F3", bg="skyblue")
        title.pack(pady=10)

        # Фрейм для списка песен (теперь внутри main_content)
        list_frame = tk.Frame(main_content, bg="skyblue")
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.song_list = Listbox(list_frame, yscrollcommand=scrollbar.set,
                                 font=("Arial", 11), selectbackground="#2196F3")
        self.song_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.song_list.yview)
        self.song_list.bind('<<ListboxSelect>>', self.on_song_select)

        # Кнопки добавления (теперь внутри main_content)
        btn_frame = tk.Frame(main_content, bg="skyblue")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📁 Добавить папку", command=self.add_folder,
                  bg="white", fg="black", bd=1, font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📄 Добавить файлы", command=self.add_files,
                  bg="white", fg="black", bd=1, font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=5)

        # Кнопки плеера (теперь внутри main_content)
        player_frame = tk.Frame(main_content, bg="skyblue")
        player_frame.pack(pady=10)

        tk.Button(player_frame, text="⏮", command=self.prev_song,
                  font=("Arial", 16), width=3, bg="skyblue", activebackground="cornflower blue", bd=0).pack(
            side=tk.LEFT, padx=5)

        self.play_btn = tk.Button(player_frame, text="▶", command=self.play_pause,
                                  font=("Arial", 20), width=3, bg="skyblue", fg="black",
                                  activebackground="cornflower blue", bd=0)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(player_frame, text="⏭", command=self.next_song,
                  font=("Arial", 16), width=3, bg="skyblue", activebackground="cornflower blue", bd=0).pack(
            side=tk.LEFT, padx=5)
        tk.Button(player_frame, text="⏹", command=self.stop_song,
                  font=("Arial", 16), width=3, bg="skyblue", fg="black", activebackground="cornflower blue", bd=0).pack(
            side=tk.LEFT, padx=5)

        # Статус бар (теперь внутри main_content)
        self.status_label = tk.Label(main_content, text="Готов к работе",
                                     font=("Arial", 12), fg="green", bg="skyblue")
        self.status_label.pack(pady=10)

    # --- Остальные методы логики остаются без изменений ---
    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for file in os.listdir(folder):
                if file.lower().endswith(('.mp3', '.wav')):
                    full_path = os.path.normpath(os.path.join(folder, file))
                    if full_path not in self.songs:
                        self.songs.append(full_path)
                        self.song_list.insert(tk.END, file)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav")])
        for file in files:
            full_path = os.path.normpath(file)
            if full_path not in self.songs:
                self.songs.append(full_path)
                self.song_list.insert(tk.END, os.path.basename(file))

    def on_song_select(self, event):
        selection = self.song_list.curselection()
        if selection:
            self.current_index = selection[0]
            self.current_song = self.songs[self.current_index]

    def play_pause(self):
        if not self.songs:
            messagebox.showwarning("Внимание", "Сначала добавьте треки!")
            return
        if not self.current_song:
            self.current_index = 0
            self.current_song = self.songs[self.current_index]
            self.song_list.selection_set(0)

        if self.is_playing:
            if self.is_paused:
                self.mci_send("resume ghost_player")
                self.is_paused = False
                self.play_btn.config(text="⏸")
                self.status_label.config(text=f"▶ {os.path.basename(self.current_song)}", fg="green")
            else:
                self.mci_send("pause ghost_player")
                self.is_paused = True
                self.play_btn.config(text="▶")
                self.status_label.config(text=f"⏸ Пауза: {os.path.basename(self.current_song)}", fg="orange")
        else:
            self.play_song()

    def play_song(self):
        try:
            self.mci_send("close ghost_player")
            song_path = f'"{self.current_song}"'
            self.mci_send(f"open {song_path} type mpegvideo alias ghost_player")
            self.mci_send("play ghost_player")
            self.is_playing = True
            self.is_paused = False
            self.play_btn.config(text="⏸")
            self.status_label.config(text=f"▶ {os.path.basename(self.current_song)}", fg="green")
            threading.Thread(target=self.check_music_end, daemon=True).start()
        except Exception as e:
            self.is_playing = False
            self.status_label.config(text=f"Ошибка: {str(e)}", fg="red")

    def check_music_end(self):
        while self.is_playing:
            status = self.mci_send("status ghost_player mode")
            if "stopped" in status and not self.is_paused:
                self.root.after(0, self.next_song)
                break
            self.root.after(200)

    def stop_song(self):
        self.mci_send("stop ghost_player")
        self.mci_send("close ghost_player")
        self.is_playing = False
        self.is_paused = False
        self.play_btn.config(text="▶")
        self.status_label.config(text="⏹ Остановлено", fg="red")

    def next_song(self):
        if not self.songs: return
        self.current_index = self.current_index + 1 if self.current_index < len(self.songs) - 1 else 0
        self.current_song = self.songs[self.current_index]
        self.update_listbox_selection()
        self.play_song()

    def prev_song(self):
        if not self.songs: return
        self.current_index = self.current_index - 1 if self.current_index > 0 else len(self.songs) - 1
        self.current_song = self.songs[self.current_index]
        self.update_listbox_selection()
        self.play_song()

    def update_listbox_selection(self):
        self.song_list.selection_clear(0, tk.END)
        self.song_list.selection_set(self.current_index)
        self.song_list.see(self.current_index)


if __name__ == "__main__":
    root = tk.Tk()
    app = mp_3_player(root)
    root.mainloop()
