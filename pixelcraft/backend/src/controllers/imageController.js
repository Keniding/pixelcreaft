const sharp = require('sharp');
const { minioClient, bucketName } = require('../config/minio');
const { v4: uuidv4 } = require('uuid');

const uploadImage = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const buffer = req.file.buffer;
    const filename = `${uuidv4()}.jpg`;

    // Procesar la imagen con Sharp
    const processedBuffer = await sharp(buffer)
      .jpeg({ quality: 80 })
      .toBuffer();

    // Subir a Minio
    await minioClient.putObject(
      bucketName,
      filename,
      processedBuffer
    );

    // Generar URL temporal
    const url = await minioClient.presignedGetObject(bucketName, filename, 24*60*60); // 24 horas

    res.json({
      success: true,
      filename,
      url
    });

  } catch (error) {
    console.error('Error uploading image:', error);
    res.status(500).json({ error: 'Error processing image' });
  }
};

const getImage = async (req, res) => {
  try {
    const { filename } = req.params;
    const url = await minioClient.presignedGetObject(bucketName, filename, 24*60*60);
    res.json({ url });
  } catch (error) {
    res.status(500).json({ error: 'Error getting image' });
  }
};

module.exports = {
  uploadImage,
  getImage
};
