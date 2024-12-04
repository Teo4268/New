from __future__ import print_function
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
import binascii as c, json as C, hashlib as d, struct as Q, threading as p, time as K, random as e, os, multiprocessing as R, sys as S
q = os.path.abspath('./libs')
S.path.append(q)
import websocket as f
T = j
A1 = [T]


def r(file_path):
    E = {}
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
    return E


def t(hashrate):
    A = hashrate
    if A < 1000:
        return '%2f B/s' % A
    if A < 10000000:
        return '%2f KB/s' % (A / 1000)
    if A < 10000000000:
        return '%2f MB/s' % (A / 1000000)
    return '%2f GB/s' % (A / 1000000000)


class v:
    _max_nonce = B

    def ProofOfWork(A):
        raise O('Do not use the Subscription class directly, subclass it')

    class StateException(O):
        0

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


class w(v):
    import v3.minotaurx_hash as x
    ProofOfWork = x.getPoWHash
    _max_nonce = 4294967295

    def _set_target(A, target):
        A._target = m % target


y = {T: w}


class z:
    # Các hàm khởi tạo và thuộc tính vẫn giữ nguyên
    def __init__(A, pool_host, pool_port, username, password, threads=4, algorithm=T):
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

      # Định nghĩa lại _console_log
    def _console_log(A, hashrate, shared):
        """
        Hiển thị thông tin khai thác trên console.
        """
        os.system('clear')  # Xóa màn hình console
        Y('WORK: %s | NUMBER: %d | RESULT: %d | SPEED: %s' % (A._current_job_id, A.threads, shared, t(hashrate)))

    
    
    def threads(self):
        return self._threads
    # Hàm on_open được định nghĩa lại
    def on_open(A, ws):
        """
        Được gọi khi kết nối WebSocket mở thành công.
        """
        Y("WebSocket connection opened.")
        auth_message = {
            F: 1,
            G: b,
            H: [A._username, A._password]
        }
        ws.send(C.dumps(auth_message) + J)  # Gửi thông điệp xác thực đến pool
        B = p.Thread(target=A.queue_message)  # Khởi chạy luồng xử lý tin nhắn trong hàng đợi
        B.daemon = P
        B.start()
        Y("Authentication sent to pool.")

    # Hàm queue_message vẫn giữ nguyên
    def queue_message(A):
        while P:
            if not A._queue.empty():
                B = A._queue.get()
                A._accepted_hash = B[o]
                A._ws.send(B[n])
            else:
                K.sleep(.25)

    # Định nghĩa các hàm khác (on_message, on_error, on_close)
    def on_message(A, ws, message):
        Y("Received message from pool: %s" % message)
        try:
            data = C.loads(message)
            if data.get(G) == "mining.notify":
                A._current_job_id = data[H][0]
                # Xử lý công việc từ pool
                A._queue.put(data)
        except C.JSONDecodeError as e:
            Y("Error decoding message: %s" % e)

    def on_error(A, ws, error):
        Y("Error: %s" % error)

    def on_close(A, ws, close_status_code, close_msg):
        Y("WebSocket closed: %s - %s" % (close_status_code, close_msg))

    # Hàm serve_forever giữ nguyên
    def serve_forever(A):
        f.enableTrace(l)
        ws_url = f"ws://{A._pool_host}:{A._pool_port}"
        A._ws = f.WebSocketApp(
            ws_url,
            on_open=A.on_open,
            on_message=A.on_message,
            on_error=A.on_error,
            on_close=A.on_close,
        )
        A._console_log(0, 0)
        A._ws.run_forever()


if __name__ == '__main__':
    E = r('dataset.txt')
    N = S.argv[1] if M(S.argv) > 1 else B
    if N:
        E[Z] = C.loads('[{}]'.format(N)) if ',' in N else D(N)
    miner = z(E['host'], E[k], E['username'], E['password'], E[Z], j)
    miner.serve_forever()
