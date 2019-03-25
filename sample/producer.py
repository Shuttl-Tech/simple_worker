from simple_worker import App

app = App()


@app.register_task_handler("my_task", queue="blah-prefix")
def my_task_handler(a, b):
    # Do something worthwhile
    print(a, b)
    pass


if __name__ == "__main__":
    while True:
        app.add_task("my_task", **{"a": 1, "b": 2})
        # app.add_task('my_task', a=1, b=2)
        input("next")  # wait
