const Minio = require('minio');
require('dotenv').config();

const minioClient = new Minio.Client({  
    endPoint: process.env.MINIO_ENDPOINT || 'localhost',
    port: parseInt(process.env.MINIO_PORT) || 9000, 
    useSSL: process.env.MINIO_USE_SSL === 'true',
    accessKey: process.env.MINIO_ACCESS_KEY,
    secretKey: process.env.MINIO_SECRET_KEY
});

const bucketName = process.env.MINIO_BUCKET_NAME || 'images';

const ensureBucket = async () => {
    try {
        const exists = await minioClient.bucketExists(bucketName);
        if (!exists) {
            await minioClient.makeBucket(bucketName);
            console.log(`Bucket ${bucketName} created successfully`);
        }
    } catch (err) {
        console.error('Error creating bucket:', err);
    }
};

ensureBucket();

module.exports = { minioClient, bucketName };
