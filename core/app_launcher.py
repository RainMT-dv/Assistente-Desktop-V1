"""App launcher module for opening applications via JSON configuration."""

import json
import os
import re
from typing import Dict, List, Optional, Tuple


class AppLauncher:
    """Launcher for applications defined in JSON configuration."""

    def __init__(self, apps_path: str = "config/apps.json"):
        """
        Initialize the app launcher.

        Args:
            apps_path: Path to apps.json configuration file
        """
        self.apps_path = apps_path
        self.apps: Dict[str, str] = {}
        self._load_apps()

    def _load_apps(self) -> None:
        """Load applications from JSON file."""
        try:
            with open(self.apps_path, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
            print(f"[INFO] AppLauncher carregado: {len(self.apps)} apps")
        except FileNotFoundError:
            print(f"[AVISO] {self.apps_path} não encontrado. Criando arquivo vazio.")
            self.apps = {}
            self._save_apps()
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON inválido em {self.apps_path}: {e}")
            self.apps = {}

    def _save_apps(self) -> None:
        """Save applications to JSON file."""
        try:
            with open(self.apps_path, "w", encoding="utf-8") as f:
                json.dump(self.apps, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERRO] Falha ao salvar apps.json: {e}")

    def reload(self) -> None:
        """Reload applications from disk."""
        self._load_apps()
        print("[INFO] Apps recarregados")

    def find_app(self, query: str) -> Optional[str]:
        """
        Find an app by name (case-insensitive and partial match).

        Args:
            query: App name or partial name to search for

        Returns:
            Path to executable if found, None otherwise
        """
        query_lower = query.lower().strip()

        # Exact match first
        for name, path in self.apps.items():
            if name.lower() == query_lower:
                return path

        # Partial match
        for name, path in self.apps.items():
            if query_lower in name.lower() or name.lower() in query_lower:
                return path

        return None

    def _clean_command(self, text: str) -> str:
        """Remove command keywords like 'abrir', 'abre', etc."""
        # Words to remove from start
        command_words = [
            r"^abrir\s+",
            r"^abre\s+",
            r"^abra\s+",
            r"^launch\s+",
            r"^open\s+",
            r"^executar\s+",
            r"^executa\s+",
            r"^rodar\s+",
            r"^roda\s+",
            r"^iniciar\s+",
            r"^inicia\s+",
        ]

        cleaned = text.lower().strip()
        for pattern in command_words:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    def launch(self, query: str) -> Tuple[bool, str]:
        """
        Launch an application by query.

        Args:
            query: App name or command like "abrir chrome"

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Clean command words
        clean_query = self._clean_command(query)

        if not clean_query:
            return (False, "[Neutra] Qual app você quer abrir?")

        # Find app
        app_path = self.find_app(clean_query)

        if not app_path:
            available = ", ".join(self.list_apps())
            return (False, f"[Neutra] Não encontrei '{clean_query}'. Apps disponíveis: {available}")

        # Launch based on OS
        try:
            if os.name == "nt":  # Windows
                # Check if it has arguments (like Discord's --processStart)
                if " --" in app_path:
                    os.system(f'start "" {app_path}')
                else:
                    os.startfile(app_path)
            else:  # Linux/Mac
                import subprocess
                subprocess.Popen([app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            app_name = clean_query.title()
            return (True, f"[Feliz] Abri o {app_name} pra você!")
        except Exception as e:
            print(f"[ERRO] Falha ao abrir app: {e}")
            return (False, f"[Raiva] Não consegui abrir {clean_query}. Deu erro aqui!")

    def list_apps(self) -> List[str]:
        """
        List all available app names.

        Returns:
            List of app names
        """
        return sorted(self.apps.keys())

    def add_app(self, name: str, path: str) -> bool:
        """
        Add a new application.

        Args:
            name: App name (lowercase recommended)
            path: Full path to executable

        Returns:
            True if added successfully
        """
        if not os.path.exists(path):
            print(f"[AVISO] Caminho não existe: {path}")

        self.apps[name.lower()] = path
        self._save_apps()
        print(f"[INFO] App adicionado: {name} -> {path}")
        return True

    def remove_app(self, name: str) -> bool:
        """
        Remove an application.

        Args:
            name: App name to remove

        Returns:
            True if removed successfully
        """
        name_lower = name.lower()
        if name_lower in self.apps:
            del self.apps[name_lower]
            self._save_apps()
            print(f"[INFO] App removido: {name}")
            return True
        return False


if __name__ == "__main__":
    launcher = AppLauncher()

    print("\n[INFO] Apps disponíveis:")
    for app in launcher.list_apps():
        print(f"  - {app}")

    # Test find
    print("\n[INFO] Testando buscas:")
    test_queries = ["chrome", "wind", "discord", "naoexiste"]
    for q in test_queries:
        result = launcher.find_app(q)
        print(f"  '{q}' -> {result if result else 'Não encontrado'}")
