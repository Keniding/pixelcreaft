const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const multer = require('multer');
const imageController = require('./controllers/imageController');

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(',')
}));
app.use(express.json());

// Rutas para imágenes
app.post('/api/images/upload', upload.single('image'), imageController.uploadImage);
app.get('/api/images/:filename', imageController.getImage);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
