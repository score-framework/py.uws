#ifndef USE_LIBUV
#define USE_LIBUV
#endif

#include <map>
#include "uWS/uWS.h"
#include <condition_variable>
#include <Python.h>

class UwsHub;

typedef uWS::WebSocket<uWS::SERVER> UwsWebSocket;

typedef std::function<void(void* data, uWS::WebSocket<uWS::SERVER>*)> OnConnectCallbackType;
typedef std::function<void(void* data, uWS::WebSocket<uWS::SERVER>*, char *, size_t)> OnMessageCallbackType;
typedef std::function<void(void* data, uWS::WebSocket<uWS::SERVER>*, int, char *, size_t)> OnDisconnectCallbackType;

class Hub : public uWS::Hub {

    public:
        void stopListening();

};

void Hub::stopListening() {
    this->uWS::Group<uWS::SERVER>::stopListening();
}

typedef struct {
    Hub* hub;
    bool stopped;
    std::mutex stopMutex;
    std::condition_variable stopCondition;
} StopCallbackData;

class UwsHub {

    public:
        void onConnect(OnConnectCallbackType callback, void* data);
        void onDisconnect(OnDisconnectCallbackType callback, void* data);
        void onMessage(OnMessageCallbackType callback, void* data);

        bool listen(char* host, int port);
        void stopListening();

        void start();
        void stop();

    private:
        Hub hub;

        uv_async_t stopHandle;
        StopCallbackData stopData;
};

void stopCallback(uv_async_t* handle) {
    auto uv_walk_callback = [](uv_handle_t* handle, void* /*arg*/) {
        if (!uv_is_closing(handle))
            uv_close(handle, nullptr);
    };
    auto loop = handle->loop;
    auto data = (StopCallbackData*) handle->data;
    data->hub->getDefaultGroup<true>().close();
    uv_stop(loop);
    uv_walk(loop, uv_walk_callback, nullptr);
    uv_run(loop, UV_RUN_DEFAULT);
    uv_loop_close(loop);
    std::unique_lock< std::mutex > lock(data->stopMutex);
    data->stopped = true;
    data->stopCondition.notify_one();
    lock.unlock();
};

bool UwsHub::listen(char* host, int port) {
    return this->hub.listen(host, port);
};

void UwsHub::stopListening() {
    this->hub.stopListening();
};

void UwsHub::start() {
    this->stopData.hub = &(this->hub);
    this->stopData.stopped = false;
    this->stopHandle.data = &this->stopData;
    uv_loop_t* loop = this->hub.getLoop();
    uv_async_init(loop, &(this->stopHandle), stopCallback);
    this->hub.run();
};

void UwsHub::stop() {
    uv_async_send(&(this->stopHandle));
    std::unique_lock< std::mutex > lock(this->stopData.stopMutex);
    while (!this->stopData.stopped) {
        this->stopData.stopCondition.wait(lock);
    }
};

void UwsHub::onConnect(OnConnectCallbackType callback, void* data) {
    this->hub.onConnection([this, callback, data](uWS::WebSocket<uWS::SERVER>* ws, uWS::HttpRequest req) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        callback(data, ws);
        PyGILState_Release(gstate);
    });
};

void UwsHub::onDisconnect(OnDisconnectCallbackType callback, void* data) {
    this->hub.onDisconnection([this, callback, data](uWS::WebSocket<uWS::SERVER>* ws, int code, char *message, size_t length) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        callback(data, ws, code, message, length);
        PyGILState_Release(gstate);
    });
};

void UwsHub::onMessage(OnMessageCallbackType callback, void* data) {
    this->hub.onMessage([this, callback, data](uWS::WebSocket<uWS::SERVER>* ws, char *message, size_t length, uWS::OpCode opCode) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        callback(data, ws, message, length);
        PyGILState_Release(gstate);
    });
};
