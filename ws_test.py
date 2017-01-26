import websocket
import thread
import time
import json

class turn_holder():
    turn = 'red'
    
def on_message(ws, message):
    print message
    new_message = json.loads(message)
    turn_holder.turn = new_message["turn"]

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(*args):
        while True:
            time.sleep(3)
            ws.send(json.dumps({"player":turn_holder.turn,"move":"punch"}))
            
        time.sleep(1)
        ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://10.161.124.143:8888/ws",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()