from scrip import validade_time
import sys

self = validade_time
def main():
    try:
        app = validade_time.App()
        app.mainloop()
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    main()
    sys.exit(0)