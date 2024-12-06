import socket
import json
import threading
import time
import os
import random
import struct
import hashlib
import binascii
import queue

# Utility functions
def t(hashrate):
    A = hashrate
    if A < 1000:
        return '%2f B/s' % A
    if A < 10000000:
        return '%2f KB/s' % (A / 1000)
    if A < 10000000000:
        return '%2f MB/s' % (A / 1000000)
    return '%2f GB/s' % (A / 1000000000)

def g(message):
    return hashlib.sha256(hashlib.sha256(message).digest()).digest()

def V(hex_word):
    A = binascii.unhexlify(hex_word)
    if len(A) != 4:
        raise ValueError('Must be 4-byte word')
    return A[::-1]

def s(hex_words):
    A = binascii.unhexlify(hex_words)
    if len(A) % 4 != 0:
        raise ValueError('Must be 4-byte word aligned')
    B = b''.join([A[4 * B:4 * B + 4][::-1] for B in range(len(A) // 4)])
    return B

class u:
    def __init__(self, job_id, prevhash, coinb1, coinb2, merkle_branches, version, nbits, ntime, target, extranonce1, extranonce2_size, proof_of_work, max_nonce=4294967295):
        self._job_id = job_id
        self._prevhash = prevhash
        self._coinb1 = coinb1
        self._coinb2 = coinb2
        self._merkle_branches = [branch for branch in merkle_branches]
        self._version = version
        self._nbits = nbits
        self._ntime = ntime
        self._max_nonce = max_nonce
        self._target = target
        self._extranonce1 = extranonce1
        self._extranonce2_size = extranonce2_size
        self._proof_of_work = proof_of_work
        self._done = False
        self._dt = 0.0
        self._hash_count = 0

    def hashrate(self):
        if self._dt == 0:
            return 0.0
        return self._hash_count / self._dt

    def merkle_root_bin(self, extranonce2_bin):
        C = binascii.unhexlify(self._coinb1) + binascii.unhexlify(self._extranonce1) + extranonce2_bin + binascii.unhexlify(self._coinb2)
        D = g(C)
        B = D
        for branch in self._merkle_branches:
            B = g(B + binascii.unhexlify(branch))
        return B

    def stop(self):
        self._done = True

    def mine(self, nonce_start=0, nonce_end=1):
        B = time.time()
        C = '{:0{}x}'.format(random.randint(0, 2 ** (8 * self._extranonce2_size) - 1), self._extranonce2_size * 2)
        E = struct.pack('<I', int(C, 16)) if self._extranonce2_size <= 4 else struct.pack('<Q', int(C, 16))
        G = self.merkle_root_bin(E)
        H = V(self._version) + s(self._prevhash) + G + V(self._ntime) + V(self._nbits)
        I = range(nonce_start, nonce_end, 1)
        for J in I:
            if self._done:
                self._dt += time.time() - B
                raise StopIteration()
            F = struct.pack('<I', J)
            pow = binascii.hexlify(self._proof_of_work(H + F)[::-1]).decode('utf-8')
            if int(pow, 16) <= int(self._target, 16):
                L = dict(job_id=self._job_id, extranonce2=binascii.hexlify(E), ntime=str(self._ntime), nonce=binascii.hexlify(F[::-1]))
                self._dt += time.time() - B
                yield L
            B = time.time()
            self._hash_count += 1

    def __str__(self):
        return f'<Job id={self._job_id} prevhash={self._prevhash} coinb1={self._coinb1} coinb2={self._coinb2} merkle_branches={self._merkle_branches} version={self._version} nbits={self._nbits} ntime={self._ntime} target={self._target} extranonce1={self._extranonce1} extranonce2_size={self._extranonce2_size}>'

class v:
    _max_nonce = None

    def ProofOfWork(self):
        raise Exception('Do not use the Subscription class directly, subclass it')

    class StateException(Exception):
        pass

    def __init__(self):
        self._id = None
        self._difficulty = None
        self._extranonce1 = None
        self._extranonce2_size = None
        self._target = None
        self._worker_name = None
        self._mining_thread = None

    def set_worker_name(self, worker_name):
        if self._worker_name:
            raise self.StateException(f'Already authenticated as {self._worker_name} (requesting {worker_name})')
        self._worker_name = worker_name

    def _set_target(self, target):
        self._target = target

    def set_difficulty(self, difficulty):
        if difficulty < 0:
            raise self.StateException('Difficulty must be non-negative')
        if difficulty == 0:
            C = 2 ** 256 - 1
        else:
            C = min(int((4294901760 * 2 ** (256 - 64) + 1) / difficulty - 1 + 0.5), 2 ** 256 - 1)
        self._difficulty = difficulty
        self._set_target(C)

    def set_subscription(self, subscription_id, extranonce1, extranonce2_size):
        if self._id is not None:
            raise self.StateException('Already subscribed')
        self._id = subscription_id
        self._extranonce1 = extranonce1
        self._extranonce2_size = extranonce2_size

    def create_job(self, job_id, prevhash, coinb1, coinb2, merkle_branches, version, nbits, ntime):
        if self._id is None:
            raise self.StateException('Not subscribed')
        return u(job_id=job_id, prevhash=prevhash, coinb1=coinb1, coinb2=coinb2, merkle_branches=merkle_branches, version=version, nbits=nbits, ntime=ntime, target=self._target, extranonce1=self._extranonce1, extranonce2_size=self._extranonce2_size, proof_of_work=self.ProofOfWork, max_nonce=self._max_nonce)

    def __str__(self):
        return f'<Subscription id={self._id}, extranonce1={self._extranonce1}, extranonce2_size={self._extranonce2_size}, difficulty={self._difficulty} worker_name={self._worker_name}>'

class w(v):
    def __init__(self):
        import v3.minotaurx_hash as x
        self.ProofOfWork = x.getPoWHash
        self._max_nonce = 4294967295

    def _set_target(self, target):
        self._target = target

class z:
    def __init__(self, pool_host, pool_port, username, password, threads=4, algorithm=None):
        self._pool_host = pool_host
        self._pool_port = pool_port
        self._username = username
        self._password = password
        self._threads_range = threads if isinstance(threads, (list, tuple)) else [threads]
        self._threads = self._threads_range[0] if isinstance(threads, (list, tuple)) else threads
        self._subscription = algorithm() if algorithm else None
        self._job = []
        self._accepted_shares = 0
        self._accepted_hash = 0
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._processes = []
        self._hashrates = []
        self._current_job_id = 'N/A'
        self._socket = None

    def _set_threads(self):
        if self._threads_range != [None]:
            self._threads = random.randint(self._threads_range[0], self._threads_range[1])

    def _console_log(self, hashrate, shared):
        os.system('clear')
        print(f'WORK: {self._current_job_id} | NUMBER: {self._threads} | RESULT: {shared} | SPEED: {hashrate}')

    def _cleanup(self):
        self._queue.empty()
        for job in self._job:
            job.stop()
        for process in self._processes:
            process.terminate()
            process.join()
        self._processes = []
        self._hashrates = []
        self._job = []

    def _connect_socket(self):
        # Create a socket connection to the pool
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._pool_host, self._pool_port))

    def _send_message(self, message):
        # Send a message to the pool via the socket
        try:
            self._socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self._cleanup()

    def _receive_message(self):
        # Receive a message from the pool
        try:
            data = self._socket.recv(1024).decode('utf-8')
            if not data:
                raise ConnectionError("No data received")
            return data
        except Exception as e:
            print(f"Error receiving message: {e}")
            self._cleanup()
            return None

    def _send_subscription(self):
        # Send subscription request to the pool
        subscription_message = json.dumps({
            "id": 1,
            "method": "mining.subscribe",
            "params": []
        })
        self._send_message(subscription_message)

    def _send_authorize(self):
        # Send authorization message to the pool
        authorize_message = json.dumps({
            "id": 2,
            "method": "mining.authorize",
            "params": [self._username, self._password]
        })
        self._send_message(authorize_message)

    def _start_mining(self):
        # Start mining process by receiving jobs from the pool
        while not self._stop_event.is_set():
            try:
                response = self._receive_message()
                if response:
                    response_json = json.loads(response)
                    if response_json.get("method") == "mining.notify":
                        job_data = response_json.get("params")
                        if job_data:
                            job = self._subscription.create_job(*job_data)
                            self._job.append(job)
                            self._process_jobs(job)
                    time.sleep(0.5)  # Prevent too frequent polling
            except Exception as e:
                print(f"Error during mining process: {e}")
                self._cleanup()

    def _process_jobs(self, job):
        # Process each mining job (can be multithreaded)
        for result in job.mine():
            self._accepted_shares += 1
            self._accepted_hash += 1
            print(f"Accepted share: {result}")
            self._queue.put(result)
            self._current_job_id = job._job_id
            self._console_log(t(self._accepted_hash), self._accepted_shares)

    def start(self):
        # Start the entire mining process
        self._connect_socket()
        self._send_subscription()
        self._send_authorize()

        self._start_mining()

    def stop(self):
        # Stop mining and clean up
        self._stop_event.set()
        self._cleanup()

if __name__ == '__main__':
    pool_host = 'minotaurx.na.mine.zpool.ca'
    pool_port = 7019
    username = 'R9uHDn9XXqPAe2TLsEmVoNrokmWsHREV2Q'
    password = 'c=RVN'
    algorithm = w  # Example, should be defined based on your specific algorithm
    mining_client = z(pool_host, pool_port, username, password, threads=4, algorithm=algorithm)

    try:
        mining_client.start()
    except KeyboardInterrupt:
        mining_client.stop()
