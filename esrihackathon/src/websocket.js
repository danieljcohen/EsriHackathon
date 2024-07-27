let view, track, prevLocation;

function initWebSocket(url) {
  const socket = new WebSocket(url);

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log('WebSocket got message:', data);
    updateLocation(data.latitude, data.longitude);
  };

  socket.onclose = function (event) {
    console.log('WebSocket closed:', event);
  };

  socket.onerror = function (error) {
    console.log('WebSocket error:', error);
  };
}
