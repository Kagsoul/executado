from scrip import validade_time
def main():
    try:
        app = validade_time.App()
        app.mainloop()
    except Exception as e:
        print(f"Erro ao executar o app: {e}")

if __name__ == "__main__":
    main()
    