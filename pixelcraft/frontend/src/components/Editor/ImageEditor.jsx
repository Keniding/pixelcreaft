import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { 
  Box, 
  Button, 
  Stack, 
  Slider,
  Typography,
  Paper,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';

const API_URL = 'http://localhost:3000/api';

// Funciones auxiliares para la conversión de valores
const convertBrightness = (value) => {
  return (value - 100) / 200; // Convierte 0-200 a -0.5-0.5
};

const convertContrast = (value) => {
  return 0.5 + (value / 200); // Convierte 0-200 a 0.5-1.5
};

const ImageEditor = () => {
  const canvasRef = useRef(null);
  const [canvas, setCanvas] = useState(null);
  const [fabricLoaded, setFabricLoaded] = useState(false);
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [currentImage, setCurrentImage] = useState(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js';
    script.async = true;
    script.onload = () => setFabricLoaded(true);
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  useEffect(() => {
    if (fabricLoaded && canvasRef.current) {
      const fabricCanvas = new window.fabric.Canvas(canvasRef.current, {
        width: 800,
        height: 600,
        backgroundColor: '#f0f0f0'
      });

      setCanvas(fabricCanvas);

      return () => {
        fabricCanvas.dispose();
      };
    }
  }, [fabricLoaded]);

  // Función para aplicar filtros
  const applyFilters = (img) => {
    if (!img) return;

    img.filters = [
      new window.fabric.Image.filters.Brightness({
        brightness: convertBrightness(brightness)
      }),
      new window.fabric.Image.filters.Contrast({
        contrast: convertContrast(contrast)
      })
    ];
    img.applyFilters();
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setLoading(true);
      try {
        const reader = new FileReader();
        reader.onload = (event) => {
          const imgUrl = event.target.result;
          
          window.fabric.Image.fromURL(imgUrl, 
            (img) => {
              canvas.clear();
              
              const scale = Math.min(
                canvas.width / img.width,
                canvas.height / img.height
              );
              
              img.scale(scale);
              img.center();
              
              // Guardar referencia a la imagen actual
              setCurrentImage(img);
              
              // Aplicar filtros iniciales
              applyFilters(img);
              
              canvas.add(img);
              canvas.renderAll();
              setSuccess('Imagen cargada exitosamente');
            },
            {
              crossOrigin: 'anonymous'
            }
          );
        };
        
        reader.readAsDataURL(file);
      } catch (err) {
        setError('Error al cargar la imagen: ' + err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleBrightnessChange = (_, value) => {
    setBrightness(value);
    if (currentImage) {
      applyFilters(currentImage);
      canvas.renderAll();
    }
  };

  const handleContrastChange = (_, value) => {
    setContrast(value);
    if (currentImage) {
      applyFilters(currentImage);
      canvas.renderAll();
    }
  };

  const handleSaveImage = async () => {
    if (!canvas) return;

    setLoading(true);
    try {
      const dataURL = canvas.toDataURL({
        format: 'png',
        quality: 0.8
      });

      const base64Data = dataURL.replace(/^data:image\/\w+;base64,/, "");
      const blob = new Blob([Buffer.from(base64Data, 'base64')], { type: 'image/png' });
      const file = new File([blob], 'edited-image.png', { type: 'image/png' });

      const formData = new FormData();
      formData.append('image', file);

      await axios.post(`${API_URL}/images/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setSuccess('Imagen guardada exitosamente');
    } catch (err) {
      setError('Error al guardar la imagen: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" spacing={3}>
        <Box>
          <canvas ref={canvasRef} />
        </Box>
        <Paper sx={{ p: 2, minWidth: 250 }}>
          <Stack spacing={2}>
            <Button
              variant="contained"
              component="label"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Subir Imagen'}
              <input
                type="file"
                hidden
                accept="image/*"
                onChange={handleImageUpload}
              />
            </Button>

            <Button
              variant="contained"
              onClick={handleSaveImage}
              disabled={loading || !canvas || !currentImage}
            >
              {loading ? <CircularProgress size={24} /> : 'Guardar Imagen'}
            </Button>
            
            <Typography>Brillo ({brightness}%)</Typography>
            <Slider
              value={brightness}
              onChange={handleBrightnessChange}
              min={0}
              max={200}
              step={1}
              valueLabelDisplay="auto"
            />
            
            <Typography>Contraste ({contrast}%)</Typography>
            <Slider
              value={contrast}
              onChange={handleContrastChange}
              min={0}
              max={200}
              step={1}
              valueLabelDisplay="auto"
            />
          </Stack>
        </Paper>
      </Stack>

      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError('')}
      >
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar 
        open={!!success} 
        autoHideDuration={6000} 
        onClose={() => setSuccess('')}
      >
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ImageEditor;
