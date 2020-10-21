import os
import socket
import struct
import sys
from threading import Lock, Thread
from pygame import mixer
from pydub import AudioSegment
import pickle
import threading


QUEUE_LENGTH = 10
SEND_BUFFER = 4096

# per-client struct
class Client:
    def __init__(self, conn, addr):
        self.lock = Lock()
        self.conn = conn
        self.addr = addr
        self.operation = None
        self.sent = False


# Thread that sends music and lists to the client.  All send() calls
# are contained in this function. The song is broken into pieces of 
# 10000ms each. Client maintains state of how much of the song it has
# and asks for more based on that
def client_write(client, songlist, songs):
    while 1:
        try:
            client.lock.acquire()
            if client.operation is not None and client.sent == False:
                song_part_size = 10000
                if client.operation == "!!!get_list???":
                    print(client.conn.send(pickle.dumps(songlist)+"eomlist".encode()))
                elif client.operation[:11] == "!!!get_song":
                    print(client.conn.send(songs[int(client.operation[12:-4])][:song_part_size].raw_data+"eomsong".encode()))
                else:
                    args = client.operation[13:-4].split(",")
                    sid = int(args[0])
                    time_start = int(args[1]) * 1000
                    print(client.conn.send(songs[sid][time_start:time_start+song_part_size].raw_data+"eomsong".encode()))
                client.sent = True
            client.lock.release()
        except:
            pass


# Thread that receives commands from the client.  All recv() calls are
# contained in this function.
def client_read(client, songlist, songs):
    while 1:
        #print("hello")
        try:
            data = client.conn.recv(2048)
            if data:
                print("Message received was:", data.decode())
                client.lock.acquire()
                client.sent = False
                client.operation = data.decode()
                client.lock.release()
                #return
            else:
                print("disconnected")
                return
        except:
            return

# gets all song data and stores it for when a client asks
def get_mp3s(musicdir):
    print("Reading music files...")
    songs = []
    songlist = []

    for i, filename in enumerate(os.listdir(musicdir)):
        if not filename.endswith(".mp3"):
            continue
        songlist.append((filename[:-4], i))
        songs.append(AudioSegment.from_mp3(musicdir+"/"+filename))
    print("Found {0} song(s)!".format(len(songs)))
    return songs, songlist

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python server.py [port] [musicdir]")
    if not os.path.isdir(sys.argv[2]):
        sys.exit("Directory '{0}' does not exist".format(sys.argv[2]))

    port = int(sys.argv[1])
    songs, songlist = get_mp3s(sys.argv[2])
    threads = []

    # create a socket and accept incoming connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", port))
    sock.listen(QUEUE_LENGTH)
    while True:
        conn, addr = sock.accept()
        client = Client(conn, addr)
        t = Thread(target=client_read, args=([client, songlist, songs]))
        threads.append(t)
        t.start()
        t = Thread(target=client_write, args=([client, songlist, songs]))
        threads.append(t)
        t.start()
    sock.close()


if __name__ == "__main__":
    main()