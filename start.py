from __init__ import app
from python.dsbot.run_bot import run_bot
import multiprocessing

if __name__ == "__main__":
    try:
        manager = multiprocessing.Manager()
        shared_data = manager.dict()
        
        run_bot_process = multiprocessing.Process(target=run_bot) 
        run_bot_process.start()

        print("Процесс run_bot запущен.")

        app.run(host='26.45.155.104', port=8000, debug=False)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        print('Запуск завершен')
