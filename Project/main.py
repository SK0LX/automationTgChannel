import time

import schedule

from DIContainer import AppContainer

if __name__ == "__main__":
    container = AppContainer()
    job = container.job_runner()

    schedule.every(1).seconds.do(job.run, 1, "meta-llama/llama-3.2-3b-instruct:free")

    while True:
        schedule.run_pending()
        time.sleep(1)