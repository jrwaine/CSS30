import socket
import threading
from typing import Callable


class Connection:
    MCAST_GRP: str = "224.1.1.1"
    MCAST_PORT: int = 5007

    @classmethod
    def publish_multicast(cls, msg: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.sendto(msg.encode("utf-8"), (cls.MCAST_GRP, cls.MCAST_PORT))

    @classmethod
    def listen_multicast(cls, msg_callback: Callable[[bytes]]) -> threading.Thread:
        def loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except AttributeError:
                pass
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

            sock.bind((cls.MCAST_GRP, cls.MCAST_PORT))
            host = socket.gethostbyname(socket.gethostname())
            sock.setsockopt(
                socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host)
            )
            sock.setsockopt(
                socket.SOL_IP,
                socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(cls.MCAST_GRP) + socket.inet_aton(host),
            )

            try:
                while True:
                    try:
                        data, addr = sock.recvfrom(4096)
                        msg_callback(data)
                    except socket.error as e:
                        print("Expection")
            except:
                sock.close()

        t = threading.Thread(target=loop, args=(), daemon=True)
        t.start()
        return t

    @classmethod
    def send_rcv_unicast(cls, msg: str, port: int) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        sock.connect("localhost", port)
        sock.send(msg)
        b = sock.recv(4096)
        return b.decode("utf-8")

    @classmethod
    def listen_unicast(
        cls, port: int, msg_callback: Callable[[bytes], bytes]
    ) -> threading.Thread:
        def loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            sock.bind("localhost", port)
            sock.listen(5)
            try:
                while True:
                    conn, addr = sock.accept()
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        answer = msg_callback(data)
                        conn.send(answer)
                    conn.close()
            except:
                sock.close()

        t = threading.Thread(target=loop, args=(), daemon=True)
        t.start()
        return t
