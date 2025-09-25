# Nome do Arquivo: ce70b1cd_image_detection.py
# Descrição: Contém funções para detecção de imagem (template matching) em screenshots.
# Versão: 01.00.03 -> Inclusão do ID da célula no nome do arquivo e descrição das alterações no campo Versão.
# Analista: Gemini
# Programador: Gled Carneiro
# -----------------------------------------------------------------------------
import cv2
import numpy as np

# Função para encontrar a posição de uma imagem na tela (lógica de detecção de imagem)
def find_image_on_screen(screenshot_path, template_path):
    """
    Encontra a posição de uma imagem (template) dentro de outra imagem (screenshot).

    Args:
        screenshot_path (str): Caminho para o arquivo da screenshot.
        template_path (str): Caminho para o arquivo da imagem a ser detectada (template).

    Returns:
        tuple: Uma tupla (x, y, w, h) representando a posição e dimensões da imagem encontrada,
               ou None se a imagem não for encontrada.
    """
    try:
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)

        if screenshot is None:
            print(f"Erro: Não foi possível carregar a screenshot de {screenshot_path}")
            return None
        if template is None:
            print(f"Erro: Não foi possível carregar o template de {template_path}")
            return None

        # Converta as imagens para tons de cinza
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Realiza o template matching
        # cv2.TM_CCOEFF_NORMED é um método de comparação que funciona bem na maioria dos casos
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # Encontra a localização do melhor resultado
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Define um limiar para considerar a correspondência como válida.
        # Você pode precisar ajustar este valor dependendo das suas imagens.
        threshold = 0.8

        if max_val >= threshold:
            # Pega as dimensões do template
            w, h = template_gray.shape[::-1]
            # Pega as coordenadas do canto superior esquerdo
            top_left = max_loc
            # Calcula as coordenadas do canto inferior direito
            bottom_right = (top_left[0] + w, top_left[1] + h)

            # print(f"Imagem encontrada em: {top_left} a {bottom_right}")
            return (top_left[0], top_left[1], w, h)
        else:
            # print("Imagem não encontrada na screenshot.") # Comentado para evitar muita verbosidade em loops de tentativa
            return None

    except Exception as e:
        print(f"Ocorreu um erro durante a detecção da imagem: {e}")
        return None

# Removido o exemplo de uso direto que não faz parte do fluxo principal
# screenshot_file = "screenshot.png"
# template_file = "template.png"
# image_position = find_image_on_screen(screenshot_file, template_file)
# if image_position:
#     x, y, w, h = image_position
#     print(f"Coordenadas da imagem detectada (canto superior esquerdo): ({x}, {y})")
#     print(f"Centro da imagem: ({x + w // 2}, {y + h // 2})")