import pygame
import sys
import math
import os
from PIL import Image, ImageSequence  # Necesitas instalar Pillow

# Inicializar Pygame
pygame.init()

# Configuración inicial de la pantalla
base_width, base_height = 800, 800
screen_info = pygame.display.Info()
screen_width, screen_height = base_width, base_height
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Sistema Solar")

# Ruta del directorio
base_path = os.path.dirname(os.path.abspath(__file__))
images_path = os.path.join(base_path, "Imagenes")

# Cargar GIF de fondo
background_frames = []
current_frame = 0
last_frame_update = 0
frame_delay = 50  # Ajusta la velocidad de la animación

try:
    gif_path = os.path.join(images_path, "background.gif")
    gif = Image.open(gif_path)
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
        background_frames.append(pygame_frame)
except Exception as e:
    print(f"⚠️ Error al cargar el GIF: {e}")
    background_frames = None

# Diccionario para caché de imágenes
image_cache = {}

# Fuentes
pygame.font.init()
font = pygame.font.Font(None, 20)
notification_font = pygame.font.Font(None, 24)

# Clase para cuerpos celestes
class CelestialBody:
    def __init__(self, image_name, radius, distance, speed, rotation_speed=0, name=""):
        self.name = name
        self.radius = radius
        self.distance = distance
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.rotation_angle = 0
        
        if image_name in image_cache:
            self.image = image_cache[image_name]
        else:
            try:
                image_path = os.path.join(images_path, image_name)
                image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(image, (radius*2, radius*2))
                image_cache[image_name] = self.image
            except pygame.error:
                print(f"⚠️ Advertencia: No se pudo cargar {image_name}")
                self.image = pygame.Surface((radius*2, radius*2))
                self.image.fill((255, 255, 255))

    def update_position(self):
        self.angle += self.speed
        self.rotation_angle += self.rotation_speed
        self.angle %= 360
        self.rotation_angle %= 360

    def get_position(self):
        x = base_width//2 + self.distance * math.cos(math.radians(self.angle))
        y = base_height//2 + self.distance * math.sin(math.radians(self.angle))
        return int(x), int(y)

# Crear cuerpos celestes
sun = CelestialBody("Sun.png", 50, 0, 0, name="Sol")
planets = [
    CelestialBody("Mercury.png", 8, 70, 1.5, name="Mercurio"),
    CelestialBody("Venus.png", 12, 100, 1.2, name="Venus"),
    CelestialBody("Earth.png", 14, 150, 1, name="Tierra"),
    CelestialBody("Mars.png", 12, 200, 0.8, name="Marte"),
    CelestialBody("Jupiter.png", 16, 250, 0.6, name="Júpiter"),
    CelestialBody("Saturn.png", 14, 300, 0.5, name="Saturno"),
    CelestialBody("Uranus.png", 12, 350, 0.4, name="Urano"),
    CelestialBody("Neptune.png", 12, 400, 0.3, name="Neptuno"),
]

# Variables de control
clock = pygame.time.Clock()
fullscreen = False
virtual_screen = pygame.Surface((base_width, base_height))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen_width = screen_info.current_w
                    screen_height = screen_info.current_h
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                else:
                    screen_width, screen_height = base_width, base_height
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            screen_width, screen_height = event.w, event.h

    # Actualizar fondo animado
    now = pygame.time.get_ticks()
    if background_frames and now - last_frame_update > frame_delay:
        current_frame = (current_frame + 1) % len(background_frames)
        last_frame_update = now

    # Dibujar en la superficie virtual
    if background_frames:
        bg = pygame.transform.scale(background_frames[current_frame], (base_width, base_height))
        virtual_screen.blit(bg, (0, 0))
    else:
        virtual_screen.fill((0, 0, 0))

    # Dibujar Sol
    virtual_screen.blit(sun.image, (base_width//2 - sun.radius, base_height//2 - sun.radius))

    # Dibujar órbitas y planetas
    for planet in planets:
        pygame.draw.circle(virtual_screen, (255,255,255), (base_width//2, base_height//2), planet.distance, 1)
        planet.update_position()
        x, y = planet.get_position()
        virtual_screen.blit(planet.image, (x - planet.radius, y - planet.radius))
        text = font.render(planet.name, True, (255,255,255))
        virtual_screen.blit(text, (x + 10, y - 10))

    # Escalar a la pantalla real
    screen.blit(pygame.transform.scale(virtual_screen, (screen_width, screen_height)), (0, 0))

    # Mostrar notificación en modo ventana
    if not fullscreen and (screen_width < 800 or screen_height < 600):
        notification = notification_font.render("Presiona F11 para pantalla completa", True, (255,255,255))
        screen.blit(notification, (10, 10))

    pygame.display.flip()
    clock.tick(60)