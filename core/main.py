import time
import schedule
import argparse
from DIContainer import AppContainer


def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Запуск задания с определенным интервалом.")
    parser.add_argument("-t", type=int, required=True, help="Интервал в часах")
    args = parser.parse_args()

    container = AppContainer()
    job = container.job_runner()

    # Планирование задания
    schedule.every(args.t).seconds.do(job.run, 1, "meta-llama/llama-3.2-3b-instruct:free")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
