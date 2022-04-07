import socket
import struct
import threading
import traceback
from typing import Callable


class Connection:
    MCAST_GRP: str = "224.1.1.1"
    MCAST_PORT: int = 5007

    @classmethod
    def publish_multicast(cls, msg: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.sendto(msg.encode("utf-8"), (cls.MCAST_GRP, cls.MCAST_PORT))
        sock.close()

    @classmethod
    def listen_multicast(
        cls, port: int, msg_callback: Callable[[bytes], None]
    ) -> threading.Thread:
        def loop():
            # MCAST_GRP = '224.1.1.1'
            # MCAST_PORT = 5007
            # IS_ALL_GROUPS = True

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # on this port, listen ONLY to MCAST_GRP
            sock.bind((cls.MCAST_GRP, cls.MCAST_PORT))
            mreq = struct.pack(
                "4sl", socket.inet_aton(cls.MCAST_GRP), socket.INADDR_ANY
            )

            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            try:
                while True:
                    try:
                        data, addr = sock.recvfrom(4096)
                        msg_callback(data)
                    except socket.error as e:
                        print("Expection socker", e)
                        traceback.print_exc()
            except Exception as e:
                print("multicast error", e)
                traceback.print_exc()
            sock.close()

        t = threading.Thread(target=loop, args=(), daemon=True)
        t.start()
        return t

    @classmethod
    def send_unicast(cls, msg: str, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        sock.connect(("localhost", port))
        sock.send(msg.encode("utf-8"))
        sock.close()

    @classmethod
    def listen_unicast(
        cls, port: int, msg_callback: Callable[[bytes], bytes]
    ) -> threading.Thread:
        def loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            sock.bind(("localhost", port))
            sock.listen(5)
            try:
                while True:
                    conn, addr = sock.accept()
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        answer = msg_callback(data)
                        # conn.send(answer)
                    conn.close()
            except:
                sock.close()

        t = threading.Thread(target=loop, args=(), daemon=True)
        t.start()
        return t
