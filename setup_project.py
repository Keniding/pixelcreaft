import os
import subprocess
import json
import sys
from pathlib import Path

def check_dependencies():
    print("Verificando dependencias necesarias...")
    
    # Verificar Node.js
    try:
        node_version = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
        if node_version.returncode == 0:
            print(f"✅ Node.js instalado: {node_version.stdout.strip()}")
        else:
            print("❌ Node.js no encontrado")
            print("Por favor, instala Node.js desde https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("❌ Node.js no encontrado")
        print("Por favor, instala Node.js desde https://nodejs.org/")
        return False

    # Verificar npm
    try:
        npm_version = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
        if npm_version.returncode == 0:
            print(f"✅ npm instalado: {npm_version.stdout.strip()}")
        else:
            print("❌ npm no encontrado")
            print("Por favor, reinstala Node.js desde https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("❌ npm no encontrado")
        print("Por favor, reinstala Node.js desde https://nodejs.org/")
        return False

    return True

def create_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"📁 Creado directorio: {path}")

def create_file(path, content=""):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Creado archivo: {path}")

def run_npm_install(package=None):
    try:
        if package:
            cmd = ["npm", "install", package, "--save"]
        else:
            cmd = ["npm", "install"]
        
        result = subprocess.run(cmd, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print(f"❌ Error instalando {'dependencias' if not package else package}")
        return False

def setup_frontend():
    print("\n🚀 Configurando Frontend...")
    os.chdir("frontend")
    
    # Inicializar proyecto Vite con React
    print("Inicializando proyecto Vite con React...")
    process = subprocess.Popen(
        ["npm", "create", "vite@latest", ".", "--", "--template", "react"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    # Enviar "1" para seleccionar "Remove existing files and continue"
    stdout, stderr = process.communicate(input="1\n")
    
    print("📦 Instalando dependencias base del frontend...")
    if not run_npm_install():
        print("❌ Error instalando dependencias base")
        return False
    
    # Instalar dependencias adicionales una por una
    print("📦 Instalando dependencias adicionales...")
    dependencies = [
        "@mui/material",
        "@emotion/react",
        "@emotion/styled",
        "@mui/icons-material",
        "fabric"
    ]
    
    for dep in dependencies:
        print(f"Instalando {dep}...")
        if not run_npm_install(dep):
            print(f"❌ Error instalando {dep}")
            return False
        print(f"✅ {dep} instalado correctamente")
    
    os.chdir("..")
    return True

def setup_backend():
    print("\n🚀 Configurando Backend...")
    os.chdir("backend")

    # Crear package.json
    package_json = {
        "name": "pixelcraft-backend",
        "version": "1.0.0",
        "description": "Backend para PixelCraft - Editor de imágenes",
        "main": "src/index.js",
        "scripts": {
            "start": "node src/index.js",
            "dev": "nodemon src/index.js",
            "test": "echo \"Error: no test specified\" && exit 1"
        },
        "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5",
            "dotenv": "^16.3.1",
            "multer": "^1.4.5-lts.1",
            "sharp": "^0.32.6"
        },
        "devDependencies": {
            "nodemon": "^3.0.1"
        }
    }

    create_file("package.json", json.dumps(package_json, indent=2))

    # Crear .env
    env_content = """PORT=3000
UPLOAD_DIR=uploads
ALLOWED_ORIGINS=http://localhost:5173"""
    create_file(".env", env_content)

    # Crear .gitignore
    gitignore_content = """node_modules/
.env
uploads/*
!uploads/.gitkeep"""
    create_file(".gitignore", gitignore_content)

    # Crear archivo principal index.js
    index_js_content = """const express = require('express');
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
});"""
    create_file("src/index.js", index_js_content)

    # Crear archivo de configuración
    config_js_content = """require('dotenv').config();

module.exports = {
port: process.env.PORT || 3000,
uploadDir: process.env.UPLOAD_DIR || 'uploads',
allowedOrigins: process.env.ALLOWED_ORIGINS.split(',')
};"""
    create_file("src/config/config.js", config_js_content)

    # Crear archivo vacío en uploads para mantener el directorio en git
    create_file("uploads/.gitkeep", "")

    print("📦 Instalando dependencias del backend...")
    if not run_npm_install():
        print("❌ Error instalando dependencias del backend")
        return False

    os.chdir("..")
    return True

def setup_project():
    if not check_dependencies():
        sys.exit(1)

    # Limpiar caché de npm
    print("🧹 Limpiando caché de npm...")
    subprocess.run(["npm", "cache", "clean", "--force"], shell=True)

    # Directorio raíz del proyecto
    root_dir = "pixelcraft"
    create_directory(root_dir)
    os.chdir(root_dir)

    # Estructura Frontend
    frontend_dir = "frontend"
    create_directory(frontend_dir)

    # Estructura Backend
    backend_dir = "backend"
    create_directory(backend_dir)

    # Frontend directories
    frontend_dirs = [
        "src/components/Editor",
        "src/components/Toolbar",
        "src/components/Filters",
        "src/services",
        "src/utils",
        "public",
    ]

    for dir_path in frontend_dirs:
        create_directory(os.path.join(frontend_dir, dir_path))

    # Backend directories
    backend_dirs = [
        "src/controllers",
        "src/services",
        "src/models",
        "src/middleware",
        "src/config",
        "uploads"
    ]

    for dir_path in backend_dirs:
        create_directory(os.path.join(backend_dir, dir_path))

    frontend_success = setup_frontend()
    backend_success = setup_backend()

    if frontend_success and backend_success:
        print("\n✨ ¡Proyecto creado exitosamente!")
        print("\nPasos siguientes:")
        print("1. cd pixelcraft/frontend")
        print("2. npm run dev")
        print("\nEn otra terminal:")
        print("3. cd pixelcraft/backend")
        print("4. npm run dev")
    else:
        print("\n❌ Hubo errores durante la instalación")
        print("Por favor, verifica los mensajes de error anteriores")

if __name__ == "__main__":
    setup_project()