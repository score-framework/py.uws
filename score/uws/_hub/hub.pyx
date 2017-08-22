from libcpp.map cimport map


cdef extern from "<uWS/uWS.h>" namespace "uWS":

    cdef enum OpCode:
        TEXT = 1
        BINARY = 2
        CLOSE = 8
        PING = 9
        PONG = 10


cdef extern from "uws.cpp":

    ctypedef void (*on_connect_cb)(
        void* data, UwsWebSocket *ws)

    ctypedef void (*on_disconnect_cb)(
        void* data, UwsWebSocket *ws, int code, char *message, size_t length)

    ctypedef void (*on_message_cb)(
        void* data, UwsWebSocket *ws, char *message, size_t length)

    cdef cppclass UwsWebSocket:

        void send(char*, OpCode)

    cdef cppclass UwsHub:
        void onConnect(on_connect_cb callback, void* data)
        void onDisconnect(on_disconnect_cb callback, void* data)
        void onMessage(on_message_cb callback, void* data)
        int listen(char* host, int port)
        void stopListening()
        void start() nogil
        void stop() nogil


cdef class Client:

    cdef UwsWebSocket* _c_ws

    cdef public hub

    cdef public dict data

    def __init__(Client self, hub):
        self.hub = hub
        self.data = {}

    cdef send(self, str message):
        b = message.encode('UTF-8')
        cdef char* msg = b
        self._c_ws.send(msg, OpCode.TEXT)


cdef class Hub:

    cdef UwsHub* _c_hub

    connect_callbacks = []

    disconnect_callbacks = []

    message_callbacks = []

    connections = []

    def __cinit__(self):
        self._c_hub = new UwsHub()
        if self._c_hub is NULL:
            raise MemoryError()
        self._c_hub.onConnect(_on_connect_callback, <void*>self)
        self._c_hub.onDisconnect(_on_disconnect_callback, <void*>self)
        self._c_hub.onMessage(_on_message_callback, <void*>self)

    def __dealloc__(self):
        if self._c_hub is not NULL:
            del self._c_hub

    cpdef void listen(self, str host, int port) except *:
        host_ = host.encode('UTF-8')
        if not self._c_hub.listen(host_, port):
            raise Exception('Error on call to hub.listen()')

    cpdef void stop_listening(self) except *:
        self._c_hub.stopListening()

    cpdef void start(self):
        with nogil:
            self._c_hub.start()

    cpdef void stop(self):
        with nogil:
            self._c_hub.stop()

    cpdef void add_connect_callback(self, callback):
        self.connect_callbacks.append(callback)

    cpdef void add_disconnect_callback(self, callback):
        self.disconnect_callbacks.append(callback)

    cpdef void add_message_callback(self, callback):
        self.message_callbacks.append(callback)

    cpdef void remove_connect_callback(self, callback):
        self.connect_callbacks.remove(callback)

    cpdef void remove_disconnect_callback(self, callback):
        self.disconnect_callbacks.remove(callback)

    cpdef void remove_message_callback(self, callback):
        self.message_callbacks.remove(callback)

    cdef void _on_connect(Hub self, Client client):
        for callback in self.connect_callbacks:
            callback(client)

    cdef void _on_disconnect(Hub self, Client client, int code, str message):
        for callback in self.disconnect_callbacks:
            callback(client, code, message)

    cdef void _on_message(Hub self, Client client, str message):
        for callback in self.message_callbacks:
            callback(client, message)


ctypedef UwsWebSocket* UwsWebSocketP
ctypedef void* voidP


cdef map[UwsWebSocketP, voidP] _connectionMap


cdef void _on_connect_callback(void* data, UwsWebSocket *ws):
    hub = (<Hub>data)
    client = Client(hub)
    client._c_ws = ws
    _connectionMap[ws] = <void*>client
    hub.connections.append(client)
    hub._on_connect(client)


cdef void _on_disconnect_callback(void* data, UwsWebSocket *ws, int code,
                                  char *message, size_t length):
    hub = (<Hub>data)
    client = <Client>(_connectionMap[ws])
    hub._on_disconnect(client, code, str(message[:length], 'ASCII'))
    _connectionMap.erase(ws)
    hub.connections.remove(client)


cdef void _on_message_callback(void* data, UwsWebSocket *ws,
                               char *message, size_t length):
    client = <Client>(_connectionMap[ws])
    hub = <Hub>(client.hub)
    hub._on_message(client, str(message[:length], 'UTF-8'))
