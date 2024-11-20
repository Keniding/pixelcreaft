import json
import subprocess
import os
from datetime import datetime
from shutil import copy2
from typing import Dict, List, Tuple

class DependencyUpdater:
    def __init__(self, project_type: str):
        self.project_type = project_type
        if project_type == "frontend":
            self.project_dir = "pixelcraft/frontend"
        else:
            self.project_dir = "pixelcraft/backend"
            
        self.package_json_path = os.path.join(self.project_dir, "package.json")
        self.backup_dir = os.path.join(self.project_dir, "backups")

    def create_backup(self) -> None:
        """Crear backup de los archivos de configuración"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup package.json
        if os.path.exists(self.package_json_path):
            backup_path = os.path.join(self.backup_dir, f"package.json.{timestamp}")
            copy2(self.package_json_path, backup_path)
            print(f"✅ Backup creado en: {backup_path}")
        
        # Backup package-lock.json
        package_lock = os.path.join(self.project_dir, "package-lock.json")
        if os.path.exists(package_lock):
            backup_lock_path = os.path.join(self.backup_dir, f"package-lock.json.{timestamp}")
            copy2(package_lock, backup_lock_path)
            print(f"✅ Backup de package-lock creado en: {backup_lock_path}")

    def run_command(self, command: str) -> Tuple[str, str, int]:
        """Ejecutar comando en el directorio del proyecto"""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.project_dir
            )
            stdout, stderr = process.communicate()
            return stdout, stderr, process.returncode
        except Exception as e:
            return "", str(e), 1

    def get_latest_version(self, package: str) -> str:
        """Obtener la última versión de un paquete"""
        cmd = f"npm view {package} version"
        stdout, _, code = self.run_command(cmd)
        return stdout.strip() if code == 0 else ""

    def update_package_json(self) -> None:
        """Actualizar package.json con las últimas versiones"""
        try:
            with open(self.package_json_path, 'r') as f:
                package_data = json.load(f)

            print(f"\n📦 Actualizando {self.project_type}...")

            # Actualizar dependencias regulares
            if "dependencies" in package_data:
                print("\n📦 Actualizando dependencies...")
                for pkg in package_data["dependencies"]:
                    latest = self.get_latest_version(pkg)
                    if latest:
                        old_version = package_data["dependencies"][pkg]
                        package_data["dependencies"][pkg] = f"^{latest}"
                        print(f"  ↑ {pkg}: {old_version} → ^{latest}")

            # Actualizar devDependencies
            if "devDependencies" in package_data:
                print("\n🛠️ Actualizando devDependencies...")
                for pkg in package_data["devDependencies"]:
                    latest = self.get_latest_version(pkg)
                    if latest:
                        old_version = package_data["devDependencies"][pkg]
                        package_data["devDependencies"][pkg] = f"^{latest}"
                        print(f"  ↑ {pkg}: {old_version} → ^{latest}")

            # Guardar cambios
            with open(self.package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
            print(f"\n✅ package.json de {self.project_type} actualizado")

        except Exception as e:
            print(f"❌ Error actualizando package.json: {str(e)}")

    def install_dependencies(self) -> None:
        """Instalar dependencias actualizadas"""
        print(f"\n📥 Instalando dependencias actualizadas para {self.project_type}...")
        commands = [
            "npm install",
            "npm audit fix",
            "npm cache clean --force"
        ]

        for cmd in commands:
            print(f"\n🔄 Ejecutando: {cmd}")
            stdout, stderr, code = self.run_command(cmd)
            if code != 0:
                print(f"⚠️ Advertencia en {cmd}:")
                print(stderr)
            else:
                print(stdout)

    def run_update(self) -> None:
        """Ejecutar proceso completo de actualización"""
        if not os.path.exists(self.project_dir):
            print(f"❌ No se encontró el directorio {self.project_dir}")
            return

        print(f"\n🚀 Iniciando actualización de dependencias para {self.project_type}...")
        
        # Crear backup
        self.create_backup()
        
        # Actualizar package.json
        self.update_package_json()
        
        # Instalar dependencias
        self.install_dependencies()
        
        print(f"\n✨ Proceso de actualización completado para {self.project_type}")
        
        # Mostrar dependencias actuales usando caracteres ASCII
        stdout, _, _ = self.run_command("npm list --depth=0")
        print(f"\n📋 Dependencias actuales de {self.project_type}:")
        for line in stdout.split('\n'):
            if '└──' in line:
                line = line.replace('└──', '+--')
            if '├──' in line:
                line = line.replace('├──', '+--')
            if line.strip():
                print(line)

def update_all_projects():
    """Actualizar tanto frontend como backend"""
    print("🔄 Iniciando actualización de todos los proyectos...")

    # Verificar que exista el directorio pixelcraft
    if not os.path.exists("pixelcraft"):
        print("❌ No se encontró el directorio pixelcraft")
        return

    # Actualizar Frontend
    print("\n=== FRONTEND ===")
    frontend_updater = DependencyUpdater("frontend")
    frontend_updater.run_update()

    # Actualizar Backend
    print("\n=== BACKEND ===")
    backend_updater = DependencyUpdater("backend")
    backend_updater.run_update()

    print("\n✅ Actualización completa de todos los proyectos")

if __name__ == "__main__":
    update_all_projects()