import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.current_file = None
        self.config = self.load_config()
        self.translations = self.load_translations()
        self.current_theme = self.config.get('theme', 'light')
        self.language = self.config.get('language', 'RU')

        self.setup_ui()
        self.check_first_run()

    def load_config(self):
        config_path = 'fm_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        # Изначальные настройки
        return {'first_run': True, 'language': 'RU', 'theme': 'light', 'language_changed': False}

    def save_config(self):
        with open('fm_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def load_translations(self):
        return {
            'EN': {
                'title': 'File Manager',
                'file': 'File',
                'new': 'New',
                'open': 'Open',
                'save': 'Save',
                'rename': 'Rename',
                'delete': 'Delete',
                'exit': 'Exit',
                'theme': '🌓 Theme',
                'language': '🌐 Language',
                'tutorial_title': 'Tutorial',
                'tutorial_text': (
                    "1. New file: Ctrl+N\n"
                    "2. Open file: Ctrl+O\n"
                    "3. Save file: Ctrl+S\n"
                    "4. Toggle theme: Theme button\n"
                    "5. Change language: Language button"
                ),
                'good_luck': 'Good luck!'
            },
            'RU': {
                'title': 'Файловый менеджер',
                'file': 'Файл',
                'new': 'Новый',
                'open': 'Открыть',
                'save': 'Сохранить',
                'rename': 'Переименовать',
                'delete': 'Удалить',
                'exit': 'Выход',
                'theme': '🌓 Тема',
                'language': '🌐 Язык',
                'tutorial_title': 'Обучение',
                'tutorial_text': (
                    "1. Новый файл: Ctrl+N\n"
                    "2. Открыть файл: Ctrl+O\n"
                    "3. Сохранить файл: Ctrl+S\n"
                    "4. Переключение темы: кнопка Тема\n"
                    "5. Смена языка: кнопка Язык"
                ),
                'good_luck': 'Удачной работы!'
            }
        }

    def setup_ui(self):
        self.root.title(self.translations[self.language]['title'])
        self.root.geometry('800x600')

        # Меню
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(
            menu=self.file_menu,
            label=self.translations[self.language]['file']
        )
        self.file_menu.add_command(
            label=self.translations[self.language]['new'],
            command=self.new_file,
            accelerator='Ctrl+N'
        )
        self.file_menu.add_command(
            label=self.translations[self.language]['open'],
            command=self.open_file,
            accelerator='Ctrl+O'
        )
        self.file_menu.add_command(
            label=self.translations[self.language]['save'],
            command=self.save_file,
            accelerator='Ctrl+S'
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label=self.translations[self.language]['exit'],
            command=self.root.quit
        )
        self.root.config(menu=self.menu_bar)

        # Горячие клавиши
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())

        # Панель инструментов
        self.toolbar = ttk.Frame(self.root)
        self.theme_btn = ttk.Button(
            self.toolbar,
            text=self.translations[self.language]['theme'],
            command=self.toggle_theme
        )
        self.lang_btn = ttk.Button(
            self.toolbar,
            text=self.translations[self.language]['language'],
            command=self.toggle_language
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.lang_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Текстовое поле с прокруткой
        self.text_area = tk.Text(self.root, wrap=tk.WORD)
        self.scrollbar = ttk.Scrollbar(self.root, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(expand=True, fill=tk.BOTH)

        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == 'dark':
            bg = '#2d2d2d'
            fg = 'white'
            insertbackground = 'white'  # курсор
        else:
            bg = 'white'
            fg = 'black'
            insertbackground = 'black'
        self.text_area.config(bg=bg, fg=fg, insertbackground=insertbackground)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', background=bg, foreground=fg)
        style.configure('TFrame', background=bg)
        self.toolbar.config(style='TFrame')

    def check_first_run(self):
        # Если сменили язык - не показываем сообщение
        if self.config.get('language_changed', False):
            self.config['language_changed'] = False
            self.save_config()
            return

        if self.config.get('first_run', True):
            messagebox.showinfo(
                self.translations[self.language]['tutorial_title'],
                self.translations[self.language]['tutorial_text']
            )
            self.config['first_run'] = False
            self.save_config()
        else:
            messagebox.showinfo(
                self.translations[self.language]['title'],
                self.translations[self.language]['good_luck']
            )

    def new_file(self):
        if self.confirm_discard_changes():
            self.text_area.delete(1.0, tk.END)
            self.current_file = None
            self.root.title(self.translations[self.language]['title'])

    def open_file(self):
        if not self.confirm_discard_changes():
            return
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_file = file_path
                self.root.title(f"{os.path.basename(file_path)} - {self.translations[self.language]['title']}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file:\n{e}")

    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo(self.translations[self.language]['title'], "File saved.")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = file_path
                self.root.title(f"{os.path.basename(file_path)} - {self.translations[self.language]['title']}")
                messagebox.showinfo(self.translations[self.language]['title'], "File saved.")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file:\n{e}")

    def confirm_discard_changes(self):
        # Можно расширить, чтобы проверять изменения, сейчас просто вопрос
        return messagebox.askyesno(
            self.translations[self.language]['title'],
            "Discard current changes?" if self.language == 'EN' else "Отменить текущие изменения?"
        )

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.config['theme'] = self.current_theme
        self.save_config()
        self.apply_theme()

    def toggle_language(self):
        self.language = 'EN' if self.language == 'RU' else 'RU'
        self.config['language'] = self.language
        self.config['language_changed'] = True
        self.save_config()
        # Перезапускаем приложение, чтобы обновить интерфейс
        self.root.destroy()
        root = tk.Tk()
        FileManagerApp(root)
        root.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()
