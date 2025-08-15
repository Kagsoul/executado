import tkinter as tk
from tkinter import messagebox
import datetime
import pandas
import csv
import os
import sys
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
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
        produto_col = None
        for col in df.columns:
            if col in ["produto", "produtos", "nome", "item"]:
                produto_col = col
                break
        if not produto_col:
            produto_col = df.columns[0] 
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
        self.geometry("530x400")
        self.resizable(False, False)
        self.configure(bg="black")
        self.create_widgets()

    def create_widgets(self):
        self.label_atual = tk.Label(self, text="Agora:")
        self.label_atual.pack(pady=8)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=5)
        tk.Label(form_frame, text="Produto:").grid(row=0, column=0)
        self.entry_produto = tk.Entry(form_frame)
        self.entry_produto.grid(row=0, column=1)
        tk.Label(form_frame, text="Validade (DD/MM/AAAA):").grid(row=0, column=2)
        self.entry_validade = tk.Entry(form_frame)
        self.entry_validade.grid(row=0, column=3)
        self.button_add = tk.Button(form_frame, text="Adicionar", command=self.adicionar_produto)
        self.button_add.grid(row=0, column=4, padx=5)

        self.text_area = tk.Text(self, height=13, width=50)
        self.text_area.pack(pady=8)

        self.button_ativar = tk.Button(self, text="Ativar Monitoramento", command=self.ativar)
        self.button_ativar.pack(pady=5)

    def adicionar_produto(self):
        produto = self.entry_produto.get().strip().title()
        validade = self.entry_validade.get().strip()
        try:
            datetime.datetime.strptime(validade, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return
        novo_arquivo = not os.path.exists(DADOS_FILE)
        precisa_cabecalho = novo_arquivo or os.path.getsize(DADOS_FILE) == 0
        with open(DADOS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            if precisa_cabecalho:
                writer.writerow(['produto', 'validade'])
            writer.writerow([produto, validade])
        self.entry_produto.delete(0, tk.END)
        self.entry_validade.delete(0, tk.END)
        messagebox.showinfo("Sucesso", f"Produto '{produto}' adicionado!")

    def ativar(self):
        self.button_ativar.config(state='disabled')
        self.atualizar()

    def atualizar(self):
        self.label_atual.config(text="Agora: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            produtos, erros = carregar_produtos(DADOS_FILE=DADOS_FILE)
            produtos.sort(key=lambda x: x[1])
            
            self.text_area.tag_configure("vencido", foreground="red")
            self.text_area.delete("1.0", tk.END)
            
            for produto, dias in produtos:
                if dias <= 0:
                    linha = f"⚠️{produto}: {dias} dias - VENCIDO\n"
                    self.text_area.insert(tk.END, linha, "vencido")
                elif dias <= 30:
                    linha = f"⚠️{produto}: {dias} dias para vencer\n"
                    self.text_area.insert(tk.END, linha)
                else:
                    linha = f"{produto}: {dias} dias para vencer\n"
                    self.text_area.insert(tk.END, linha)

            if erros:
                self.text_area.insert(tk.END, "\nErros encontrados:\n" + "\n".join(erros), "vencido")

        except FileNotFoundError as e:
            messagebox.showerror("Erro", str(e))

        self.after(2000000, self.atualizar)

if __name__ == "__main__":
    app = App()
    app.mainloop()