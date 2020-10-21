import readline
import socket
import struct
import sys
import threading
from time import sleep
import pickle
from pygame import mixer


# Utilised existing skeleton with some changes
# Wrapper used to communicate between threads
class mywrapper(object):
    def __init__(self):
        self.id = None
        self.socket_length = 0
        self.usual = 0
        self.channel = None
        self.send = True


# Receive messages and add music to channel
def recv_thread_func(wrap, cond_filled, sock, channel):
    dat = b''
    while True:
        try:
            # when data is received, get all of it
            data = sock.recv(4096)
            if data:
                dat += data
                # if we reach end of message (seen by reading eomlist
                # or eomsong) then do stuff with data
                if data[-7:] == b'eomlist':
                    # data is song list. Simply print
                    print(pickle.loads(dat[:-7]))
                    dat = b''
                elif data[-7:] == b'eomsong':
                    # data is song. If this is continuation, add to channel
                    # queue. If not, play in channel.
                    cond_filled.acquire()
                    sound = mixer.Sound(buffer=dat[:-7])
                    # if file received is smaller than usual, add to queue
                    # but set id to None since song is over
                    if sound.get_length() < wrap.usual:
                        wrap.id, wrap.socket_length, wrap.usual, wrap.send = None, 0, 0, True
                        if channel.get_busy() == 1:
                            channel.queue(sound)
                    elif channel.get_busy() == 1:
                        channel.queue(sound)
                        wrap.send = True
                        wrap.socket_length += sound.get_length()
                    else:
                        channel.play(sound)
                        wrap.usual = sound.get_length()
                        wrap.socket_length += sound.get_length()
                    cond_filled.release()
                    dat = b''
            else:
                print("disconnected")
                return
        except Exception as e:
            print(e)
            return


# this thread function is just used to ask for more music,
# that is, continue the song that was already playing
def play_thread_func(wrap, cond_filled, sock, channel):
    while True:
        cond_filled.acquire()
        ch_busy, ch_queue, wr_send, wr_id = channel.get_busy(), channel.get_queue(), wrap.send, wrap.id
        cond_filled.release()
        if ch_busy == 1 and ch_queue == None and wr_send and wr_id is not None:
                cond_filled.acquire()
                query = "!!!cont_song("+wrap.id+","+str(wrap.socket_length)[:-2]+")???"
                sock.send(query.encode())
                wrap.send = False
                cond_filled.release()


def main():
    if len(sys.argv) < 3:
        print('Usage: %s <server name/ip> <server port>' % sys.argv[0])
        sys.exit(1)


    mixer.init(frequency=44100, buffer=4096)
    channel = mixer.Channel(0)


    # Create a pseudo-file wrapper, condition variable, and socket.  These will
    # be passed to the thread we're about to create.
    wrap = mywrapper()
    wrap.channel = channel

    # Create a condition variable to synchronize the receiver and player threads.
    # In python, this implicitly creates a mutex lock too.
    # See: https://docs.python.org/2/library/threading.html#condition-objects
    cond_filled = threading.Condition()

    # Create a TCP socket and try connecting to the server.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], int(sys.argv[2])))

    

    # Create a thread whose job is to receive messages from the server.
    recv_thread = threading.Thread(
        target=recv_thread_func,
        args=(wrap, cond_filled, sock, channel)
    )
    recv_thread.daemon = True
    recv_thread.start()

    play_thread = threading.Thread(
        target=play_thread_func,
        args=(wrap, cond_filled, sock, channel)
    )
    play_thread.daemon = True
    play_thread.start()

    # Enter our never-ending user I/O loop.  Because we imported the readline
    # module above, input gives us nice shell-like behavior (up-arrow to
    # go backwards, etc.).
    while True:
        line = input()

        if ' ' in line:
            cmd, args = line.split(' ', 1)
        else:
            cmd = line

        # TODO: Send messages to the server when the user types things.
        if cmd in ['l', 'list']:
            print('The user asked for list.')
            cond_filled.acquire()
            sock.send("!!!get_list???".encode())
            cond_filled.release()

        if cmd in ['p', 'play']:
            print('The user asked to play:', args)
            query = "!!!get_song("+args+")???"
            cond_filled.acquire()
            if channel.get_busy() == 1:
                channel.stop()
            wrap.id = args
            sock.send(query.encode())
            cond_filled.release()

        if cmd in ['s', 'stop']:
            print('The user asked for stop.')
            cond_filled.acquire()
            channel.stop() 
            cond_filled.release()

        if cmd in ['quit', 'q', 'exit']:
            sys.exit(0)

if __name__ == '__main__':
    main()
