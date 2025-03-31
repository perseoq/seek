# Seek | DeepSeek CLI (No oficial) 
## Características principales:

1. **Sistema de configuración**:
   - Lee y escribe en `~/.deepseek/seek.json`
   - Almacena API key, modelo predeterminado y parámetros de generación
   - Comando `seek config` para configuración inicial

2. **Nuevos comandos**:
   - `seek config --api-key tu_key`: Configura la API key
   - `seek chat`: Modo interactivo de chat
   - `seek man`: Manual extendido

3. **Mejoras en output**:
   - Opción `-n` para nombres personalizados de archivos
   - Soporte para más lenguajes de programación
   - Mejores mensajes de confirmación

4. **Modo interactivo**:
   - Chat continuo con historial
   - Comandos especiales (/save, /exit, /reset)

## Cómo usar:

1. **Primera configuración**:
   ```bash
   mkdir -p ~/.deepseek
   seek config --api-key tu_api_key_deepseek
   ```

2. **Ejemplos de uso**:
   ```bash
   # Consulta simple
   seek -i "Cómo funciona Python async?" -t
   
   # Generar código con nombre personalizado
   seek -i "Script Python para análisis de datos" -o -c -n analisis_datos
   
   # Modo interactivo
   seek chat
   
   # Configurar modelo específico
   seek config --model deepseek-coder
   ```

3. **Estructura del archivo de configuración**:
   ```json
   {
       "api_key": "tu_api_key",
       "default_model": "deepseek-chat",
       "temperature": 0.7,
       "max_tokens": 2000
   }
   ```

