
import json
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox

import keyboard
import pyautogui
import pygetwindow as gw

CONFIG = "config.json"
executando = False
ENTER_DELAY = 0.20
usar_enter = None


def salvar():
    dados = {
        "janela": entrada_janela.get().strip(),
        "x": entrada_x.get().strip(),
        "y": entrada_y.get().strip(),
        "intervalo": entrada_intervalo.get().strip(),
        "usar_enter": usar_enter.get() if usar_enter is not None else False,
    }

    try:
        with open(CONFIG, "w", encoding="utf-8") as arq:
            json.dump(dados, arq, indent=2, ensure_ascii=False)

    except OSError as erro:
        messagebox.showerror("Erro", f"Não foi possível salvar a configuração:\n{erro}")


def carregar():
    if not os.path.exists(CONFIG):
        entrada_intervalo.insert(0, "0.2")
        return

    try:
        with open(CONFIG, encoding="utf-8") as arq:
            dados = json.load(arq)

        entrada_janela.delete(0, tk.END)
        entrada_janela.insert(0, dados.get("janela", ""))

        entrada_x.delete(0, tk.END)
        entrada_x.insert(0, dados.get("x", ""))

        entrada_y.delete(0, tk.END)
        entrada_y.insert(0, dados.get("y", ""))

        entrada_intervalo.delete(0, tk.END)
        entrada_intervalo.insert(0, dados.get("intervalo", "0.2"))

        if usar_enter is not None:
            usar_enter.set(dados.get("usar_enter", False))

    except (OSError, json.JSONDecodeError):
        entrada_intervalo.delete(0, tk.END)
        entrada_intervalo.insert(0, "0.2")


def manter_foco():
    entrada_janela.focus_set()


def capturar_hotkey():
    x, y = pyautogui.position()

    def atualizar():
        entrada_x.delete(0, tk.END)
        entrada_y.delete(0, tk.END)

        entrada_x.insert(0, str(x))
        entrada_y.insert(0, str(y))

        salvar()
        atualizar_status(f"Posição salva: X={x} Y={y}")

    janela.after(0, atualizar)


def _handle_enter_click():
    try:
        x = int(entrada_x.get())
        y = int(entrada_y.get())
        time.sleep(ENTER_DELAY)
        pyautogui.click(x, y)
    except Exception:
        pass


def on_enter(event):
    if not executando or (usar_enter is not None and not usar_enter.get()):
        return

    threading.Thread(target=_handle_enter_click, daemon=True).start()


def register_hotkeys():
    try:
        keyboard.on_press_key("enter", on_enter)
        keyboard.add_hotkey("F8", capturar_hotkey)
    except Exception:
        pass


def capturar():
    messagebox.showinfo(
        "Capturar posição",
        "Posicione o mouse sobre a caixa de leitura e aguarde 5 segundos."
    )

    threading.Thread(target=_capturar_posicao, daemon=True).start()


def _capturar_posicao():
    time.sleep(5)
    x, y = pyautogui.position()

    entrada_x.delete(0, tk.END)
    entrada_y.delete(0, tk.END)

    entrada_x.insert(0, str(x))
    entrada_y.insert(0, str(y))

    salvar()
    janela.after(0, manter_foco)


def validar_valores():
    if not entrada_janela.get().strip():
        messagebox.showwarning("Atenção", "Informe parte do título da janela.")
        entrada_janela.focus_set()
        return False

    try:
        int(entrada_x.get())
        int(entrada_y.get())
        intervalo = float(entrada_intervalo.get())

        if intervalo <= 0:
            raise ValueError

    except ValueError:
        messagebox.showwarning(
            "Atenção",
            "Informe valores válidos para X, Y e intervalo (maior que zero)."
        )
        entrada_intervalo.focus_set()
        return False

    return True


def atualizar_status(texto):
    status_label.config(text=f"Status: {texto}")


def loop():
    global executando

    while executando:
        try:
            titulo = entrada_janela.get().strip()
            if not titulo:
                raise ValueError("Título da janela não informado")

            janelas = gw.getWindowsWithTitle(titulo)
            if janelas and janelas[0].isActive:
                pyautogui.click(int(entrada_x.get()), int(entrada_y.get()))

        except Exception:
            pass

        time.sleep(max(0.05, float(entrada_intervalo.get())))

    janela.after(0, lambda: atualizar_status("Parado"))


def iniciar():
    global executando

    if executando:
        return

    if not validar_valores():
        return

    salvar()
    executando = True

    if usar_enter is not None and usar_enter.get():
        atualizar_status("Executando (Enter automático)")
    else:
        atualizar_status("Executando")
        threading.Thread(target=loop, daemon=True).start()


def parar():
    global executando

    if not executando:
        return

    executando = False
    atualizar_status("Parando...")


janela = tk.Tk()
janela.title("Auto Bipe Fiscal")
janela.geometry("380x300")
janela.resizable(False, False)

frame = tk.Frame(janela, padx=16, pady=16)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Nome da Janela", anchor="w").pack(fill="x")
entrada_janela = tk.Entry(frame, width=40)
entrada_janela.pack(fill="x", pady=(0, 8))

lk_frame = tk.Frame(frame)
lk_frame.pack(fill="x")

subframe = tk.Frame(lk_frame)
subframe.pack(fill="x")

label_x = tk.Label(subframe, text="X")
label_x.grid(row=0, column=0, sticky="w")
entrada_x = tk.Entry(subframe, width=15)
entrada_x.grid(row=1, column=0, sticky="w")

label_y = tk.Label(subframe, text="Y")
label_y.grid(row=0, column=1, sticky="w", padx=(10, 0))
entrada_y = tk.Entry(subframe, width=15)
entrada_y.grid(row=1, column=1, sticky="w", padx=(10, 0))

label_intervalo = tk.Label(frame, text="Intervalo (segundos)", anchor="w")
label_intervalo.pack(fill="x", pady=(12, 0))
entrada_intervalo = tk.Entry(frame, width=20)
entrada_intervalo.pack(fill="x", pady=(0, 8))

usar_enter = tk.BooleanVar()
check_enter = tk.Checkbutton(
    frame,
    text="Modo Enter automático (Enter aciona clique)",
    variable=usar_enter,
    anchor="w"
)
check_enter.pack(fill="x", pady=(0, 8))

instrucao_hotkey = tk.Label(
    frame,
    text="Pressione F8 para salvar a posição atual",
    fg="#555",
    anchor="w"
)
instrucao_hotkey.pack(fill="x", pady=(0, 8))

botao_capturar = tk.Button(
    frame,
    text="Capturar posição",
    command=capturar,
    bg="#2196F3",
    fg="white",
    activebackground="#1976D2",
    relief="flat"
)
botao_capturar.pack(fill="x", pady=(4, 6))

botao_iniciar = tk.Button(
    frame,
    text="Iniciar",
    command=iniciar,
    bg="#4CAF50",
    fg="white",
    activebackground="#388E3C",
    relief="flat"
)
botao_iniciar.pack(fill="x", pady=(0, 6))

botao_parar = tk.Button(
    frame,
    text="Parar",
    command=parar,
    bg="#F44336",
    fg="white",
    activebackground="#D32F2F",
    relief="flat"
)
botao_parar.pack(fill="x")

status_label = tk.Label(frame, text="Status: Parado", anchor="w")
status_label.pack(fill="x", pady=(12, 0))

carregar()
register_hotkeys()
manter_foco()

janela.mainloop()
