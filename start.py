from multiprocessing import Process
from __init__ import app
from python.run_bot import run_bot

def start_bot():
    run_bot()

if __name__ == "__main__":
    try:
        bot_process = Process(target=start_bot)
        bot_process.start()

        print("Процесс run_bot запущен.")

        app.run(host='26.45.155.104', port=8000, debug=False)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        print("Запуск завершен")
