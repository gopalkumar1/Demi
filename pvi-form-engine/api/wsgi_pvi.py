from run_pvi_api import app

def worker_abort(worker):
    print("worker_abort")
    return {"code":1}
    pass

def on_reload(server):
    print(" worker on_reload")
    return {"code":2}
    pass

if __name__ == "__main__":
	app.run()
