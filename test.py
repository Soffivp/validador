import re

class ValidadorSimple:
    def __init__(self):
        # Definimos los patrones y estructuras propios de Shoppy
        self.tokens = {
            'tipos': r'\b(cadena|ent|dec|boolean)\b',
            'control': r'\b(para|mientras|si|contrario|init|decir)\b',
            'operadores': r'(<=|>=|==|!=|&&|\|\||[+\-*/=<>!]|\+\+|--)',
            'delimitadores': r'[{}()\[\];]',
            'identificadores': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
            'numeros': r'\b\d+(\.\d+)?\b',
            'cadenas': r'"[^"]*"',
            'comentarios': r'_.*',
            'booleanos': r'\b(true|false)\b'
        }

        #crea un patron con el nombre y los elementos de los tokens
        # | hace que al conbinar los patrones puedan coincidir entre si
        self.patron_completo = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.tokens.items())
        self.regex = re.compile(self.patron_completo)
        self.pila_delimitadores = []  # Mover la pila en cada interaccion

    def tokenizar(self, linea):
        # obtiene los tokens
        tokens = []
        #busca las coincidencias en las lineas de codigo
        for match in self.regex.finditer(linea):
            #match itera los objetos y guarda el nombre del ultimo grupo
            tipo = match.lastgroup
            #guarda el valor de los grupos
            valor = match.group()
            if tipo not in ['comentarios']:  # Ignorar comentarios para análisis
                #Crea un diccionario con la información del token
                #guarda el tipo de token y el valor en una lista
                tokens.append({'tipo': tipo, 'valor': valor})
        return tokens

    def validar_balance(self, tokens):
        #Verifica balance de delimitadores usando la pila de instancia
        pares = {'(': ')', '[': ']', '{': '}'}

        for token in tokens:
            if token['tipo'] == 'delimitadores':
                valor = token['valor']
                if valor in pares:
                    self.pila_delimitadores.append(valor)
                elif valor in pares.values():
                    if not self.pila_delimitadores or pares[self.pila_delimitadores.pop()] != valor:
                        return f"Delimitadores mal emparejados: {valor}"
        return None

    def validar_sintaxis(self, tokens):
        #Validaciones sintácticas básicas
        errores = []

        for i, token in enumerate(tokens):
            # Tipo seguido de identificador
            if token['tipo'] == 'tipos' and i + 1 < len(tokens):
                if tokens[i + 1]['tipo'] != 'identificadores':
                    errores.append(f"Falta identificador después de '{token['valor']}'")

            # Asignación precedida por identificador
            if token['valor'] == '=' and (i == 0 or tokens[i-1]['tipo'] != 'identificadores'):
                errores.append("Asignación debe ir precedida por identificador")

        return errores

    def analizar_linea(self, linea, num_linea):
        #Analiza una línea completa
        linea_original = linea.strip()
        if not linea_original:
            return {'linea': num_linea, 'contenido': '', 'valida': True, 'tokens': [], 'errores': []}

        tokens = self.tokenizar(linea_original)
        errores = []

        # Validar sintaxis
        errores.extend(self.validar_sintaxis(tokens))

        return {
            'linea': num_linea,
            'contenido': linea_original,
            'valida': len(errores) == 0,
            'tokens': tokens,
            'errores': errores
        }

    def procesar_archivo(self, archivo):
        #Procesa archivo completo con validación de delimitadores global
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
        except FileNotFoundError:
            print(f"Archivo '{archivo}' no encontrado")
            return []
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            return []

        resultados = []
        self.pila_delimitadores = []  # Reiniciar pila para cada archivo
        print(f"\n--- ANALIZANDO: {archivo} ---\n")

        # Primera pasada: procesar todas las líneas y tokens
        for i, linea in enumerate(lineas, 1):
            resultado = self.analizar_linea(linea, i)
            resultados.append(resultado)

            # Validar delimitadores (acumulativo)
            self.validar_balance(resultado['tokens'])

        # Segunda pasada: mostrar resultados con balance global
        for i, resultado in enumerate(resultados, 1):
            # Mostrar resultado
            estado = "✓" if resultado['valida'] and not self.pila_delimitadores else "✗"
            print(f"Línea {i:2d}: {estado} {resultado['contenido']}")

            # Mostrar errores
            for error in resultado['errores']:
                print(f"        Error: {error}")

            # Mostrar tokens (opcional)
            if resultado['tokens'] and len(resultado['tokens']) > 0:
                tokens_str = ', '.join([f"{t['valor']}" for t in resultado['tokens']])
                print(f"        Tokens: {tokens_str}")
            print()

        # Verificar balance final
        if self.pila_delimitadores:
            print(f"--- ERROR: Delimitadores sin cerrar: {', '.join(self.pila_delimitadores)} ---")

        return resultados

def main():
    validador = ValidadorSimple()
    archivo = "prueba.txt"
    print("--- VALIDADOR DE LENGUAJE SHOPPY ---")
    #print(f"Analizando archivo: {archivo}")
    resultados = validador.procesar_archivo(archivo)

if __name__ == "__main__":
    main()