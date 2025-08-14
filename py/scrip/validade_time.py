import tkinter as tk
from tkinter import messagebox
import datetime
import pandas
import csv
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_FILE = os.path.join(BASE_DIR, "produtos.csv")

def calculate_days_to_expiry(expiry_date):
    try:
        expiry_date = datetime.datetime.strptime(expiry_date, '%d/%m/%Y')
        return (expiry_date - datetime.datetime.now()).days
    except ValueError:
        return None

def carregar_produtos(DADOS_FILE):
    produtos = []
    erros = []
    if not os.path.exists(DADOS_FILE):
        raise FileNotFoundError(f"Arquivo '{DADOS_FILE}' não encontrado.")
    try:
        df = pandas.read_csv(DADOS_FILE, delimiter=';', encoding='utf-8')
        df.columns = [col.strip().lower() for col in df.columns]
        # Tenta encontrar a coluna do produto por variações
        produto_col = None
        for col in df.columns:
            if col in ["produto", "produtos", "nome", "item"]:
                produto_col = col
                break
        if not produto_col:
            produto_col = df.columns[0]  # Assume a primeira coluna se não encontrar
        validade_col = None
        for col in df.columns:
            if col in ["validade", "data", "vencimento"]:
                validade_col = col
                break
        if not validade_col:
            validade_col = df.columns[1] if len(df.columns) > 1 else None
        for idx, row in df.iterrows():
            try:
                produto = str(row.get(produto_col, "Desconhecido")).strip().title()
                validade_str = str(row.get(validade_col, "")).strip() if validade_col else ""
                days = calculate_days_to_expiry(validade_str)
                if days is None:
                    erros.append(f"❌ {produto}: data inválida ({validade_str})")
                else:
                    produtos.append((produto, days))
            except Exception as e:
                erros.append(f"Erro ao processar linha {idx+1}: {str(e)}")
    except Exception as e:
        erros.append(f"Erro ao ler arquivo: {str(e)}")
    return produtos, erros

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📦 Produtos perto do vencimento")
        self.geometry("420x320")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        self.label_atual = tk.Label(self, text="Agora:")
        self.label_atual.pack(pady=5)

        self.text_area = tk.Text(self, height=13, width=50)
        self.text_area.pack(pady=5)

        self.button_ativar = tk.Button(self, text="Ativar Monitoramento", command=self.ativar)
        self.button_ativar.pack(pady=5)

    def ativar(self):
        self.button_ativar.config(state='disabled')
        self.atualizar()

    def atualizar(self):
        self.label_atual.config(text="Agora: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            produtos, erros = carregar_produtos(DADOS_FILE=DADOS_FILE)
            texto = ""
            for produto, dias in produtos:
                if dias <= 30:
                    texto += f"⚠️{produto}: {dias} ja venceu\n"
                else: 
                    texto += f"{produto}: {dias} para vencer\n"

            if erros:
                texto += "\nErros encontrados:\n" + "\n".join(erros)

            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, texto)

        except FileNotFoundError as e:
            messagebox.showerror("Erro", str(e))

        self.after(2000, self.atualizar)

if __name__ == "__main__":
    
    app = App()
    app.mainloop()
