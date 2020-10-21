# Streaming Music Service for Graduate Networked Systems Course

In this project, you'll be designing and implementing a protocol of your own design to build a streaming music service.
In class, we discussed a few approaches to building such a service: simple HTTP gets, a custom streaming protocol like RTSP, or DASH-like chunking via HTTP.
For this project, we want you to try your hand at a custom protocol to learn all of the concerns that go into constructing one.
Note that while RTSP is a good strawman, it is likely *much* more complicated than you need for this project.

Since you will be developing the protocol, client, and server, there is no single correct design or architecture.
This is different from previous projects, where you have seen and implemented several types of protocols -- now you get to decide how to apply the patterns you've seen in a new scenario!


### Requirements

* Your protocol should be implemented directly on top of sockets.  You should not, for instance, use an HTTP protocol or implementation.

* We have provided skeleton code for a threaded client and server in Python.  Feel free to start from scratch in a different language or with a different architecture (e.g.,  select() statements).  If you choose a different language, you will be responsible for finding libraries that can play mp3 files.

* Your server should be able to handle multiple clients simultaneously.  They should be able join and leave at any time, and the server should continue to operate seamlessly.

* The client should be able to stream, i.e., start playing music before the mp3 has been downloaded.  Note that mp3s are designed exactly for this purpose!  If you start feeding  mp3 data frames to a music player, it will be able to play without needing the entire file.

* Your client should be interactive and it should know how to handle at least the following commands:
    * `list`: Retrieve a list of songs that are available on the server, along with their ID numbers.
    * `play [song number]`: Begin playing the song with the specified ID number. If another song is already playing, the client should switch immediately to the new one.
    * `stop`: Stops playing the current song, if there is one playing.

* The client should not cache data. In other words, if the user tells the client to get a song list or play a song, the two should exchange messages to facilitate this. Don't retrieve an item from the server once and then repeat it back again on subsequent requests.

* One of the parameters to your server should be a path to a directory that contains audio files. Within this directory, you may assume that any file ending in ".mp3" is an mp3 audio file. I have provided two files as a start.  Feel free to use those or your own mp3 files for testing. **Please do not submit audio files to Canvas!**

* You are allowed to develop and demo this project outside of the Vagrant VM, but we have already set up the Vagrant VM to be compatible with playing audio programmatically.  It may also facilitate interoperability between partners with different OSes and installed packages.
