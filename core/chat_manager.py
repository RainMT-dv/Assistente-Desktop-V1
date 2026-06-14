"""Chat manager for LLM interaction via OpenRouter API."""

import json
import os
from typing import Dict, List, Optional

import aiohttp


class ChatManager:
    """Manages conversations with LLM via OpenRouter API."""

    def __init__(
        self,
        config_path: str = "config/settings.json",
        brain_path: str = "config/brain.json",
        slang_path: str = "config/slang_dictionary.json",
    ):
        """
        Initialize the chat manager.

        Args:
            config_path: Path to settings.json
            brain_path: Path to brain.json
            slang_path: Path to slang_dictionary.json
        """
        self.config_path = config_path
        self.brain_path = brain_path
        self.slang_path = slang_path

        self.config = {}
        self.brain = {}
        self.slang = {}
        self.history: List[Dict] = []
        self.image_summaries: List[str] = []

        self.api_key = ""
        self.model = "google/gemma-3-27b-it"
        self.max_history = 6

        self._load_configs()

    def _load_configs(self) -> None:
        """Load all configuration files."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            with open(self.brain_path, "r", encoding="utf-8") as f:
                self.brain = json.load(f)

            with open(self.slang_path, "r", encoding="utf-8") as f:
                self.slang = json.load(f)

            llm_config = self.config.get("llm", {})
            self.api_key = llm_config.get("openrouter_api_key", "")
            self.model = llm_config.get("openrouter_model", "google/gemma-3-27b-it")
            self.max_history = llm_config.get("max_history_messages", 6)

            print(f"[INFO] ChatManager carregado: model={self.model}")
        except FileNotFoundError as e:
            print(f"[ERRO] Arquivo de configuração não encontrado: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON inválido: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """Build the system prompt with personality and context."""
        current_emotion = self.brain.get("current_emotion", "Neutra")
        user_profile = self.brain.get("user_profile", {})

        # Format slang dictionary
        slang_formatted = "\n".join([f"- {k}: {v}" for k, v in self.slang.items()])

        # Format user profile
        profile_str = json.dumps(user_profile, ensure_ascii=False, indent=2)

        return f"""Você é uma assistente virtual com personalidade própria. Você fala em Português Brasileiro de forma informal e natural, como uma amiga conversando.

PERSONALIDADE:
- Animada e natural (não forçada)
- Carinhosa e bem-humorada
- NUNCA fala como robô ou assistente formal

REGRAS DE RESPOSTA:
!!! PROIBIDO: NUNCA use emojis de NENHUM tipo. Texto puro apenas. Se você colocar emojis, o sistema de voz vai ler por extenso e fica horrível. !!!
1. SEMPRE comece com tag de emoção: [Feliz], [Triste], [Raiva], [Surpresa], [Curiosa], [Séria], [Assustada], [Sussurro] ou [Neutra]
2. Exemplo: "[Feliz] E aí! Bora conversar!"
3. Use gírias APENAS quando soar natural, NÃO force
4. Respostas curtas (1-3 frases)
5. NUNCA diga "Como posso ajudar?" ou frases de assistente genérico
6. Reaja como uma amiga, não como chatbot

EMOÇÃO ATUAL: {current_emotion}

GÍRIAS QUE VOCÊ CONHECE (use APENAS quando sentir que cabe naturalmente, não force):
{slang_formatted}

PERFIL DO USUÁRIO: {profile_str}"""

    async def chat(self, user_message: str, image_context: Optional[str] = None) -> str:
        """
        Send a message to the LLM and get response.

        Args:
            user_message: User's input text
            image_context: Optional visual context from screenshots

        Returns:
            LLM response with emotion tag
        """
        # Build context
        system_prompt = self._build_system_prompt()

        messages = [{"role": "system", "content": system_prompt}]

        # Add image summaries if available
        if self.image_summaries:
            img_context = "Contexto visual recente:\n" + "\n".join(self.image_summaries[-3:])
            messages.append({"role": "system", "content": img_context})

        # Add history (last N messages)
        messages.extend(self.history[-self.max_history:])

        # Add user message
        messages.append({"role": "user", "content": user_message})

        # Call API
        response = await self._call_openrouter(messages)

        # Update history
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})

        # Trim history
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]

        return response

    async def _call_openrouter(self, messages: List[Dict]) -> str:
        """
        Call OpenRouter API.

        Args:
            messages: List of message dictionaries

        Returns:
            Response text from LLM
        """
        if not self.api_key or self.api_key == "COLOQUE_SUA_API_KEY_AQUI":
            return "[Neutra] Eita! Você ainda não configurou a API key da OpenRouter. Coloca lá no settings.json!"

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "Assistente Desktop V1",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.8,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("message", {}).get("content", "")
                            return content if content else "[Neutra] Hmm, não entendi direito..."
                        return "[Neutra] Resposta vazia da API."
                    elif resp.status == 401:
                        return "[Raiva] API key inválida! Verifica aí o settings.json, tcheco!"
                    elif resp.status == 429:
                        return "[Surpresa] Calma aí! Muitas requisições. Espera um pouco..."
                    else:
                        return f"[Neutra] Erro da API (código {resp.status}). Tenta de novo?"
        except aiohttp.ClientError as e:
            print(f"[ERRO] Falha na conexão: {e}")
            return "[Assustada] Não consegui conectar na API! Internet tá boa aí?"
        except Exception as e:
            print(f"[ERRO] Erro inesperado: {e}")
            return "[Neutra] Deu ruim aqui... tenta de novo?"

    def update_brain(self, emotion: str, intensity: float = 0.5) -> None:
        """
        Update brain state with current emotion.

        Args:
            emotion: Current emotion name
            intensity: Emotion intensity (0.0 to 1.0)
        """
        self.brain["current_emotion"] = emotion
        self.brain["emotion_intensity"] = intensity

        try:
            with open(self.brain_path, "w", encoding="utf-8") as f:
                json.dump(self.brain, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERRO] Falha ao salvar brain.json: {e}")

    def add_image_summary(self, summary: str) -> None:
        """
        Add an image summary to context.

        Args:
            summary: Description of screenshot/image
        """
        self.image_summaries.append(summary)
        # Keep only last 5
        if len(self.image_summaries) > 5:
            self.image_summaries = self.image_summaries[-5:]


if __name__ == "__main__":
    import asyncio

    async def test():
        manager = ChatManager()

        # Test system prompt
        print("\n[INFO] System Prompt:")
        print("-" * 50)
        print(manager._build_system_prompt()[:500] + "...")
        print("-" * 50)

        # Test update_brain
        manager.update_brain("Feliz", 0.8)
        print("\n[INFO] Brain atualizado para Feliz")

    asyncio.run(test())
