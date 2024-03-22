const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const AWS = require('aws-sdk');
const { ExpressAdapter } = require('socket.io-adapter-express');

// Configure AWS IVS
const IVS = new AWS.IVS({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION
});

// Route to generate a new stream key
app.get('/generateStreamKey', async (req, res) => {
  try {
    const streamKey = await IVS.createStreamKey({ channelArn: process.env.IVS_CHANNEL_ARN }).promise();
    res.json({ streamKey: streamKey.streamKey });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to generate stream key' });
  }
});

// Serve static files (including client-side code)
app.use(express.static('public'));

io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('disconnect', () => {
    console.log('user disconnected');
  });

  socket.on('stream', (data) => {
    // Broadcast stream data to all connected clients
    io.emit('stream', data);
  });
});

http.listen(5000, () => {
  console.log('Server is running on port 5000');
});
