import pygame
import json
import math
import os

# --- AYARLAR ---
SCREEN_WIDTH = 1000  # Streamlit'teki display_width ile aynı olsun
SCREEN_HEIGHT = 800  # Haritanın oranına göre ayarla
FPS = 60
ROVER_SPEED = 2      # Piksel cinsinden hız
ROVER_SIZE = 20      # Rover'ın simgedeki boyutu

# --- RENKLER ---
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# --- JSON VERİSİNİ OKU ---
def load_path(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    # Veriler 256'lık sistemde olduğu için ekran boyutuna ölçekliyoruz
    # sw ve sh katsayılarını Streamlit kodunla aynı tutmalısın
    sw = SCREEN_WIDTH / 256
    sh = SCREEN_HEIGHT / 256
    return [(p['x'] * sw, p['y'] * sh) for p in data]

# --- PYGAME BAŞLAT ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🌙 TUA Astro - Rover Mission Simulation")
clock = pygame.time.Clock()

# --- GÖRSEL VARLIKLAR ---
# Arka plan resmi (Streamlit'te kullandığın resmin aynısı)
try:
    bg_img = pygame.image.load("pcam/PCAM8.png")
    bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    bg_img = None
    print("Arka plan resmi bulunamadı, siyah ekran kullanılacak.")

# --- ROTA VE ROVER DURUMU ---
full_path = load_path("rover_mission_path.json") # Streamlit'ten indirdiğin dosya
current_point_idx = 0
rover_pos = list(full_path[0]) # Başlangıç noktası

def move_rover(current_pos, target_pos, speed):
    """Rover'ı hedefe doğru pürüzsüzce hareket ettirir."""
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    distance = math.hypot(dx, dy)
    
    if distance < speed:
        return target_pos, True # Hedefe ulaştı
    
    # Birim vektör hesapla ve hızla çarp
    vx = (dx / distance) * speed
    vy = (dy / distance) * speed
    return [current_pos[0] + vx, current_pos[1] + vy], False

# --- ANA DÖNGÜ ---
running = True
mission_complete = False

while running:
    screen.fill((0, 0, 0))
    if bg_img:
        screen.blit(bg_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Rotayı Çiz (Gidilecek yol)
    if len(full_path) > 1:
        pygame.draw.lines(screen, CYAN, False, full_path, 2)

    # 2. Rover Hareket Mantığı
    if not mission_complete:
        target = full_path[current_point_idx]
        rover_pos, reached = move_rover(rover_pos, target, ROVER_SPEED)
        
        if reached:
            current_point_idx += 1
            if current_point_idx >= len(full_path):
                mission_complete = True
                print("🏁 Görev Tamamlandı!")

    # 3. Rover'ı Çiz (Basit bir kare veya üçgen)
    rover_rect = pygame.Rect(0, 0, ROVER_SIZE, ROVER_SIZE)
    rover_rect.center = (int(rover_pos[0]), int(rover_pos[1]))
    pygame.draw.rect(screen, RED, rover_rect)
    
    # 4. Bilgi Yazısı
    font = pygame.font.SysFont("Arial", 20)
    status_text = "DURUM: GOREV DEVAM EDIYOR" if not mission_complete else "DURUM: HEDEFE ULASILDI"
    text_surf = font.render(status_text, True, WHITE)
    screen.blit(text_surf, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()