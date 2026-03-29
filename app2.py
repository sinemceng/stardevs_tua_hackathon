import streamlit as st
import numpy as np
import cv2
import heapq
import math
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
import subprocess
import os

import json
import pandas as pd

def convert_path_to_json(path):
    # Simülasyonlar için [{x:..., y:...}, ...] formatında JSON
    json_data = [{"x": float(p[0]), "y": float(p[1])} for p in path]
    return json.dumps(json_data)

def convert_path_to_csv(path):
    # Veri analizi için CSV formatı
    df = pd.DataFrame(path, columns=['x', 'y'])
    return df.to_csv(index=False).encode('utf-8')

# ==========================================
# 🛰️ 1. ALGORİTMA: ULTIMATE A* (POTANSİYEL ALANLI - MEVCUT)
# ==========================================
def run_ultimate_astar(input_grid, original_mask, start, goal):
    height, width = input_grid.shape
    start_node = (int(start[1]), int(start[0])) # (y, x)
    goal_node = (int(goal[1]), int(goal[0]))
    
    dist_map = cv2.distanceTransform((1 - original_mask).astype(np.uint8), cv2.DIST_L2, 5)

    open_list = []
    heapq.heappush(open_list, (0, start_node))
    came_from = {}
    g_score = {start_node: 0}
    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    while open_list:
        current = heapq.heappop(open_list)[1]
        if math.dist(current, goal_node) < 3:
            path = []
            while current in came_from:
                path.append((current[1], current[0]))
                current = came_from[current]
            path.append((start[0], start[1]))
            return path[::-1], True

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < height and 0 <= neighbor[1] < width:
                if input_grid[neighbor[0], neighbor[1]] == 1:
                    continue
                
                dist_to_rock = dist_map[neighbor[0], neighbor[1]]
                safety_penalty = 0
                if dist_to_rock < 18:
                    safety_penalty = (18 - dist_to_rock) ** 2.5 
                
                move_cost = math.sqrt(dx**2 + dy**2)
                tentative_g_score = g_score[current] + move_cost + safety_penalty

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    h = math.dist(neighbor, goal_node)
                    heapq.heappush(open_list, (tentative_g_score + h, neighbor))
    return None, False

# ==========================================
# 🛰️ 2. ALGORİTMA: HYBRID A* (KİNEMATİK KISITLI - YENİ)
# ==========================================
def hybrid_astar_engine(grid, start, goal):
    height, width = grid.shape
    # (maliyet, x, y, theta)
    start_node_data = (0, float(start[0]), float(start[1]), 0.0)
    queue = [start_node_data]

    visited = set()
    parents = {}
    costs = {(int(start[0]), int(start[1])): 0.0}

    steer_angles = [-math.pi / 4, 0, math.pi / 4]  # Sol, Düz, Sağ
    step_size = 4.0  

    while queue:
        priority, x, y, theta = heapq.heappop(queue)

        if math.dist((x, y), goal) < 6:
            # Yolu geri inşa et
            path = []
            curr = (x, y)
            while curr in parents:
                path.append(curr)
                curr = parents[curr]
            path.append(start)
            return path[::-1], True

        if (int(x), int(y)) in visited: continue
        visited.add((int(x), int(y)))

        for angle in steer_angles:
            new_theta = (theta + angle) % (2 * math.pi)
            new_x = x + step_size * math.cos(new_theta)
            new_y = y + step_size * math.sin(new_theta)

            nx, ny = int(new_x), int(new_y)

            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny, nx] == 0:
                    current_cost = costs.get((int(x), int(y)), 0)
                    new_cost = current_cost + step_size + abs(angle) * 2

                    if (nx, ny) not in costs or new_cost < costs[(nx, ny)]:
                        costs[(nx, ny)] = new_cost
                        priority = new_cost + math.dist((nx, ny), goal)
                        heapq.heappush(queue, (priority, new_x, new_y, new_theta))
                        parents[(new_x, new_y)] = (x, y)

    return None, False

# ==========================================
# 📂 3. NPY İŞLEME
# ==========================================
@st.cache_data
def load_fixed_npy(file_path):
    """
    Dosya seçiciyi aradan kaldırıp direkt dosyayı okur.
    """
    if not os.path.exists(file_path):
        st.error(f"Kritik Hata: '{file_path}' dosyası klasörde bulunamadı!")
        return None, None
    try:
        mask = np.load(file_path)
        if len(mask.shape) == 3: mask = np.squeeze(mask)
        if len(mask.shape) == 3: mask = mask[:, :, 0]
        if mask.shape != (256, 256): mask = cv2.resize(mask, (256, 256))
        binary_mask = (mask > 0.5).astype(np.uint8)
        kernel = np.ones((5,5), np.uint8)
        dilated_grid = cv2.dilate(binary_mask, kernel, iterations=2)
        return dilated_grid, binary_mask
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
        return None, None

# ==========================================
# 🎨 4. STREAMLIT ARAYÜZ
# ==========================================
st.set_page_config(page_title="TUA Astro - Multi-Algo", layout="wide")

if "points" not in st.session_state:
    st.session_state.points = [] 

with st.sidebar:
    NPY_FILE_PATH = "tahmin_sonucu.npy"
    st.header("⚙️ Görev Kontrol")
    
    # --- ALGORİTMA SEÇİM KUTUSU ---
    algo_choice = st.selectbox(
        "Navigasyon Algoritması Seçin",
        ["Ultimate A* (Potansiyel Alan)", "Hybrid A* (Kinematik Kısıtlı)"]
    )
    
    st.info(f"📁 Kaynak: {NPY_FILE_PATH} (Otomatik Yüklendi)")
    
    if st.button("Seçimleri Temizle"):
        st.session_state.points = []
        st.rerun()
    
    # Durum Bilgisi
    if len(st.session_state.points) == 0:
        st.info("Haritadan **Başlangıç** noktasını seç.")
    elif len(st.session_state.points) == 1:
        st.warning("Haritadan **Hedef** noktasını seç.")

# Harita Yükleme
map_img_path = "pcam/PCAM8.png"
try:
    orig_img = Image.open(map_img_path).convert("RGB")
    W, H = orig_img.size
except:
    W, H = 1024, 1024
    orig_img = Image.new('RGB', (W, H), (30,30,30))

draw_img = orig_img.copy()
sw, sh = W / 256, H / 256


# --- 🛰️ HESAPLAMA VE ÇİZİM ---
grid, base_mask = load_fixed_npy(NPY_FILE_PATH)

if grid is not None:
    # Engelleri çiz
    mask_large = cv2.resize(base_mask, (W, H))
    red_overlay = Image.new("RGB", (W, H), (255, 0, 0))
    mask_alpha = Image.fromarray((mask_large * 100).astype(np.uint8)).convert("L")
    draw_img.paste(red_overlay, (0, 0), mask_alpha)

    if len(st.session_state.points) == 2:
        start_pt = st.session_state.points[0]
        goal_pt = st.session_state.points[1]
        
        if algo_choice == "Ultimate A* (Potansiyel Alan)":
            path, success = run_ultimate_astar(grid, base_mask, start_pt, goal_pt)
        else:
            path, success = hybrid_astar_engine(grid, start_pt, goal_pt)
        
        if success:
            # 1. Görselleştirme
            path_pts = [(p[0] * sw, p[1] * sh) for p in path]
            draw = ImageDraw.Draw(draw_img)
            draw.line(path_pts, fill="#00FFFF", width=6)
            st.sidebar.success(f"✅ {algo_choice} ile rota çizildi.")

            # 2. JSON Hazırla ve OTOMATİK KAYDET
            json_data = [{"x": float(p[0]), "y": float(p[1])} for p in path]
            json_string = json.dumps(json_data)
            with open("rover_mission_path.json", "w") as f:
                f.write(json_string)

            # 3. OTOMATİK SİMÜLASYON BAŞLAT
            try:
                subprocess.Popen(["python", "simulation.py"])
                st.sidebar.info("🚀 Simülasyon Başlatıldı!")
            except Exception as e:
                st.sidebar.error(f"Simülasyon hatası: {e}")

            # 4. İndirme Butonu
            st.sidebar.markdown("---")
            st.sidebar.download_button(
                label="JSON İndir",
                data=json_string,
                file_name="rover_mission_path.json",
                mime="application/json"
            )
        else:
            st.sidebar.error("❌ Yol bulunamadı! Rover İçin Uygun Zemin Seçin")


# İşaretçiler
draw = ImageDraw.Draw(draw_img)
for i, pt in enumerate(st.session_state.points):
    color = "blue" if i == 0 else "yellow"
    px, py = pt[0] * sw, pt[1] * sh
    draw.ellipse([(px-10, py-10), (px+10, py+10)], fill=color, outline="white", width=3)

# --- 🖱️ INTERAKTİF PANEL ---
st.subheader(f"Şu anki Mod: {algo_choice}")
display_width = 1000
value = streamlit_image_coordinates(draw_img, width=display_width)

if value:
    scale_x = W / display_width
    scale_y = H / (display_width * (H / W))
    new_pt = (int((value["x"] * scale_x) / sw), int((value["y"] * scale_y) / sh))
    
    if len(st.session_state.points) < 2:
        if len(st.session_state.points) == 0 or new_pt != st.session_state.points[-1]:
            st.session_state.points.append(new_pt)
            st.rerun()