from __future__ import print_function
import binascii as c, json as C, hashlib as d, struct as Q, threading as p, time as K, random as e, os, multiprocessing as R, sys as S
import websocket as f

# Các hằng số và khai báo
o = 'hashrate'
n = 'shared'
m = '%064x'
l = False
k = 'port'
j = 'minotaurx'
i = tuple
h = ValueError
b = 'mining.subscribe'
a = 'mining.submit'
Z = 'threads'
Y = print
X = range
W = isinstance
P = True
O = Exception
M = len
J = '\n'
H = 'params'
G = 'method'
F = 'id'
D = int
B = None
A = property
q = os.path.abspath('./libs')
S.path.append(q)

# Đọc cấu hình từ file dataset.txt
def r(file_path):
    E = {}
    try:
        with open(file_path, 'r') as F:
            for G in F:
                B, A = G.strip().split('=', 1)
                if B == k:
                    A = D(A)
                elif B == Z:
                    if A.startswith('['):
                        A = C.loads(A)
                    else:
                        A = D(A)
                E[B] = A
    except Exception as e:
        print(f"Error reading dataset file: {e}")
    return E

# Hàm chuyển đổi tốc độ băm
def t(hashrate):
    A = hashrate
    if A < 1000:
        return '%2f B/s' % A
    if A < 10000000:
        return '%2f KB/s' % (A / 1000)
    if A < 10000000000:
        return '%2f MB/s' % (A / 1000000)
    return '%2f GB/s' % (A / 1000000000)

# Lớp v (cơ sở)
class v:
    _max_nonce = B

    def ProofOfWork(A):
        raise O('Do not use the Subscription class directly, subclass it')

    class StateException(O):
        pass

    def __init__(A):
        A._id = B
        A._difficulty = B
        A._extranonce1 = B
        A._extranonce2_size = B
        A._target = B
        A._worker_name = B

    id = A(lambda s: s._id)
    worker_name = A(lambda s: s._worker_name)
    difficulty = A(lambda s: s._difficulty)
    target = A(lambda s: s._target)
    extranonce1 = A(lambda s: s._extranonce1)
    extranonce2_size = A(lambda s: s._extranonce2_size)

    def set_worker_name(A, worker_name):
        if A._worker_name:
            raise A.StateException('Already authenticated as %r (requesting %r)' % A._username)
        A._worker_name = worker_name

    def _set_target(A, target):
        A._target = m % target

    def set_difficulty(B, difficulty):
        A = difficulty
        if A < 0:
            raise B.StateException('Difficulty must be non-negative')
        if A == 0:
            C = 2 ** 256 - 1
        else:
            C = min(D((4294901760 * 2 ** (256 - 64) + 1) / A - 1 + .5), 2 ** 256 - 1)
        B._difficulty = A
        B._set_target(C)

# Lớp w (cơ sở mở rộng)
class w(v):
    import v3.minotaurx_hash as x
    ProofOfWork = x.getPoWHash
    _max_nonce = 4294967295

    def _set_target(A, target):
        A._target = m % target

y = {j: w}

# Lớp z (Khởi tạo và kết nối WebSocket)
class z:
    def __init__(A, pool_host, pool_port, username, password, threads=4, algorithm=j):
        C = threads
        A._pool_host = pool_host
        A._pool_port = pool_port
        A._username = username
        A._password = password
        A._threads_range = C if W(C, (list, i)) else B
        A._threads = C[0] if W(C, (list, i)) else C
        A._subscription = y[algorithm]()
        A._job = []
        A._ws = B
        A._main_thread = B
        A._accepted_shares = 0
        A._accepted_hash = 0
        A._queue = R.Queue()
        A._stop_event = R.Event()
        A._processes = []
        A._hashrates = []
        A._current_job_id = 'N/A'

    def _set_threads(A):
        if A._threads_range is not B:
            A._threads = e.randint(A._threads_range[0], A._threads_range[1])

    def threads(A):
        return A._threads

    def _console_log(A, hashrate, shared):
        os.system('clear')
        Y('WORK: %s | NUMBER: %d | RESULT: %d | SPEED: %s' % (A._current_job_id, A._threads, shared, t(hashrate)))

    def on_open(A, ws):
    Y("WebSocket connection opened.")
    # Gửi thông điệp 'mining.subscribe'
    auth_message = {
        'method': 'mining.subscribe',
        'params': [],
        'id': 1
    }
    ws.send(C.dumps(auth_message))

def on_message(A, ws, message):
    Y("Received message: %s" % message)
    data = C.loads(message)
    if data['method'] == 'mining.notify':
        A._current_job_id = data['params'][0]
        # Xử lý công việc từ pool
        A._queue.put(data)

    def on_message(A, ws, message):
        Y(f"Received message from pool: {message}")
        try:
            data = C.loads(message)
            if data.get(G) == "mining.notify":
                A._current_job_id = data[H][0]
                A._queue.put(data)
        except C.JSONDecodeError as e:
            Y(f"Error decoding message: {e}")

    def on_error(A, ws, error):
        Y(f"Error: {error}")
        if "Connection is already closed" in str(error):
            Y("Attempting to reconnect...")
            A.serve_forever()

    def on_close(A, ws, close_status_code, close_msg):
        Y(f"WebSocket closed: {close_status_code} - {close_msg}")

    def serve_forever(A):
        ws_url = f"ws://{A._pool_host}:{A._pool_port}"
        A._ws = f.WebSocketApp(
            ws_url,
            on_open=A.on_open,
            on_message=A.on_message,
            on_error=A.on_error,
            on_close=A.on_close,
        )
        Y(f"Connecting to WebSocket at {ws_url}")
        A._console_log(0, 0)
        A._ws.run_forever()

if __name__ == '__main__':
    E = r('dataset.txt')
    N = S.argv[1] if M(S.argv) > 1 else B
    if N:
        E[Z] = C.loads('[{}]'.format(N)) if ',' in N else D(N)
    miner = z(E['host'], E[k], E['username'], E['password'], E[Z], j)
    miner.serve_forever()
