import typer, subprocess, sys, time, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = typer.Typer()

class RH(FileSystemEventHandler):
    def __init__(self, s):
        self.s = s
        self.p = None
        self.st()

    def st(self):
        if self.p: self.p.kill()
        self.p = subprocess.Popen([sys.executable, '-m', self.s], env=os.environ.copy())

    def on_modified(self, e):
        if e.src_path.endswith('.py'):
            print(f'Reloading...')
            self.st()

@app.command()
def run(r: bool = typer.Option(False, "--reload")):
    if r:
        o = Observer()
        o.schedule(RH('Bot'), 'Bot', recursive=True)
        o.start()
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt: o.stop()
        o.join()
    else:
        import runpy
        runpy.run_module("Bot", run_name="__main__")

if __name__ == "__main__":
    app()