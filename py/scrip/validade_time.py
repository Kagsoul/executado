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
        return [], []  
    try:
        df = pandas.read_csv(DADOS_FILE, delimiter=';', encoding='utf-8')
        df.columns = [col.strip().lower() for col in df.columns]
        produto_col = next((col for col in df.columns if col in ["produto", "produtos", "nome", "item"]), df.columns[0])
        validade_col = next((col for col in df.columns if col in ["validade", "data", "vencimento"]), df.columns[1] if len(df.columns) > 1 else None)

        for idx, row in df.iterrows():
            try:
                produto = str(row.get(produto_col, "Desconhecido")).strip().title()
                validade_str = str(row.get(validade_col, "")).strip() if validade_col else ""
                days = calculate_days_to_expiry(validade_str)
                if days is None:
                    erros.append(f"❌ {produto}: data inválida ({validade_str})")
                else:
                    produtos.append((produto, validade_str, days))
            except Exception as e:
                erros.append(f"Erro ao processar linha {idx+1}: {str(e)}")
    except Exception as e:
        erros.append(f"Erro ao ler arquivo: {str(e)}")
    return produtos, erros

 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📦 Produtos perto do vencimento")
        self.geometry("530x460")
        self.resizable(False, False)
        self.configure(bg="black")
        self.vencidos_historico = []   
        self.create_widgets()
        self.atualizar()

    def create_widgets(self):
        self.label_atual = tk.Label(self, text="Agora:", fg="white", bg="black")
        self.label_atual.pack(pady=8)

        form_frame = tk.Frame(self, bg="black")
        form_frame.pack(pady=5)
        tk.Label(form_frame, text="Produto:", fg="white", bg="black").grid(row=0, column=0)
        self.entry_produto = tk.Entry(form_frame)
        self.entry_produto.grid(row=0, column=1)
        tk.Label(form_frame, text="Validade (DD/MM/AAAA):", fg="white", bg="black").grid(row=0, column=2)
        self.entry_validade = tk.Entry(form_frame)
        self.entry_validade.grid(row=0, column=3)
        self.button_add = tk.Button(form_frame, text="Adicionar", command=self.adicionar_produto)
        self.button_add.grid(row=0, column=4, padx=5)

        self.text_area = tk.Text(self, height=13, width=50)
        self.text_area.pack(pady=8)

        self.button_ativar = tk.Button(self, text="Ativar Monitoramento", command=self.atualizar)
        self.button_ativar.pack(pady=5)

        self.button_remover = tk.Button(self, text="Remover Vencidos", command=self.remover_produtos_vencidos)
        self.button_remover.pack(pady=5)

        legenda = tk.Label(self, text="Legenda: Red Vencido | Orange Quase vencido | Black Ok", fg="white", bg="black")
        legenda.pack(pady=5)

        self.label_removidos = tk.Label(self, text="", fg="white", bg="black", font=("Arial", 10))
        self.label_removidos.pack(pady=3)

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
        self.atualizar()

    def remover_produtos_vencidos(self):
        produtos, erros = carregar_produtos(DADOS_FILE)
        produtos_removidos = [p for p in produtos if calculate_days_to_expiry(p[1]) <= 0]

        if produtos_removidos:
            
            self.vencidos_historico.extend(produtos_removidos)

        
            data_backup = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = os.path.join(BASE_DIR, f"produtos_removidos_{data_backup}.csv")
            with open(backup_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['produto', 'validade'])
                for p in produtos_removidos:
                    writer.writerow([p[0], p[1]])

             
            produtos_restantes = [p for p in produtos if calculate_days_to_expiry(p[1]) > 0]
            with open(DADOS_FILE, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['produto', 'validade'])
                for p in produtos_restantes:
                    writer.writerow([p[0], p[1]])

            removidos_str = "\n".join([f"{p[0]} - {p[1]}" for p in produtos_removidos])
            messagebox.showinfo(
                "Remoção Concluída", 
                f"Produtos vencidos removidos:\n{removidos_str}\n\nBackup criado: {os.path.basename(backup_file)}"
            )
            self.label_removidos.config(
                text=f"✅ {len(produtos_removidos)} produto(s) removido(s) do CSV.",
                fg="lightgreen"
            )
        else:
            messagebox.showinfo("Remoção Concluída", "Nenhum produto vencido encontrado.")
            self.label_removidos.config(
                text="Nenhum produto vencido para remover.",
                fg="orange"
            )

        self.after(5000, lambda: self.label_removidos.config(text=""))
        self.atualizar()

    def atualizar(self):
        self.label_atual.config(text="Agora: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            produtos, erros = carregar_produtos(DADOS_FILE=DADOS_FILE)

             
            todos_produtos = produtos + [(p[0], p[1], calculate_days_to_expiry(p[1])) for p in self.vencidos_historico]

             
            todos_produtos.sort(key=lambda x: x[2] if x[2] is not None else 9999)

            self.text_area.tag_configure("vencido", foreground="red")
            self.text_area.tag_configure("quase_vencido", foreground="orange")
            self.text_area.tag_configure("ok", foreground="black")
            self.text_area.tag_configure("erro", foreground="yellow")

            self.text_area.delete("1.0", tk.END)

            for produto, validade_str, dias in todos_produtos:
                if dias is None:
                    linha = f"❓ {produto}: data inválida ({validade_str})\n"
                    self.text_area.insert(tk.END, linha, "erro")
                elif dias <= 0:
                    linha = f"⚠️ {produto}: {dias} dias - VENCIDO\n"
                    self.text_area.insert(tk.END, linha, "vencido")
                elif dias <= 30:
                    linha = f"⏳ {produto}: {dias} dias para vencer\n"
                    self.text_area.insert(tk.END, linha, "quase_vencido")
                else:
                    linha = f"{produto}: {dias} dias restantes\n"
                    self.text_area.insert(tk.END, linha, "ok")

            if erros:
                self.text_area.insert(tk.END, "\nErros encontrados:\n", "erro")
                for erro in erros:
                    self.text_area.insert(tk.END, erro + "\n", "erro")

        except FileNotFoundError as e:
            messagebox.showerror("Erro", str(e))

        self.after(20000, self.atualizar)   

 
if __name__ == "__main__":
    app = App()
    app.mainloop()
