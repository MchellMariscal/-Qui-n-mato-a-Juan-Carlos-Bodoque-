import pygame
import random
import textwrap
import sys
import math
import os
from collections import deque

pygame.init()
# -------------------------
# Configuración
# -------------------------
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quien mato a Bodoque")
CLOCK = pygame.time.Clock()
FPS = 60

# Fuentes
try:
    font_path = "Bungee-Regular.ttf" # Si está en la misma carpeta

    FONT_BIG = pygame.font.Font(font_path, 40)
    FONT_MED = pygame.font.Font(font_path, 20)
    FONT_SM = pygame.font.Font(font_path, 15)
    FONT_XS = pygame.font.Font(font_path, 13)

except pygame.error as e:
    print(f"Error al cargar la fuente '{font_path}': {e}. Usando fuente por defecto.")
    FONT_BIG = pygame.font.Font(None, 70)
    FONT_MED = pygame.font.Font(None, 28)
    FONT_SM = pygame.font.Font(None, 22)
    FONT_XS = pygame.font.Font(None, 18)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo de fuente '{font_path}'. Usando fuente por defecto.")
    FONT_BIG = pygame.font.Font(None, 40)
    FONT_MED = pygame.font.Font(None, 28)
    FONT_SM = pygame.font.Font(None, 22)
    FONT_XS = pygame.font.Font(None, 18)


# -------------------------
# --- Cargar Imágenes de Fondo y Convertir a Escala de Grises ---
# -------------------------
def convert_to_grayscale(surface):
    grayscale_surface = pygame.Surface(surface.get_size(), 0, 32).convert_alpha()
    grayscale_surface.blit(surface, (0, 0))

    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            r, g, b, a = surface.get_at((x, y))
            gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
            grayscale_surface.set_at((x, y), (gray, gray, gray, a))
    return grayscale_surface

# Imagen para la pantalla de INTRODUCCIÓN
try:
    image_path_intro = os.path.join("Imagenes", "fondo.png")
    fondo_original_intro = pygame.image.load(image_path_intro).convert_alpha()
    FONDO_INTRO = pygame.transform.scale(fondo_original_intro, (WIDTH, HEIGHT))
    # FONDO_INTRO = convert_to_grayscale(FONDO_INTRO) # Descomenta para grises
except pygame.error as e:
    print(f"Error al cargar la imagen '{image_path_intro}': {e}")
    FONDO_INTRO = pygame.Surface((WIDTH, HEIGHT)); FONDO_INTRO.fill((46, 46, 46))
except FileNotFoundError as e:
    print(f"Error: No se encontró '{image_path_intro}'. {e}")
    FONDO_INTRO = pygame.Surface((WIDTH, HEIGHT)); FONDO_INTRO.fill((46, 46, 46))

# Imagen para el MENÚ PRINCIPAL
try:
    image_path_menu = os.path.join("Imagenes", "bodoque.jpg")
    fondo_original_menu = pygame.image.load(image_path_menu).convert_alpha()
    FONDO_MENU = pygame.transform.scale(fondo_original_menu, (WIDTH, HEIGHT))
    # FONDO_MENU = convert_to_grayscale(FONDO_MENU) # Descomenta para grises
except pygame.error as e:
    print(f"Error al cargar la imagen '{image_path_menu}': {e}")
    FONDO_MENU = pygame.Surface((WIDTH, HEIGHT)); FONDO_MENU.fill((46, 46, 46))
except FileNotFoundError as e:
    print(f"Error: No se encontró '{image_path_menu}'. {e}")
    FONDO_MENU = pygame.Surface((WIDTH, HEIGHT)); FONDO_MENU.fill((46, 46, 46))

# -------------------------
# --- Paleta de Colores (Fondo Oscuro, Elementos Claros) ---
# -------------------------
BG = (46, 46, 46)             # 6 Gris grafito (#2E2E2E) - Fondo principal (oscuro)
PANEL = (74, 74, 74)          # 5 Gris oscuro (#4A4A4A) - Paneles (ligeramente más claro)
CARD = (128, 128, 128)        # 4 Gris acero (#808080) - Botones secundarios, tarjetas (más claro)
ACCENT = (224, 224, 224)      # 2 Gris claro (#E0E0E0) - Acentos, botones activos (claro)
ACCENT_HOVER = (245, 245, 245) # 1 Gris muy claro (#F5F5F5) - Hover (muy claro)
OK = (224, 224, 224)          # 2 Gris claro (#E0E0E0) - Botones OK/Comenzar (claro)
BAD = (176, 176, 176)         # 3 Gris medio (#B0B0B0) - Botones Fallo/Acusar (distinto de OK, más claro que Card)
TEXT = (255, 255, 255)        # 0 Blanco puro (#FFFFFF) - Texto principal (muy claro)
MUTED = (176, 176, 176)       # 3 Gris medio (#B0B0B0) - Texto secundario (más claro)
SHADOW = (0, 0, 0)            # 7 Negro puro (#000000) - Sombras, texto sobre muy claro
NEGRO_PURO = (0, 0, 0)        # 7 Negro puro (#000000)
DARK_GREY = PANEL


# -------------------------
# Datos del juego
# -------------------------
PERSONAJES = [
    "Tulio Triviño", # El jugador
    "Juanín Juan Harry",
    "Policarpo Avendaño",
    "Patana Tufillo",
    "Mario Hugo",
    "Mico el Micrófono"
]

SOSPECHOSOS = [p for p in PERSONAJES if p != "Tulio Triviño"] # Lista sin el jugador

LOCACIONES = [
    "Estudio Principal",
    "Sala de Guiones",
    "Cuarto de Iluminación",
    "Bodega de Utilería",
    "Set de Entrevistas"
]

ARMAS = [
    "Micrófono de Hierro",
    "Cable Eléctrico Pelado",
    "Estatua del Topo Gigio",
    "Guión Envenenado",
    "Tijeras de Escenografía"
]

CASOS = [
    {
    "nombre": "La Transmisión Final",
    "culpable": "Policarpo Avendaño",
    "arma": "Micrófono de Hierro",
    "locacion": "Estudio Principal",
    "motivo": (
        "Durante años, Policarpo soportó las burlas y humillaciones de Bodoque, "
        "quien lo veía como un presentador anticuado y prescindible. Aquella noche, "
        "la tensión entre ambos alcanzó su punto más alto durante una grabación en vivo. "
        "Bodoque, entre risas, improvisó un comentario sarcástico sobre la carrera de Policarpo. "
        "La rabia reprimida explotó: tomó el micrófono de hierro y lo golpeó con toda su fuerza. "
        "El ruido del impacto se confundió con el eco de la lluvia sobre el techo del canal. "
        "Minutos después, Policarpo intentó borrar su culpa limpiando las manchas, "
        "pero el remordimiento no se borra tan fácil como la sangre."
    ),
    "pista_clave": (
        "El estudio aún huele a ozono y metal caliente. "
        "En el piso, cerca de la cámara principal, hay un rastro de marcas metálicas recientes. "
        "Un camarógrafo afirma haber visto a Policarpo limpiándose las manos con una cortina roja, "
        "nervioso, con la mirada perdida en el suelo. "
        "En la mesa de sonido hay un micrófono fuera de su soporte, "
        "como si alguien lo hubiese soltado con prisa justo después de un acto imperdonable."
    ),
    "pistas_falsas": {
        "Sala de Guiones": (
            "La habitación está cubierta de papeles arrugados y tazas de café vacías. "
            "Juanín, con ojeras y los ojos vidriosos, repasaba los horarios una y otra vez, "
            "murmurando: 'teníamos que corregirlo, debimos hacerlo antes'. "
            "Su ansiedad es palpable, pero sus manos temblorosas no parecen las de un asesino."
        ),
        "Cuarto de Iluminación": (
            "El olor a polvo y electricidad quemada impregna el aire. "
            "Mico, con un destornillador entre los dedos, ajusta los focos con precisión enfermiza. "
            "Dice que 'todo estaba bajo control', aunque su voz suena más a justificación que a certeza. "
            "Un foco parpadea y, por un instante, su sombra parece sonreír sola."
        ),
        "Bodega de Utilería": (
            "Entre cajas viejas y disfraces olvidados, el silencio es casi sepulcral. "
            "Mario Hugo carga materiales con torpeza, evitando tu mirada. "
            "En el suelo hay un guante blanco, ligeramente húmedo, "
            "como si alguien lo hubiera dejado caer en plena huida. "
            "El aire aquí está cargado de polvo y culpa."
        ),
        "Set de Entrevistas": (
            "El set está a oscuras, salvo por una lámpara encendida al fondo. "
            "Patana sostiene su libreta con fuerza, los nudillos tensos. "
            "Dice que buscaba silencio, pero su voz tiembla al pronunciar el nombre de Bodoque. "
            "En la silla de entrevistas, aún se distingue la huella de alguien que se sentó hace poco. "
            "El ambiente se siente tenso, como si la escena misma recordara lo ocurrido."
        )
    }
}
]

# ... (código previo) ...

# -------------------------
# --- Datos de Sospechosos y Rutas de Imagen ---
# -------------------------
SUSPECT_DATA = {
    "Juanín Juan Harry": {
        "cargo": "Productor Ejecutivo del Noticiero 31 Minutos",
        "edad": "38 años",
        "personalidad": "Ansioso, perfeccionista, emocionalmente frágil.",
        "relacion": "Bodoque lo trataba con condescendencia, burlándose de sus nervios. Lo llamaba 'ratón de oficina'.",
        "motivo_posible": "Bodoque descubrió desvíos de dinero en los presupuestos de producción que Juanín había realizado. La confrontación pudo haber escalado.",
        "comportamiento": ["Fue visto en la Bodega de Utilería, manipulando cajas.", "Evitó mantener contacto visual en interrogatorios.", "Repite constantemente que 'todo fue un accidente'."],
        "analisis_detective": "Juanín nunca quiso hacer daño, pero los hombres bajo presión toman decisiones desesperadas. Su miedo a fallar pudo convertirlo en un asesino por accidente.",
        "imagen": "Juanin_Juan_Harry.jpeg" 
    },
    "Policarpo Avendaño": {
        "cargo": "Conductor de la sección de espectáculos",
        "edad": "45 años",
        "personalidad": "Arrogante, competitivo, egocéntrico.",
        "relacion": "Rivalidad directa. Policarpo y Bodoque competían constantemente por protagonismo y reconocimiento.",
        "motivo_posible": "Orgullo herido. Bodoque se burló públicamente de un reportaje de Policarpo la noche anterior, provocando una fuerte discusión.",
        "comportamiento": ["Visto en el Estudio Principal limpiando algo con un paño., Respuestas ensayadas en interrogatorios.", "Ha intentado culpar a Mario Hugo."],
        "analisis_detective": "Policarpo mata con palabras… pero quizá, por primera vez, usó algo más pesado que un insulto. El orgullo es un veneno lento, pero mortal.",
        "imagen": "Policarpo_Avendano.jpeg" 
    },
    "Patana Tufillo": {
        "cargo": "Reportera en prácticas",
        "edad": "24 años",
        "personalidad": "Brillante, idealista, con carácter fuerte.",
        "relacion": "Mentora forzada. Bodoque la trataba con desprecio y sarcasmo, ridiculizando sus notas ecológicas en televisión.",
        "motivo_posible": "Venganza profesional. Bodoque arruinó su reportaje sobre contaminación, manipulando el guion sin su permiso.",
        "comportamiento": ["Vista en la Sala de Guiones, manipulando documentos.", "Declaró haber estado 'revisando correcciones'.", "Un técnico la vio colocando algo sobre la taza de Bodoque."],
        "analisis_detective": "Su mente es aguda como una pluma, pero el resentimiento la ha convertido en cuchilla. Patana no busca justicia, busca ser recordada.",
        "imagen": "Patana_Tufillo.jpg" 
    },
    "Mario Hugo": {
        "cargo": "Reportero de sociedad y farándula",
        "edad": "33 años",
        "personalidad": "Ingenuo, sentimental, profundamente emocional.",
        "relacion": "Lo consideraba un amigo, aunque con miedo. Bodoque se aprovechaba de su inocencia para ridiculizarlo frente al público.",
        "motivo_posible": "Humillación y ruptura emocional. Bodoque hizo pública su vida amorosa en un episodio en vivo.",
        "comportamiento": ["Visto en el Set de Entrevistas, sosteniendo una Estatua del Topo Gigio.", "Lloró durante el interrogatorio.", "Se contradijo en su paradero durante el apagón."],
        "analisis_detective": "Mario es incapaz de planear un asesinato… pero la rabia del corazón traicionado no se planea, solo estalla.",
        "imagen": "Mario_Hugo.jpg" 
    },
    "Mico el Micrófono": {
        "cargo": "Técnico de sonido e iluminación",
        "edad": "41 años",
        "personalidad": "Reservado, obsesivo, extremadamente metódico.",
        "relacion": "Bodoque sabía que Mico había manipulado transmisiones y lo chantajeaba para obtener silencio y favores.",
        "motivo_posible": "Silenciar la amenaza. Bodoque amenazó con exponerlo ante la dirección del canal.",
        "comportamiento": ["Visto en el Cuarto de Iluminación manipulando cables.", "Declaró que 'todo estaba bajo control' segundos antes del apagón.", "Evitó cooperar en el interrogatorio técnico."],
        "analisis_detective": "Mico sabe cómo cortar el sonido… y cómo cortar una vida sin que nadie oiga el grito.",
        "imagen": "Mico_el_Microfono.jpeg" 
    }
}
# ... (código para cargar imágenes de sospechosos - sigue igual) ...

# Cargar imágenes de sospechosos
SUSPECT_IMAGES = {}
for name, data in SUSPECT_DATA.items():
    try:
        img_path = os.path.join("Imagenes", data["imagen"])
        original_img = pygame.image.load(img_path).convert_alpha()
        scaled_img = pygame.transform.scale(original_img, (150, 150)) # Tamaño de imagen para el detalle
        # scaled_img = convert_to_grayscale(scaled_img) # Descomenta para grises
        SUSPECT_IMAGES[name] = scaled_img
    except Exception as e:
        print(f"Error al cargar imagen para {name} desde '{img_path}': {e}")
        SUSPECT_IMAGES[name] = None


# -------------------------
# --- Cargar Imágenes de Locaciones y Logo ---
# -------------------------
LOCATION_IMAGES_FILES = {
    "Estudio Principal": "estudio.jpg",
    "Sala de Guiones": "guiones.jpg",
    "Cuarto de Iluminación": "iluminacion.jpg",
    "Bodega de Utilería": "utileria.png",
    "Set de Entrevistas": "entrevistas.png"
}

LOCATION_IMAGES = {}
LOCATION_IMAGE_SIZE = (WIDTH // 3, HEIGHT // 4)

for name, filename in LOCATION_IMAGES_FILES.items():
    try:
        img_path = os.path.join("Imagenes", filename)
        original_img = pygame.image.load(img_path).convert_alpha()
        scaled_img = pygame.transform.scale(original_img, LOCATION_IMAGE_SIZE)
        # scaled_img = convert_to_grayscale(scaled_img) # Descomenta para grises
        LOCATION_IMAGES[name] = scaled_img
    except Exception as e:
        print(f"Error al cargar imagen para locación {name} desde '{img_path}': {e}")
        LOCATION_IMAGES[name] = None

# Cargar Logo (para el panel derecho por defecto)
try:
    logo_path = os.path.join("Imagenes", "logo.png")
    LOGO_IMG = pygame.image.load(logo_path).convert_alpha()
    LOGO_IMG = pygame.transform.scale(LOGO_IMG, (600, 500))
except Exception as e:
    print(f"Error al cargar logo.png: {e}")
    LOGO_IMG = None


# -------------------------
# Estructura del "tablero"
# -------------------------
ROOM_LABELS = {
    "Estudio Principal": ["Estudio", "Principal"],
    "Sala de Guiones": ["Sala de", "Guiones"],
    "Cuarto de Iluminación": ["Cuarto de", "Iluminación"],
    "Bodega de Utilería": ["Bodega de", "Utilería"],
    "Set de Entrevistas": ["Set de", "Entrevistas"]
}
ROOM_POS_PERCENT = {
    "Estudio Principal":      (0.5, 0.5),
    "Sala de Guiones":        (0.5, 0.2),
    "Cuarto de Iluminación": (0.2, 0.5),
    "Bodega de Utilería":     (0.5, 0.8),
    "Set de Entrevistas":     (0.8, 0.5)
}
ROOM_RADIUS = 65
ROOM_EDGES = [
    ("Estudio Principal", "Sala de Guiones"), ("Estudio Principal", "Cuarto de Iluminación"),
    ("Estudio Principal", "Bodega de Utilería"), ("Estudio Principal", "Set de Entrevistas"),
    ("Sala de Guiones", "Set de Entrevistas"), ("Set de Entrevistas", "Bodega de Utilería"),
    ("Bodega de Utilería", "Cuarto de Iluminación"), ("Cuarto de Iluminación", "Sala de Guiones")
]

SECRET_CASE = random.choice(CASOS)
SOLUTION = {
    'culpable': SECRET_CASE['culpable'], 'arma': SECRET_CASE['arma'], 'locacion': SECRET_CASE['locacion']
}

# -------------------------
# Estado del juego
# -------------------------
state = {
    'screen': 'main_menu',
    'story_page': 1,
    'turns': 5,
    'evidence': [],
    'investigated': set(),
    'selected_room': None,
    'selected_suspect': None,
    'accuse_choice': {'person': None, 'weapon': None, 'room': None},
    'result': None,
    # === MODIFICACIÓN CLAVE 1: Inicializa 'show_map' a False para mostrar el logo ===
    'show_map': False 
}


# -------------------------
# Utilities UI
# -------------------------
def draw_text(surf, text, pos, font=FONT_MED, color=TEXT, center=False, v_center=False, right=False):
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center: rect.centerx = pos[0]
    elif right: rect.right = pos[0]
    else: rect.x = pos[0]
    
    if v_center: rect.centery = pos[1]
    else: rect.y = pos[1]
    
    if center and v_center: rect.center = pos
    
    surf.blit(txt, rect)
    return rect

def rounded_rect(surface, rect, color, radius=10):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def screen_base(title):
    # Dibuja el fondo de pantalla
    SCREEN.fill(BG)
    
    # Dibuja la barra superior/cabecera
    header_rect = pygame.Rect(0, 0, WIDTH, 50)
    pygame.draw.rect(SCREEN, DARK_GREY, header_rect)
    
    # Dibuja el título de la pantalla
    draw_text(SCREEN, title, (WIDTH // 2, 25), FONT_MED, ACCENT, center=True, v_center=True)
    
    # Dibuja el contador de turnos (asume que existe una variable global 'state')
    draw_text(SCREEN, f"Turnos restantes: {state['turns']}", (WIDTH - 10, 25), FONT_MED, TEXT, right=True, v_center=True)

def draw_shadowed_panel(surface, rect, color=PANEL, shadow_offset=6):
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    rounded_rect(surface, shadow_rect, SHADOW)
    rounded_rect(surface, rect, color, radius=10)

def wrap_para(text, width, font):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = cur + (' ' if cur else '') + w
        if font.size(test)[0] > width:
            lines.append(cur); cur = w
        else: cur = test
    if cur: lines.append(cur)
    return lines

# -------------------------
# Draw screens
# -------------------------
def screen_main_menu():
    SCREEN.blit(FONDO_MENU, (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(180); overlay.fill(BG); SCREEN.blit(overlay, (0, 0))
    draw_text(SCREEN, "¿QUIÉN MATÓ A JUAN CARLOS BODOQUE?", (WIDTH // 2, HEIGHT // 3), FONT_BIG, TEXT, center=True)
    btn_rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2, 280, 64); rounded_rect(SCREEN, btn_rect, OK)
    draw_text(SCREEN, "COMENZAR", btn_rect.center, FONT_MED, color=SHADOW, center=True, v_center=True)
    draw_text(SCREEN, "Presiona ESC para salir.", (WIDTH // 2, HEIGHT - 40), FONT_XS, MUTED, center=True)
    return btn_rect
def screen_story_page1():
    SCREEN.blit(FONDO_INTRO, (0, 0))
    draw_text(SCREEN, "LA HISTORIA HASTA AHORA...", (WIDTH // 2, 60), FONT_BIG, ACCENT, center=True)
    desc = (
        "Eres Tulio Triviño, el famoso presentador de 31 Minutos. "
        "Una violenta tormenta ha dejado al canal completamente incomunicado:"
        "las puertas están selladas, las luces parpadean y el sonido de la lluvia retumba en los pasillos vacíos."
        "En medio del apagón, alguien grita. Juan Carlos Bodoque ha sido hallado muerto en el estudio principal."
    )
    lines = wrap_para(desc, WIDTH - 120, FONT_MED)
    y = 180
    for ln in lines:
        draw_text(SCREEN, ln, (WIDTH // 2, y), FONT_MED, TEXT, center=True)
        y += 28

    btn_rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT - 120, 280, 64)
    rounded_rect(SCREEN, btn_rect, OK)
    draw_text(SCREEN, "CONTINUAR", btn_rect.center, FONT_SM, color=SHADOW, center=True, v_center=True)
    return btn_rect


def screen_story_page2():
    SCREEN.blit(FONDO_INTRO, (0, 0))
    draw_text(SCREEN, "LA HISTORIA CONTINÚA...", (WIDTH // 2, 60), FONT_BIG, ACCENT, center=True)
    desc = (
        "Nadie pudo entrar ni salir desde que comenzó la tormenta... el asesino está entre ustedes."
        "Atrapado junto a tus compañeros, decides asumir el papel de detective improvisado."
        "Explora el canal, recolecta pistas y analiza las evidencias para descubrir quién mató a Bodoque, "
        "con qué arma y en qué lugar."
        "Pero cuidado, Tulio..."
    )
    lines = wrap_para(desc, WIDTH - 120, FONT_MED)
    y = 180
    for ln in lines:
        draw_text(SCREEN, ln, (WIDTH // 2, y), FONT_MED, TEXT, center=True)
        y += 28

    btn_rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT - 120, 280, 64)
    rounded_rect(SCREEN, btn_rect, OK)
    draw_text(SCREEN, "CONTINUAR", btn_rect.center, FONT_SM, color=SHADOW, center=True, v_center=True)
    return btn_rect


def screen_story_page3():
    SCREEN.blit(FONDO_INTRO, (0, 0))
    draw_text(SCREEN, "EL CASO COMIENZA...", (WIDTH // 2, 60), FONT_BIG, ACCENT, center=True)
    desc = (
        "Cada decisión te acerca a la verdad o a convertirte en la próxima víctima."
        "Afuera, la tormenta no cesa."
        "Dentro, alguien sonríe en la oscuridad."
    )
    lines = wrap_para(desc, WIDTH - 120, FONT_MED)
    y = 180
    for ln in lines:
        draw_text(SCREEN, ln, (WIDTH // 2, y), FONT_MED, TEXT, center=True)
        y += 28

    btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT - 120, 320, 64)
    rounded_rect(SCREEN, btn_rect, OK)
    draw_text(SCREEN, "COMENZAR INVESTIGACIÓN", btn_rect.center, FONT_SM, color=SHADOW, center=True, v_center=True)
    return btn_rect

def screen_intro():
    SCREEN.blit(FONDO_INTRO, (0, 0)) # Sin overlay
    draw_text(SCREEN, "LA HISTORIA HASTA AHORA...", (WIDTH // 2, 60), FONT_BIG, ACCENT, center=True)
    desc = ()
    lines = wrap_para(desc, WIDTH - 120, FONT_XS)
    y = 180
    for ln in lines: draw_text(SCREEN, ln, (WIDTH // 2, y), FONT_MED, TEXT, center=True); y += 28
    btn_rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT - 120, 280, 64); rounded_rect(SCREEN, btn_rect, OK)
    draw_text(SCREEN, "COMENZAR INVESTIGACIÓN", btn_rect.center, FONT_SM, color=SHADOW, center=True, v_center=True)
    draw_text(SCREEN, "Presiona ESC para salir.", (WIDTH // 2, HEIGHT - 40), FONT_XS, MUTED, center=True)
    return btn_rect

def screen_board(mouse_pos):
    SCREEN.fill(BG)
    left_panel_width = 240
    left = pygame.Rect(10, 10, left_panel_width, HEIGHT - 20)
    draw_shadowed_panel(SCREEN, left, color=PANEL)
    draw_text(SCREEN, "Menú del Caso", (left.x + 20, 26), FONT_MED, ACCENT)
    draw_text(SCREEN, f"Turnos restantes: {state['turns']}", (left.x + 20, 62), FONT_SM, TEXT)
    draw_text(SCREEN, "Acciones:", (left.x + 20, 100), FONT_SM, MUTED)
    btn_width, btn_y_start, btn_y_gap = left_panel_width - 40, 130, 50
    btn_invest = pygame.Rect(left.x + 20, btn_y_start, btn_width, 40); rounded_rect(SCREEN, btn_invest, ACCENT)
    draw_text(SCREEN, "Investigar locación", btn_invest.center, FONT_SM, SHADOW, center=True, v_center=True)
    btn_inv = pygame.Rect(left.x + 20, btn_y_start + btn_y_gap, btn_width, 40); rounded_rect(SCREEN, btn_inv, BAD)
    draw_text(SCREEN, "Ver inventario", btn_inv.center, FONT_SM, SHADOW, center=True, v_center=True)
    btn_suspects = pygame.Rect(left.x + 20, btn_y_start + 2*btn_y_gap, btn_width, 40); rounded_rect(SCREEN, btn_suspects, BAD)
    draw_text(SCREEN, "Ver Sospechosos", btn_suspects.center, FONT_SM, SHADOW, center=True, v_center=True)
    btn_acc = pygame.Rect(left.x + 20, btn_y_start + 3*btn_y_gap, btn_width, 40); rounded_rect(SCREEN, btn_acc, BAD)
    draw_text(SCREEN, "Hacer acusación", btn_acc.center, FONT_SM, SHADOW, center=True, v_center=True)
    
    # Se añade la indicación de que se debe hacer clic en "Investigar locación" para ver el mapa
    draw_text(SCREEN, "", (left.x + 20, btn_y_start + 4*btn_y_gap + 10), FONT_XS, MUTED)
    
    map_x_start = left.right + 10
    map_rect = pygame.Rect(map_x_start, 10, WIDTH - map_x_start - 10, HEIGHT - 20)
    draw_shadowed_panel(SCREEN, map_rect, color=PANEL)
    absolute_room_pos = {}
    hover_room = None
    
    # Lógica de dibujo del mapa o el logo
    if state.get("show_map", True):
        draw_text(SCREEN, "Mapa del Set", (map_rect.x + 16, map_rect.y + 10), FONT_MED, ACCENT)
        for name, (rel_x, rel_y) in ROOM_POS_PERCENT.items():
            padding_x, padding_y = 40, 30
            panel_w_padded, panel_h_padded = map_rect.width - (padding_x * 2), map_rect.height - (padding_y * 2)
            abs_x = map_rect.x + padding_x + (panel_w_padded * rel_x); abs_y = map_rect.y + padding_y + (panel_h_padded * rel_y)
            absolute_room_pos[name] = (abs_x, abs_y)
        for a,b in ROOM_EDGES:
            ax, ay = absolute_room_pos[a]; bx, by = absolute_room_pos[b]
            pygame.draw.line(SCREEN, MUTED, (ax, ay), (bx, by), 3)
        
        for name, pos in absolute_room_pos.items():
            x,y = pos; r = ROOM_RADIUS; dist = math.hypot(mouse_pos[0]-x, mouse_pos[1]-y); hovered = dist <= r
            color = ACCENT if name not in state['investigated'] else CARD
            if hovered: color = ACCENT_HOVER; hover_room = name
            pygame.draw.circle(SCREEN, color, (int(x), int(y)), r); pygame.draw.circle(SCREEN, SHADOW, (int(x), int(y)), r, 4)
            lines = ROOM_LABELS.get(name, [name]); line_height = FONT_XS.get_linesize() * 0.9; total_text_height = len(lines) * line_height
            start_y = y - (total_text_height / 2) + (line_height / 2); current_y = start_y
            for line in lines: draw_text(SCREEN, line, (x, current_y), FONT_XS, SHADOW, center=True, v_center=True); current_y += line_height
        
        # Mostrar Tooltip de Sala
        if hover_room:
            # Asegurar que el tooltip no se salga de la pantalla
            box_x = mouse_pos[0] + 12
            box_y = mouse_pos[1] + 12
            
            # Ancho y alto fijos para el tooltip
            box_width = 260
            box_height = 80
            
            # Ajustar si se sale por la derecha
            if box_x + box_width > WIDTH - 10:
                box_x = mouse_pos[0] - 12 - box_width
            
            # Ajustar si se sale por abajo
            if box_y + box_height > HEIGHT - 10:
                box_y = mouse_pos[1] - 12 - box_height
                
            box = pygame.Rect(box_x, box_y, box_width, box_height)
            
            rounded_rect(SCREEN, box, PANEL)
            
            # Contenido del tooltip
            if hover_room == SECRET_CASE['locacion']:
                tip = "Aquí hay algo importante... (clic para investigar)"
            else:
                tip = "Investigar: podrás encontrar observaciones o pistas falsas."
                
            draw_text(SCREEN, hover_room, (box.x + 12, box.y + 8), FONT_SM, ACCENT)
            lines = wrap_para(tip, box.width - 24, FONT_XS); ly = box.y + 34
            for ln in lines: draw_text(SCREEN, ln, (box.x + 12, ly), FONT_XS, TEXT); ly += 18
            
        ev_y_start = map_rect.y + map_rect.height - 130

    
    else:
        # Mostrar el logo si no está en modo mapa
        if LOGO_IMG:
            logo_rect = LOGO_IMG.get_rect(center=map_rect.center)
            SCREEN.blit(LOGO_IMG, logo_rect)
        else:
            draw_text(SCREEN, "Logo no disponible", (map_rect.centerx, map_rect.centery), FONT_MED, TEXT, center=True, v_center=True)

    draw_text(SCREEN, "", (20, HEIGHT-24), FONT_XS, MUTED)
    return btn_invest, btn_inv, btn_acc, hover_room, absolute_room_pos, btn_suspects

def screen_suspect_list():
    screen_base("Sospechosos")
    panel_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)
    draw_shadowed_panel(SCREEN, panel_rect, color=PANEL)
    draw_text(SCREEN, "Archivos de Sospechosos", (panel_rect.centerx, panel_rect.y + 30), FONT_BIG, ACCENT, center=True)

    buttons = []
    x_start, y_start, col_limit, button_spacing = panel_rect.x + 50, panel_rect.y + 100, 2, 60
    
    # Botones de Sospechosos
    for i, suspect in enumerate(SOSPECHOSOS):
        col = i % col_limit
        row = i // col_limit
        
        btn_width = (panel_rect.width - 150) // col_limit 
        
        x = x_start + col * (btn_width + 50)
        y = y_start + row * button_spacing
        
        btn_rect = pygame.Rect(x, y, btn_width, 40)
        rounded_rect(SCREEN, btn_rect, CARD)
        draw_text(SCREEN, suspect, btn_rect.center, FONT_MED, TEXT, center=True, v_center=True)
        buttons.append((suspect, btn_rect))

    # Botón de Volver al Tablero (Cambiado de 'Volver' a 'Volver al Tablero')
    btn_back_rect = pygame.Rect(panel_rect.x + 30, panel_rect.bottom - 70, 200, 40)
    rounded_rect(SCREEN, btn_back_rect, OK)
    draw_text(SCREEN, "Volver al Tablero", btn_back_rect.center, FONT_XS, SHADOW, center=True, v_center=True)
    buttons.append(("volver_tablero", btn_back_rect))
    
    return buttons


def screen_suspect_detail(suspect_name):
    """Muestra la ficha de investigación detallada de un sospechoso."""
    SCREEN.fill(BG)
    panel_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)
    draw_shadowed_panel(SCREEN, panel_rect, color=PANEL)
    draw_text(SCREEN, "FICHA DE INVESTIGACIÓN", (panel_rect.centerx, panel_rect.y + 30), FONT_MED, ACCENT, center=True)
    
    data = SUSPECT_DATA.get(suspect_name)
    image = SUSPECT_IMAGES.get(suspect_name)
    
    # Área de Imagen: Superior derecha
    img_width, img_height = 150, 150 
    img_x = panel_rect.right - 30 - img_width
    img_y = panel_rect.y + 30 # Más cerca del borde superior

    if image:
        img_rect = image.get_rect(topleft=(img_x, img_y))
        SCREEN.blit(image, img_rect)
        pygame.draw.rect(SCREEN, ACCENT, img_rect, 2) # Borde para destacar la imagen
    else:
        img_rect = pygame.Rect(img_x, img_y, img_width, img_height)
        rounded_rect(SCREEN, img_rect, CARD)
        draw_text(SCREEN, "(Sin Imagen)", img_rect.center, FONT_SM, TEXT, center=True, v_center=True)
        
    # Inicio del área de texto (izquierda y debajo del título)
    text_x_start = panel_rect.x + 30
    current_y = panel_rect.y + 80 # Justo debajo del título principal

    # --- INFORMACIÓN BÁSICA (CARTA POLICIACA) ---
    draw_text(SCREEN, f"Sospechoso: {suspect_name}", (text_x_start, current_y), FONT_SM, TEXT)
    current_y += 30
    draw_text(SCREEN, f"Cargo: {data.get('cargo', 'N/D')}", (text_x_start, current_y), FONT_SM, MUTED)
    current_y += 20
    draw_text(SCREEN, f"Edad: {data.get('edad', 'N/D')}", (text_x_start, current_y), FONT_SM, MUTED)
    current_y += 20
    draw_text(SCREEN, f"Personalidad: {data.get('personalidad', 'N/D')}", (text_x_start, current_y), FONT_SM, MUTED)
    current_y += 40

    # --- RELACIÓN Y MOTIVO POSIBLE ---
    draw_text(SCREEN, "Relación con Bodoque:", (text_x_start, current_y), FONT_SM, ACCENT)
    current_y += 20
    lines_relacion = wrap_para(data.get('relacion', 'N/D'), img_x - text_x_start - 20, FONT_SM)
    for line in lines_relacion:
        draw_text(SCREEN, line, (text_x_start, current_y), FONT_XS, TEXT)
        current_y += 20
    current_y += 20
    
    draw_text(SCREEN, "Motivo Posible:", (text_x_start, current_y), FONT_SM, ACCENT)
    current_y += 20
    lines_motivo = wrap_para(data.get('motivo_posible', 'N/D'), img_x - text_x_start - 20, FONT_SM)
    for line in lines_motivo:
        draw_text(SCREEN, line, (text_x_start, current_y), FONT_XS, TEXT)
        current_y += 20
    
    current_y += 30
    
    # --- COMPORTAMIENTO RECIENTE (Columna Derecha) ---
    comp_x_start = img_x - 10 # Justo a la izquierda de la imagen
    comp_y_start = img_y + img_height + 20 # Debajo de la imagen
    
    draw_text(SCREEN, "Comportamiento:", (comp_x_start, comp_y_start), FONT_XS, ACCENT)
    comp_y_start += 20
    
    comp_lines = data.get('comportamiento', ['N/D'])
    for line in comp_lines:
        lines = wrap_para(line, panel_rect.right - comp_x_start - 30, FONT_SM)
        for sub_line in lines:
            draw_text(SCREEN, f"• {sub_line}", (comp_x_start, comp_y_start), FONT_XS, MUTED)
            comp_y_start += 20
        
    

    # 3. Botón de Volver al Tablero (Para saltar la lista de sospechosos si lo desea)
    btn_back_to_list_rect = pygame.Rect(panel_rect.x + 30, panel_rect.bottom - 70, 150, 40); rounded_rect(SCREEN, btn_back_to_list_rect, CARD)
    draw_text(SCREEN, "Volver (Lista)", btn_back_to_list_rect.center, FONT_XS, TEXT, center=True, v_center=True)

    btn_back_to_board_rect = pygame.Rect(btn_back_to_list_rect.right + 20, panel_rect.bottom - 70, 200, 40); rounded_rect(SCREEN, btn_back_to_board_rect, OK)
    draw_text(SCREEN, "Volver al Tablero", btn_back_to_board_rect.center, FONT_XS, SHADOW, center=True, v_center=True)

    return btn_back_to_list_rect, btn_back_to_board_rect
    

def screen_investigate(room):
    screen_base(f"Investigando: {room}")
    
    # Generar la pista (temporalmente, la pista real se maneja en screen_investigate)
    text = "PISTA CLAVE: " + SECRET_CASE['pista_clave'] if room == SECRET_CASE['locacion'] else "OBSERVACIÓN: " + SECRET_CASE['pistas_falsas'].get(room, "Solo polvo y silencio; nadie relevante estuvo aquí. Sin rastro de actividad reciente.")
    
    panel_rect = pygame.Rect(50, 60, WIDTH - 100, HEIGHT - 120)
    draw_shadowed_panel(SCREEN, panel_rect, color=PANEL)
    
    # Imagen de Locación
    if LOCATION_IMAGES.get(room):
        # Mueve la imagen a la esquina inferior derecha del panel.
        # Utilizamos panel_rect.bottom en lugar de panel_rect.y para el cálculo vertical.
        img_rect = LOCATION_IMAGES[room].get_rect(bottomright=(panel_rect.right - 20, panel_rect.bottom - 20))
        SCREEN.blit(LOCATION_IMAGES[room], img_rect)
        
    draw_text(SCREEN, f"Detalles en {room}:", (panel_rect.x + 20, panel_rect.y + 20), FONT_XS, ACCENT)
    
    # Área de texto
    text_area_width = panel_rect.width - 40
    if LOCATION_IMAGES.get(room):
        text_area_width = img_rect.left - panel_rect.x - 40
        
    lines = wrap_para(text, text_area_width, FONT_SM)
    y = panel_rect.y + 70
    
    for ln in lines:
        draw_text(SCREEN, ln, (panel_rect.x + 20, y), FONT_SM, TEXT)
        y += 30

    # Botones
    btn_take = pygame.Rect(panel_rect.x + 20, panel_rect.bottom - 70, 200, 40); rounded_rect(SCREEN, btn_take, OK)
    draw_text(SCREEN, "Guardar evidencia", btn_take.center, FONT_SM, SHADOW, center=True, v_center=True)
    
    # Aquí, btn_back debe ser el botón de volver (que te lleva al tablero con el logo)
    btn_back = pygame.Rect(btn_take.right + 20, panel_rect.bottom - 70, 200, 40); rounded_rect(SCREEN, btn_back, CARD)
    draw_text(SCREEN, "Volver al Tablero", btn_back.center, FONT_XS, TEXT, center=True, v_center=True)
    
    return btn_take, btn_back, text

def screen_inventory():
    screen_base("Inventario y Notas")

    panel_rect = pygame.Rect(50, 60, WIDTH - 100, HEIGHT - 120)
    draw_shadowed_panel(SCREEN, panel_rect, color=PANEL)
    draw_text(SCREEN, "Pistas Guardadas:", (panel_rect.x + 20, panel_rect.y + 20), FONT_BIG, ACCENT)

    # --- Control de páginas ---
    items_per_page = 5
    total_items = len(state['evidence'])
    total_pages = max(1, math.ceil(total_items / items_per_page))
    current_page = state.get("inventory_page", 1)

    # Limitar página al rango correcto
    if current_page > total_pages:
        current_page = total_pages
    if current_page < 1:
        current_page = 1
    state["inventory_page"] = current_page

    # Selección de pistas para mostrar
    start = (current_page - 1) * items_per_page
    end = start + items_per_page
    items = state['evidence'][start:end]

    y = panel_rect.y + 70
    if items:
        for item in items:
            draw_text(SCREEN, f"[{item['loc']}]", (panel_rect.x + 30, y), FONT_SM, MUTED)
            lines = wrap_para(item['text'], panel_rect.width - 250, FONT_SM)
            for line in lines:
                draw_text(SCREEN, line, (panel_rect.x + 150, y), FONT_SM, TEXT)
                y += 25
            y += 10
    else:
        draw_text(SCREEN, "Aún no has encontrado ninguna evidencia.",
                  (panel_rect.centerx, panel_rect.centery), FONT_MED, MUTED, center=True, v_center=True)

    # --- Botones ---
    btn_back = pygame.Rect(panel_rect.x + 20, panel_rect.bottom - 70, 200, 40)
    rounded_rect(SCREEN, btn_back, OK)
    draw_text(SCREEN, "Volver al Tablero", btn_back.center, FONT_XS, SHADOW, center=True, v_center=True)

    btn_prev = btn_next = None
    if total_pages > 1:
        draw_text(SCREEN, f"Página {current_page}/{total_pages}",
                  (panel_rect.centerx, panel_rect.bottom - 55), FONT_SM, ACCENT, center=True)
        # Botón anterior
        if current_page > 1:
            btn_prev = pygame.Rect(panel_rect.centerx - 150, panel_rect.bottom - 70, 100, 40)
            rounded_rect(SCREEN, btn_prev, CARD)
            draw_text(SCREEN, "< Anterior", btn_prev.center, FONT_XS, TEXT, center=True, v_center=True)
        # Botón siguiente
        if current_page < total_pages:
            btn_next = pygame.Rect(panel_rect.centerx + 50, panel_rect.bottom - 70, 100, 40)
            rounded_rect(SCREEN, btn_next, CARD)
            draw_text(SCREEN, "Siguiente >", btn_next.center, FONT_XS, TEXT, center=True, v_center=True)

    return btn_back, btn_prev, btn_next



def screen_accuse(choice):
    screen_base("Hacer una Acusación Final")
    panel_rect = pygame.Rect(30, 60, WIDTH - 60, HEIGHT - 120)
    draw_shadowed_panel(SCREEN, panel_rect, color=PANEL)
    draw_text(SCREEN, "Selecciona el Culpable, Arma y Locación:", (panel_rect.centerx, panel_rect.y + 30), FONT_MED, ACCENT, center=True)
    
    titles = ["Sospechoso", "Arma", "Locación"]
    lists = [SOSPECHOSOS, ARMAS, LOCACIONES]
    selection_keys = ['person', 'weapon', 'room']
    
    col_gap = 10
    col_count = 3
    total_gap_width = col_gap * (col_count - 1)
    col_w = (panel_rect.width - 40 - total_gap_width) / col_count
    
    col_x = [panel_rect.x + 20, panel_rect.x + 20 + col_w + col_gap, panel_rect.x + 20 + 2*(col_w + col_gap)]
    
    # Dibuja Columnas de Selección
    button_spacing = 44
    for col_index, (title, item_list, key) in enumerate(zip(titles, lists, selection_keys)):
        x = col_x[col_index]
        draw_text(SCREEN, title, (x + col_w // 2, panel_rect.y + 70), FONT_MED, MUTED, center=True)
        
        for i, item in enumerate(item_list):
            is_selected = choice.get(key) == i
            
            y = panel_rect.y + 100 + i * button_spacing
            
            # Ajustar la posición y el tamaño para el marco
            rect = pygame.Rect(x, y, col_w, 38)
            
            color = ACCENT_HOVER if is_selected else CARD
            rounded_rect(SCREEN, rect, color)
            
            text_color = SHADOW if is_selected else TEXT
            draw_text(SCREEN, item, rect.center, FONT_SM, text_color, center=True, v_center=True)

    # Botones inferiores
    btn_y = panel_rect.bottom - 70

    # Botón de Volver (Añadido)
    btn_back = pygame.Rect(panel_rect.x + 20, btn_y, 150, 40)
    rounded_rect(SCREEN, btn_back, CARD)
    draw_text(SCREEN, "Volver", btn_back.center, FONT_MED, TEXT, center=True, v_center=True)

    # Botón de Confirmar (Re-posicionado)
    btn_confirm = pygame.Rect(WIDTH // 2 - 150, btn_y, 300, 40)
    
    is_ready = choice['person'] is not None and choice['weapon'] is not None and choice['room'] is not None
    btn_color = OK if is_ready else CARD
    btn_text_color = SHADOW if is_ready else MUTED
    
    rounded_rect(SCREEN, btn_confirm, btn_color)
    draw_text(SCREEN, "ACUSAR", btn_confirm.center, FONT_MED, btn_text_color, center=True, v_center=True)
    
    return btn_confirm, btn_back

def screen_result(success, text):
    SCREEN.blit(FONDO_MENU, (0, 0))
    overlay_color = (0, 100, 0, 180) if success else (100, 0, 0, 180)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill(overlay_color); SCREEN.blit(overlay, (0, 0))
    
    title = "¡CASO RESUELTO!" if success else "¡CASO FALLIDO!"
    title_color = TEXT if success else TEXT
    
    draw_text(SCREEN, title, (WIDTH // 2, HEIGHT // 4), FONT_BIG, title_color, center=True)
    
    # Dibujar mensaje envuelto
    lines = wrap_para(text, WIDTH - 120, FONT_MED)
    y = HEIGHT // 2 - 50
    for ln in lines:
        draw_text(SCREEN, ln, (WIDTH // 2, y), FONT_MED, TEXT, center=True)
        y += 30
    
    # Botón de Salir
    btn_exit = pygame.Rect(WIDTH // 2 - 140, HEIGHT - 120, 280, 64)
    rounded_rect(SCREEN, btn_exit, OK)
    draw_text(SCREEN, "Salir del juego", btn_exit.center, FONT_MED, SHADOW, center=True, v_center=True)
    return btn_exit

def complete_investigation(room, content):
    """Guarda la evidencia y consume un turno."""
    # Solo guarda evidencia si es la primera vez que se visita esta sala
    if room not in state['investigated']:
        state['investigated'].add(room)
        state['evidence'].append({'loc': room, 'text': content})
        state['turns'] -= 1
        return True
    return False

def evaluate_accusation(choice):
    """Evalúa la acusación final del jugador."""
    
    # 1. Obtener los nombres de las selecciones
    suspect = SOSPECHOSOS[choice['person']]
    weapon = ARMAS[choice['weapon']]
    room = LOCACIONES[choice['room']]
    
    # 2. Evaluar la acusación
    if suspect == SOLUTION['culpable'] and weapon == SOLUTION['arma'] and room == SOLUTION['locacion']:
        result_text = (f"¡Acusación correcta! El culpable es {suspect}, quien usó el {weapon} "
                      f"en {room}. El motivo: {SECRET_CASE['motivo']}")
        return True, result_text
    else:
        # Penalización: en Clue el juego termina si fallas
        state['turns'] = 0 
        result_text = (f"Acusación incorrecta. Señalaste a {suspect} con el {weapon} en {room}. "
                      f"El caso real era: {SOLUTION['culpable']}, {SOLUTION['arma']} en {SOLUTION['locacion']}."
                      f"¡El verdadero asesino escapó!")
        return False, result_text

# -------------------------
# Main Game Loop
# -------------------------
def main():
    # ----------------------------------------
    # Inicialización de Variables
    # ----------------------------------------
    global state, SCREEN, CLOCK, FPS, WIDTH, HEIGHT 
    
    running = True
    
    # Variables de estado del tablero (se actualizan en el bloque de dibujo)
    hover_room = None
    btn_invest = pygame.Rect(0, 0, 1, 1) 
    btn_inv = pygame.Rect(0, 0, 1, 1)
    btn_acc = pygame.Rect(0, 0, 1, 1)
    btn_suspects = pygame.Rect(0, 0, 1, 1)
    absolute_room_pos = {} 
    
    # Variables de estado de investigación (se actualizan en el bloque de dibujo)
    current_investigation_content = ""
    btn_take = pygame.Rect(0, 0, 1, 1) # Botón 'Tomar' en investigate
    btn_back = pygame.Rect(0, 0, 1, 1) # Botón 'Volver' en investigate
    
    # Variables de botones específicos que se calculan en el loop de dibujo
    btn_accuse_confirm = pygame.Rect(0, 0, 1, 1)
    btn_accuse_back = pygame.Rect(0, 0, 1, 1)
    btn_sus_list_back = pygame.Rect(0, 0, 1, 1)
    btn_sus_det_to_list = pygame.Rect(0, 0, 1, 1)
    btn_sus_det_to_board = pygame.Rect(0, 0, 1, 1)
    btn_inv_back = pygame.Rect(0, 0, 1, 1)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # --- Manejo de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos 
            
            # --- Manejo de Clicks de Ratón ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                # Manejo de MAIN_MENU
                if state['screen'] == 'main_menu':
                    btn = screen_main_menu() 
                    if btn.collidepoint(mouse_pos):
                        state['screen'] = 'intro'
                        state['story_page'] = 1

                # Manejo de INTRO
                elif state['screen'] == 'intro':
                    if state['story_page'] == 1: btn = screen_story_page1() 
                    elif state['story_page'] == 2: btn = screen_story_page2() 
                    elif state['story_page'] == 3: btn = screen_story_page3()
                    else: btn = None 

                    if btn and btn.collidepoint(mouse_pos):
                        if state['story_page'] < 3:
                            state['story_page'] += 1
                        else:
                            state['screen'] = 'board'
                            # Se mantiene show_map: False para el logo (Modificación 2 anterior)

                # Manejo de BOARD
                elif state['screen'] == 'board':
                    click_pos = event.pos 
                    btn_invest, btn_inv, btn_acc, hover_room, absolute_room_pos, btn_suspects = screen_board(click_pos)
                    
                    if btn_inv.collidepoint(click_pos):
                        state['screen'] = 'inventory'
                        state['show_map'] = False # Opcional: oculta mapa al ir a inventario
                    elif btn_suspects.collidepoint(click_pos):
                        state['screen'] = 'suspect_list'
                        state['show_map'] = False # Opcional: oculta mapa al ir a sospechosos
                    elif btn_acc.collidepoint(click_pos):
                        state['screen'] = 'accuse'
                        state['show_map'] = False # Opcional: oculta mapa al ir a acusar
                    
                    elif btn_invest.collidepoint(click_pos):
                        state['show_map'] = True
                        
                    elif state['show_map']: 
                        clicked_room = None
                        for name, pos in absolute_room_pos.items():
                            x, y = pos; r = ROOM_RADIUS; dist = math.hypot(click_pos[0] - x, click_pos[1] - y)
                            if dist <= r:
                                clicked_room = name
                                break
                                
                        if clicked_room:
                            state['selected_room'] = clicked_room
                            state['screen'] = 'investigate' 

                # Manejo de INVESTIGATE
                elif state['screen'] == 'investigate':
                    if btn_back.collidepoint(mouse_pos) or btn_take.collidepoint(mouse_pos): 
                        complete_investigation(state['selected_room'], current_investigation_content)
                        state['screen'] = 'board'
                        state['show_map'] = False # <--- CORRECCIÓN: Vuelve a logo/tablero no mapa

                # Manejo de INVENTORY
                elif state['screen'] == 'inventory':
                    btn_back, btn_prev, btn_next = screen_inventory()
                    if btn_back.collidepoint(mouse_pos):
                        state['screen'] = 'board'
                        state['show_map'] = False
                elif btn_prev and btn_prev.collidepoint(mouse_pos):
                    state["inventory_page"] = max(1, state.get("inventory_page", 1) - 1)
                elif btn_next and btn_next.collidepoint(mouse_pos):
                    total_items = len(state['evidence'])
                    items_per_page = 5
                    total_pages = max(1, math.ceil(total_items / items_per_page))
                    state["inventory_page"] = min(total_pages, state.get("inventory_page", 1) + 1)

                # Manejo de SUSPECT_LIST
                elif state['screen'] == 'suspect_list':
                    buttons = screen_suspect_list() 
                    for name, btn in buttons:
                        if btn.collidepoint(mouse_pos):
                            if name == "volver_tablero":
                                state['screen'] = 'board'
                                state['show_map'] = False # <--- CORRECCIÓN: Vuelve a logo/tablero no mapa
                            else:
                                state['screen'] = 'suspect_detail'
                                state['selected_suspect'] = name

                # Manejo de SUSPECT_DETAIL
                elif state['screen'] == 'suspect_detail':
                    if btn_sus_det_to_list.collidepoint(mouse_pos):
                        state['screen'] = 'suspect_list'
                    elif btn_sus_det_to_board.collidepoint(mouse_pos):
                        state['screen'] = 'board'
                        state['show_map'] = False # <--- CORRECCIÓN: Vuelve a logo/tablero no mapa
                
                # Manejo de ACCUSE
               # --- dentro de main(), en la parte de manejo de eventos ---
                elif state['screen'] == 'accuse':
                    if btn_accuse_back.collidepoint(mouse_pos):
                        state['screen'] = 'board'
                        state['show_map'] = False

                    # Calcula columnas igual que en screen_accuse
                    col_gap = 10
                    col_count = 3
                    total_gap_width = col_gap * (col_count - 1)
                    col_w = (WIDTH - 60 - total_gap_width) / col_count
                    panel_x = 30
                    panel_y = 60  # ← Agregado
                    col_x = [panel_x + 20,
                            panel_x + 20 + col_w + col_gap,
                            panel_x + 20 + 2*(col_w + col_gap)]
                    button_spacing = 44

                    # Verifica clicks con coordenadas correctas
                    for i, p in enumerate(SOSPECHOSOS):
                        rect = pygame.Rect(col_x[0], panel_y + 100 + i*button_spacing, col_w, 38)
                        if rect.collidepoint(mouse_pos):
                            state['accuse_choice']['person'] = i

                    for i, a in enumerate(ARMAS):
                        rect = pygame.Rect(col_x[1], panel_y + 100 + i*button_spacing, col_w, 38)
                        if rect.collidepoint(mouse_pos):
                            state['accuse_choice']['weapon'] = i

                    for i, l in enumerate(LOCACIONES):
                        rect = pygame.Rect(col_x[2], panel_y + 100 + i*button_spacing, col_w, 38)
                        if rect.collidepoint(mouse_pos):
                            state['accuse_choice']['room'] = i

                    # Click en ACUSAR
                    is_ready = (
                        state['accuse_choice']['person'] is not None
                        and state['accuse_choice']['weapon'] is not None
                        and state['accuse_choice']['room'] is not None
                    )
                    if btn_accuse_confirm.collidepoint(mouse_pos) and is_ready:
                        success, text = evaluate_accusation(state['accuse_choice'])
                        state['result'] = (success, text)
                        state['screen'] = 'result'

                
                # Manejo de RESULT
                elif state['screen'] == 'result':
                    btn_exit = screen_result(*state['result']) 
                    if btn_exit.collidepoint(mouse_pos):
                        running = False


        # --- DIBUJAR PANTALLAS (Actualiza rects para el próximo clic) ---
        if state['screen'] == 'main_menu':
            screen_main_menu() 
        elif state['screen'] == 'intro':
            if state['story_page'] == 1: screen_story_page1()
            elif state['story_page'] == 2: screen_story_page2()
            elif state['story_page'] == 3: screen_story_page3()
        elif state['screen'] == 'board':
            btn_invest, btn_inv, btn_acc, hover_room, absolute_room_pos, btn_suspects = screen_board(mouse_pos)
        elif state['screen'] == 'suspect_list':
            screen_suspect_list()
        elif state['screen'] == 'suspect_detail':
            btn_sus_det_to_list, btn_sus_det_to_board = screen_suspect_detail(state['selected_suspect'])
        elif state['screen'] == 'investigate':
            btn_take_rect, btn_back_rect, content = screen_investigate(state['selected_room'])
            current_investigation_content = content 
            btn_take = btn_take_rect 
            btn_back = btn_back_rect 
        elif state['screen'] == 'inventory':
            btn_inv_back = screen_inventory() # Guarda el Rect del botón Volver
        elif state['screen'] == 'accuse':
            btn_accuse_confirm, btn_accuse_back = screen_accuse(state['accuse_choice']) # Guarda los Rects de los botones
        elif state['screen'] == 'result':
            screen_result(*state['result'])

        # --- Fin de juego por turnos ---
        if state['turns'] <= 0 and state['screen'] not in ['result', 'main_menu', 'intro']:
            if state['result'] is None:
                state['result'] = (False, "¡Se te acabaron los turnos! El asesino ha escapado y el caso queda sin resolver.")
            state['screen'] = 'result'
            
        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()