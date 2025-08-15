import csv
import validade_time
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_FILE = os.path.join(BASE_DIR, "produtos.csv")

def adicionar_produto(produto, validade):
    try:
        datetime.strptime(validade, '%d/%m/%Y')
    except ValueError:
        print("❌ Data inválida. Use o formato DD/MM/AAAA.")
        return False

    novo_arquivo = not os.path.exists(DADOS_FILE)
    precisa_cabecalho = novo_arquivo or os.path.getsize(DADOS_FILE) == 0

    with open(DADOS_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        if precisa_cabecalho:
            writer.writerow(['produto', 'validade'])
        writer.writerow([produto.strip().title(), validade])
        print(f"✅ Produto '{produto}' adicionado com sucesso.")
        return True

if __name__ == "__main__":
    print("📦 Adicionar novo produto")
    nome = input("Digite o nome do produto: ")
    validade = input("Digite a data de validade (DD/MM/AAAA): ")
    sucesso = adicionar_produto(produto=nome, validade=validade)
    if sucesso:
        validade_time.App().mainloop()
