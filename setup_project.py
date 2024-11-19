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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Creado archivo: {path}")

def run_npm_install(package=None):
    try:
        if package:
            cmd = ["npm", "install", package, "--save", "--force"]
        else:
            cmd = ["npm", "install", "--force"]
        
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            print(f"❌ Error en npm install: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {'dependencias' if not package else package}")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def create_update_script():
    update_script = """#!/bin/bash
echo "🔍 Verificando actualizaciones de dependencias..."
npm outdated

echo "\\n📦 Actualizando dependencias..."
npm update

echo "\\n🛡️ Verificando vulnerabilidades..."
npm audit

echo "\\n🧹 Ejecutando npm audit fix..."
npm audit fix

echo "\\n✨ Proceso de actualización completado"
"""
    create_file("update-deps.sh", update_script)
    # Hacer el script ejecutable
    os.chmod("update-deps.sh", 0o755)
def setup_frontend():
    print("\n🚀 Configurando Frontend...")
    try:
        os.chdir("frontend")
    except Exception as e:
        print(f"❌ Error al cambiar al directorio frontend: {e}")
        return False
    
    # Inicializar proyecto Vite con React
    print("Inicializando proyecto Vite con React...")
    try:
        process = subprocess.run(
            ["npm", "create", "vite@latest", ".", "--", "--template", "react-ts"],
            shell=True,
            input="y\n",
            text=True,
            capture_output=True
        )
        if process.returncode != 0:
            print("❌ Error inicializando proyecto Vite")
            print(process.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("📦 Instalando dependencias base del frontend...")
    if not run_npm_install():
        print("❌ Error instalando dependencias base")
        os.chdir("..")
        return False
    
    # Lista actualizada de dependencias
    dependencies = [
        "@mui/material@^5.15.0",
        "@emotion/react@^11.11.1",
        "@emotion/styled@^11.11.0",
        "@mui/icons-material@^5.15.0",
        "konva@^9.2.3",
        "react-konva@^18.2.10",
        "typescript@^5.3.0",
        "@types/node@^20.10.0",
        "@types/react@^18.2.0",
        "@types/react-dom@^18.2.0",
        "axios@^1.6.2",
        "zustand@^4.4.7",
        "@typescript-eslint/eslint-plugin@^6.13.1",
        "@typescript-eslint/parser@^6.13.1",
        "eslint@^8.55.0",
        "eslint-plugin-react-hooks@^4.6.0",
        "eslint-plugin-react-refresh@^0.4.5",
        "prettier@^3.1.0"
    ]
    
    for dep in dependencies:
        print(f"Instalando {dep}...")
        if not run_npm_install(dep):
            print(f"❌ Error instalando {dep}")
            continue

    # Crear tsconfig.json con configuración optimizada
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": True,
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
            "strict": True,
            "noUnusedLocals": True,
            "noUnusedParameters": True,
            "noFallthroughCasesInSwitch": True,
            "types": ["vite/client"],
            "baseUrl": ".",
            "paths": {
                "@/*": ["src/*"]
            }
        },
        "include": ["src"],
        "references": [{ "path": "./tsconfig.node.json" }]
    }
    
    create_file("tsconfig.json", json.dumps(tsconfig, indent=2))

    # Actualizar package.json
    with open('package.json', 'r') as f:
        package_data = json.load(f)

    package_data['scripts'].update({
        "dev": "vite",
        "build": "tsc && vite build",
        "preview": "vite preview",
        "update-deps": "npm update && npm audit fix",
        "check-updates": "npm outdated",
        "type-check": "tsc --noEmit",
        "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
        "format": "prettier --write \"src/**/*.{ts,tsx}\""
    })

    package_data['engines'] = {
        "node": ">=18.0.0"
    }

    with open('package.json', 'w') as f:
        json.dump(package_data, f, indent=2)

    # Crear archivo de configuración de ESLint
    eslint_config = {
        "root": True,
        "env": {
            "browser": True,
            "es2020": True
        },
        "extends": [
            "eslint:recommended",
            "plugin:@typescript-eslint/recommended",
            "plugin:react-hooks/recommended"
        ],
        "ignorePatterns": ["dist", ".eslintrc.json"],
        "parser": "@typescript-eslint/parser",
        "plugins": ["react-refresh"],
        "rules": {
            "react-refresh/only-export-components": [
                "warn",
                { "allowConstantExport": True }
            ]
        }
    }
    create_file(".eslintrc.json", json.dumps(eslint_config, indent=2))

    # Crear archivo de configuración de Prettier
    prettier_config = {
        "semi": True,
        "singleQuote": True,
        "trailingComma": "es5",
        "tabWidth": 2,
        "printWidth": 100
    }
    create_file(".prettierrc", json.dumps(prettier_config, indent=2))

    create_update_script()
    
    try:
        os.chdir("..")
        return True
    except Exception as e:
        print(f"❌ Error al volver al directorio raíz: {e}")
        return False
    create_update_script()

    try:
        os.chdir("..")
        return True
    except Exception as e:
        print(f"❌ Error al volver al directorio raíz: {e}")
        return False

def setup_project():
    if not check_dependencies():
        return False

    print("\n🎯 Iniciando configuración del proyecto...")
    
    # Crear estructura de directorios
    create_directory("frontend")
    
    # Configurar frontend
    if not setup_frontend():
        print("❌ Error en la configuración del frontend")
        return False

    print("""
✅ Configuración completada con éxito!

Para comenzar:
1. cd frontend
2. npm run dev

Comandos disponibles:
- npm run dev: Iniciar servidor de desarrollo
- npm run build: Construir para producción
- npm run preview: Previsualizar build
- npm run lint: Ejecutar ESLint
- npm run format: Formatear código con Prettier
- npm run type-check: Verificar tipos TypeScript
- npm run update-deps: Actualizar dependencias
- npm run check-updates: Verificar actualizaciones disponibles

¡Feliz desarrollo! 🚀
    """)
    return True

if __name__ == "__main__":
    try:
        setup_project()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)
