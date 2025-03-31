#!/usr/bin/env python3
import os
import sys
import argparse
import requests
import json
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path

class DeepSeekConfig:
    def __init__(self):
        self.config_path = os.path.expanduser("~/.deepseek/seek.json")
        self.config = self._load_config()

    def _load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        except:
            pass
        
        if not os.path.exists(self.config_path):
            return {
                "api_key": "",
                "default_model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        
        with open(self.config_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Archivo de configuración inválido en {self.config_path}")
                sys.exit(1)

    def save_config(self):
        """Guarda la configuración actual en el archivo"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_api_key(self):
        if not self.config.get("api_key"):
            print("Error: API key no configurada. Por favor ejecuta 'seek config'")
            sys.exit(1)
        return self.config["api_key"]

class DeepSeekCLI:
    def __init__(self, config):
        self.config = config
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.config.get_api_key()}",
            "Content-Type": "application/json"
        }
    
    def get_response(self, prompt):
        payload = {
            "model": self.config.config.get("default_model", "deepseek-chat"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.config.get("temperature", 0.7),
            "max_tokens": self.config.config.get("max_tokens", 2000)
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return f"Error de conexión: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_code_blocks(self, text):
        code_blocks = []
        current_block = None
        language = None
        
        for line in text.split('\n'):
            if line.startswith('```') and current_block is None:
                language = line[3:].strip()
                current_block = []
            elif line.startswith('```') and current_block is not None:
                if language:
                    code_blocks.append(('code', language, '\n'.join(current_block)))
                current_block = None
                language = None
            elif current_block is not None:
                current_block.append(line)
            else:
                code_blocks.append(('text', None, line))
        
        return code_blocks

    def save_output(self, content, args):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = args.output_name if args.output_name else f"deepseek_output_{timestamp}"
        
        if args.m:
            filename = f"{base_filename}.md"
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✓ Output guardado como Markdown: {filename}")
        
        if args.f:
            filename = f"{base_filename}.txt"
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✓ Output guardado como texto: {filename}")
        
        if args.c:
            code_blocks = self.extract_code_blocks(content)
            for i, (block_type, lang, code) in enumerate(code_blocks, 1):
                if block_type == 'code' and lang:
                    ext = {
                        'python': 'py',
                        'javascript': 'js',
                        'java': 'java',
                        'c': 'c',
                        'c++': 'cpp',
                        'go': 'go',
                        'ruby': 'rb',
                        'bash': 'sh',
                        'html': 'html',
                        'css': 'css',
                        'typescript': 'ts',
                        'php': 'php',
                        'rust': 'rs',
                        'swift': 'swift',
                        'kotlin': 'kt',
                        'sql': 'sql'
                    }.get(lang.lower(), 'txt')
                    
                    filename = f"{base_filename}_{i}.{ext}"
                    with open(filename, 'w') as f:
                        f.write(code)
                    print(f"✓ Código guardado como: {filename}")
        
        if args.gz or args.z:
            files_to_compress = []
            
            if args.m:
                files_to_compress.append(f"{base_filename}.md")
            if args.f:
                files_to_compress.append(f"{base_filename}.txt")
            if args.c:
                code_blocks = self.extract_code_blocks(content)
                for i, (block_type, lang, code) in enumerate(code_blocks, 1):
                    if block_type == 'code' and lang:
                        ext = {
                            'python': 'py',
                            'javascript': 'js',
                            'java': 'java',
                            'c': 'c',
                            'c++': 'cpp',
                            'go': 'go',
                            'ruby': 'rb',
                            'bash': 'sh',
                            'html': 'html',
                            'css': 'css'
                        }.get(lang.lower(), 'txt')
                        files_to_compress.append(f"{base_filename}_{i}.{ext}")
            
            if args.gz:
                tar_filename = f"{base_filename}.tar.gz"
                with tarfile.open(tar_filename, "w:gz") as tar:
                    for file in files_to_compress:
                        if os.path.exists(file):
                            tar.add(file)
                            os.remove(file)
                print(f"✓ Archivos comprimidos como: {tar_filename}")
            
            if args.z:
                zip_filename = f"{base_filename}.zip"
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for file in files_to_compress:
                        if os.path.exists(file):
                            zipf.write(file)
                            os.remove(file)
                print(f"✓ Archivos comprimidos como: {zip_filename}")

def show_manual():
    manual = """
DEEPSEEK CLI CHAT TOOL - MANUAL

Uso básico:
  seek -i "tu consulta" [opciones]
  seek config [opciones]

Comandos principales:
  config          Configura tu API key y preferencias
  chat           Modo interactivo de chat

Opciones de consulta:
  -i, --input     Texto de entrada para DeepSeek (requerido)
  -t, --terminal  Mostrar output en terminal
  -o, --output    Guardar output en archivo(s)
  -n, --name      Nombre base para los archivos de salida
  
Opciones de output (requieren -o):
  -m, --markdown  Guardar como archivo markdown
  -f, --file      Guardar como archivo de texto
  -c, --code      Extraer bloques de código a archivos
  
Opciones de compresión (requieren -o):
  -gz             Comprimir output como tar.gz
  -z, --zip       Comprimir output como zip

Ayuda:
  --help, -h      Mostrar este mensaje
  man             Mostrar manual extendido

Ejemplos:
  seek -i "Explica los decoradores en Python" -t
  seek -i "Ejemplo de API REST en Flask" -o -m -c -n mi_api
  seek config --api-key tu_api_key --model deepseek-coder
    """
    print(manual)

def show_extended_manual():
    extended_manual = """
DEEPSEEK CLI CHAT TOOL - MANUAL EXTENDIDO

CONFIGURACIÓN:
  La herramienta guarda la configuración en ~/.deepseek/seek.json
  Para configurar:
    1. seek config --api-key tu_api_key
    2. Opcionalmente configura modelo y parámetros:
       seek config --model deepseek-coder --temperature 0.5

ARCHIVO DE CONFIGURACIÓN:
  Ubicación: ~/.deepseek/seek.json
  Contenido típico:
    {
        "api_key": "tu_api_key",
        "default_model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2000
    }

MODELOS DISPONIBLES:
  - deepseek-chat (predeterminado)
  - deepseek-coder (para código)
  - deepseek-math (para matemáticas)

OPCIONES DE OUTPUT:
  - Los nombres de archivo incluyen timestamp por defecto
  - Usa -n para especificar un nombre personalizado
  - La extracción de código reconoce +15 lenguajes

COMPRESIÓN:
  - Las opciones -gz y -z eliminan los archivos originales
  - Se comprimen todos los archivos generados

MODO INTERACTIVO:
  Usa 'seek chat' para iniciar una sesión interactiva
  Comandos especiales en modo interactivo:
    /save - Guardar la conversación
    /exit - Salir
    /reset - Reiniciar conversación

EJEMPLOS AVANZADOS:
  1. Consulta con configuración específica:
     seek -i "Optimiza este código Python" --model deepseek-coder -t

  2. Generar documentación técnica:
     seek -i "Genera documentación Markdown para una API REST" -o -m -n docs

  3. Proyecto completo con compresión:
     seek -i "Crea un CRUD en Flask con MongoDB" -o -m -c -z
    """
    print(extended_manual)

def handle_config_command(args, config):
    """Maneja el comando de configuración"""
    if args.api_key:
        config.config["api_key"] = args.api_key
    if args.model:
        config.config["default_model"] = args.model
    if args.temperature is not None:
        config.config["temperature"] = args.temperature
    if args.max_tokens:
        config.config["max_tokens"] = args.max_tokens
    
    config.save_config()
    print("✓ Configuración actualizada:")
    print(json.dumps(config.config, indent=2))

def interactive_chat(config):
    """Modo interactivo de chat"""
    print("\nDeepSeek Chat Interactivo (escribe /exit para salir)\n")
    seek = DeepSeekCLI(config)
    conversation = []
    
    while True:
        try:
            user_input = input("Tú: ")
            
            if user_input.lower() == '/exit':
                break
            if user_input.lower() == '/reset':
                conversation = []
                print("Conversación reiniciada")
                continue
            if user_input.lower() == '/save':
                filename = f"deepseek_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    for msg in conversation:
                        f.write(f"{msg['role'].capitalize()}: {msg['content']}\n\n")
                print(f"✓ Conversación guardada como {filename}")
                continue
            
            conversation.append({"role": "user", "content": user_input})
            
            print("\nDeepSeek: ", end="", flush=True)
            response = seek.get_response(user_input)
            print(response + "\n")
            
            conversation.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\nUsa /exit para salir o continúa escribiendo")
            continue

def main():
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        show_manual()
        sys.exit(0)
    
    if 'man' in sys.argv:
        show_extended_manual()
        sys.exit(0)
    
    config = DeepSeekConfig()
    
    # Subcomando: config
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        parser = argparse.ArgumentParser(description='Configura DeepSeek CLI')
        parser.add_argument('config', nargs='?', help='Configurar la CLI')
        parser.add_argument('--api-key', help='Establece tu API key')
        parser.add_argument('--model', help='Modelo predeterminado (deepseek-chat, deepseek-coder, etc.)')
        parser.add_argument('--temperature', type=float, help='Creatividad (0.0 a 1.0)')
        parser.add_argument('--max-tokens', type=int, help='Longitud máxima de respuesta')
        args = parser.parse_args()
        handle_config_command(args, config)
        sys.exit(0)
    
    # Subcomando: chat
    if len(sys.argv) > 1 and sys.argv[1] == 'chat':
        interactive_chat(config)
        sys.exit(0)
    
    # Comando principal
    parser = argparse.ArgumentParser(description='DeepSeek CLI Chat Tool', add_help=False)
    parser.add_argument('-i', '--input', help='Input text for DeepSeek')
    parser.add_argument('-t', '--terminal', action='store_true', help='Display output in terminal')
    parser.add_argument('-o', '--output', action='store_true', help='Save output to file(s)')
    parser.add_argument('-n', '--name', help='Base name for output files')
    parser.add_argument('-m', '--markdown', action='store_true', help='Save as markdown (requires -o)')
    parser.add_argument('-f', '--file', action='store_true', help='Save as text file (requires -o)')
    parser.add_argument('-c', '--code', action='store_true', help='Extract code blocks to files (requires -o)')
    parser.add_argument('-gz', action='store_true', help='Compress output as tar.gz (requires -o)')
    parser.add_argument('-z', '--zip', action='store_true', help='Compress output as zip (requires -o)')
    
    try:
        args = parser.parse_args()
    except:
        show_manual()
        sys.exit(1)
    
    if not args.input:
        print("Error: Se requiere texto de entrada (-i)")
        show_manual()
        sys.exit(1)
    
    args.output_name = args.name
    seek = DeepSeekCLI(config)
    response = seek.get_response(args.input)
    
    if args.terminal:
        print("\nDeepSeek Response:\n")
        print(response)
    
    if args.output:
        if not any([args.markdown, args.file, args.code]):
            print("Advertencia: No se especificó formato de salida con -o (usa -m, -f, o -c)")
        seek.save_output(response, args)

if __name__ == "__main__":
    main()
