#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

class ChatClient:
    def __init__(self, config_file="api_config.json"):
        self.config_file = config_file
        self.api_key = None
        self.api_base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.provider = "openai"
        self.conversation_history = []
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key")
                    self.api_base_url = config.get("api_url", "https://api.openai.com/v1/chat/completions")
                    self.model = config.get("model", "gpt-3.5-turbo")
                    self.provider = config.get("provider", "openai")
                    return config
            except Exception:
                pass
        return {}

    def _save_config(self, api_key, api_url, model, provider):
        config = {
            "api_key": api_key,
            "api_url": api_url,
            "model": model,
            "provider": provider
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.api_key = api_key
            self.api_base_url = api_url
            self.model = model
            self.provider = provider
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def _setup_api(self):
        providers = [
            {"name": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-3.5-turbo"},
            {"name": "deepseek", "url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat"},
            {"name": "custom", "url": "", "model": ""}
        ]

        print("\n" + "=" * 60)
        print("               API 配置")
        print("=" * 60)
        print("首次使用需要配置API信息")
        print()

        print("请选择API提供商:")
        for i, p in enumerate(providers, 1):
            print(f"{i}. {p['name'].capitalize()}")
        
        while True:
            try:
                choice = int(input("\n请输入选择 (1-3): "))
                if 1 <= choice <= 3:
                    selected_provider = providers[choice - 1]
                    break
                print("无效选择，请输入1-3")
            except ValueError:
                print("请输入数字")

        api_key = input("\n请输入API Key: ").strip()
        if not api_key:
            print("API Key不能为空")
            return False

        if selected_provider["name"] == "custom":
            api_url = input("请输入API URL: ").strip()
            if not api_url:
                print("API URL不能为空")
                return False
            model = input("请输入模型名称: ").strip()
            if not model:
                print("模型名称不能为空")
                return False
        else:
            api_url = selected_provider["url"]
            model = selected_provider["model"]
            print(f"\n自动配置:")
            print(f"  API URL: {api_url}")
            print(f"  模型: {model}")

        if self._save_config(api_key, api_url, model, selected_provider["name"]):
            print("\n配置已保存!")
            return True
        return False

    def _change_api(self):
        providers = [
            {"name": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-3.5-turbo"},
            {"name": "deepseek", "url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat"},
            {"name": "custom", "url": "", "model": ""}
        ]

        print("\n" + "=" * 60)
        print("            修改 API 配置")
        print("=" * 60)

        print("\n当前配置:")
        print(f"  提供商: {self.provider}")
        print(f"  API URL: {self.api_base_url}")
        print(f"  模型: {self.model}")
        print(f"  API Key: {'*' * 20}{self.api_key[-20:] if self.api_key else '未设置'}")

        print("\n请选择API提供商:")
        for i, p in enumerate(providers, 1):
            print(f"{i}. {p['name'].capitalize()}")
        
        while True:
            try:
                choice = int(input("\n请输入选择 (1-3，直接回车保留当前): "))
                if 1 <= choice <= 3:
                    selected_provider = providers[choice - 1]
                    break
                elif choice == "":
                    selected_provider = {"name": self.provider, "url": self.api_base_url, "model": self.model}
                    break
                print("无效选择，请输入1-3")
            except ValueError:
                selected_provider = {"name": self.provider, "url": self.api_base_url, "model": self.model}
                break

        api_key = input("\n新API Key (直接回车保留当前): ").strip()
        if not api_key:
            api_key = self.api_key

        if not api_key:
            print("API Key不能为空")
            return False

        if selected_provider["name"] == "custom" or selected_provider["name"] != self.provider:
            if selected_provider["name"] == "custom":
                api_url = input("请输入API URL: ").strip()
                if not api_url:
                    print("API URL不能为空")
                    return False
                model = input("请输入模型名称: ").strip()
                if not model:
                    print("模型名称不能为空")
                    return False
            else:
                api_url = selected_provider["url"]
                model = selected_provider["model"]
        else:
            api_url = self.api_base_url
            model = self.model

        if self._save_config(api_key, api_url, model, selected_provider["name"]):
            print("\n配置已更新!")
            return True
        return False

    def send_request(self, user_message):
        if not self.api_key:
            if not self._setup_api():
                return None

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.api_base_url, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                assistant_reply = result["choices"][0]["message"]["content"]
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_reply
                })
                return assistant_reply

        except urllib.error.HTTPError as e:
            error_msg = e.read().decode("utf-8")
            print(f"\nHTTP错误: {e.code}")
            try:
                error_data = json.loads(error_msg)
                if error_data.get("error", {}).get("code") == "invalid_api_key":
                    print("API Key无效，请使用 'config' 命令重新配置")
                else:
                    print(f"错误信息: {error_data.get('error', {}).get('message', '未知错误')}")
            except:
                print(f"错误信息: {error_msg[:200]}")
            return None
        except urllib.error.URLError as e:
            print(f"\n网络错误: {e.reason}")
            return None
        except Exception as e:
            print(f"\n请求错误: {e}")
            return None

    def run(self):
        print("=" * 60)
        print("          命令行聊天工具")
        print("=" * 60)
        print("输入 'exit' 或 'quit' 退出聊天")
        print("输入 'clear' 清空对话历史")
        print("输入 'history' 查看对话历史")
        print("输入 'config' 修改API配置")
        print("=" * 60)

        if not self.api_key:
            print("\n提示: 首次使用需要配置API信息")
            if not self._setup_api():
                print("配置失败，无法继续")
                return

        while True:
            try:
                user_input = input("\n你: ").strip()

                if user_input.lower() in ["exit", "quit"]:
                    print("再见!")
                    break

                if user_input.lower() == "config":
                    self._change_api()
                    continue

                if user_input.lower() == "clear":
                    self.conversation_history = []
                    print("对话历史已清空")
                    continue

                if user_input.lower() == "history":
                    print("\n--- 对话历史 ---")
                    for msg in self.conversation_history:
                        role = "你" if msg["role"] == "user" else "AI"
                        print(f"{role}: {msg['content']}")
                    print("--- 历史结束 ---")
                    continue

                if not user_input:
                    continue

                print("AI: ", end="", flush=True)

                reply = self.send_request(user_input)

                if reply:
                    print(reply)
                else:
                    print("无法获取回复，请重试")

            except KeyboardInterrupt:
                print("\n再见!")
                break

def main():
    client = ChatClient()
    client.run()

if __name__ == "__main__":
    main()