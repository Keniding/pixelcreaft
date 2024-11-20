require('dotenv').config();

module.exports = {
port: process.env.PORT || 3000,
uploadDir: process.env.UPLOAD_DIR || 'uploads',
allowedOrigins: process.env.ALLOWED_ORIGINS.split(',')
};