const express = require('express');
const cors = require('cors');
const multer = require('multer');
const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');

const app = express();
const port = 8000;

app.use(cors());

const s3 = new AWS.S3({
  accessKeyId: 'AKIAXYKJVB4MMBQZXTOK',
  secretAccessKey: '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',
  region: 'ap-south-1',
});

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

let latestAudioUrl = '';
let latestImageUrl = '';

app.post('/api/upload-audio', upload.single('audio'), async (req, res) => {
  try {
    const audioFile = req.file;

    const params = {
      Bucket: 'cosmic-calm',
      Key: `Audio/${uuidv4()}.mp3`,
      Body: audioFile.buffer,
      ContentType: 'audio/mpeg',
    };

    const data = await s3.upload(params).promise();
    latestAudioUrl = `https://cosmic-calm.s3.ap-south-1.amazonaws.com/${data.Key}`;

    res.status(200).send(latestAudioUrl);
  } catch (error) {
    console.error('Error uploading audio file:', error);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/api/upload-image', upload.single('image'), async (req, res) => {
  try {
    const imageFile = req.file;

    const params = {
      Bucket: 'cosmic-calm',
      Key: `Images/${uuidv4()}.jpg`,
      Body: imageFile.buffer,
      ContentType: 'image/jpeg',
    };

    const data = await s3.upload(params).promise();
    latestImageUrl = `https://cosmic-calm.s3.ap-south-1.amazonaws.com/${data.Key}`;

    res.status(200).send(latestImageUrl);
  } catch (error) {
    console.error('Error uploading image file:', error);
    res.status(500).send('Internal Server Error');
  }
});

app.get('/api/generate-links', (req, res) => {
  res.json({
    audioUrl: latestAudioUrl,
    imageUrl: latestImageUrl,
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
