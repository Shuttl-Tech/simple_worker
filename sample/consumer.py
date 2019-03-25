from simple_worker import App

app = App(queue_prefix="blah-prefix")


@app.register_task_handler("my_task")
def my_task_handler(a, b):
    # Do something worthwhile
    print(a, b)
    pass


if __name__ == "__main__":

    app.worker().start()
