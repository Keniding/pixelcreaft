const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors({
origin: process.env.ALLOWED_ORIGINS.split(',')
}));
app.use(express.json());

app.get('/', (req, res) => {
res.json({ message: 'PixelCraft API is running' });
});

app.listen(port, () => {
console.log(`Server is running on port ${port}`);
});