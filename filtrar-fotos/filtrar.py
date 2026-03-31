import os
import shutil
import sys
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from skimage import color

# ... (Mantenemos el diccionario THEMES del paso anterior) ...

# DICCIONARIO DE PALETAS (Esencias Linux)
THEMES = {
    "rose-pine-moon": {
        "base": [(35, 33, 54), (43, 41, 61)],
        "accents": [(156, 143, 163), (234, 154, 151), (196, 167, 231), (246, 193, 119), (234, 105, 118), (62, 143, 176), (156, 207, 216)]
    },
    "gruvbox": {
        "base": [(40, 40, 40), (60, 56, 54)],
        "accents": [(204, 36, 29), (152, 151, 26), (215, 153, 33), (69, 133, 136), (177, 98, 134), (104, 157, 106), (168, 153, 132)]
    },
    "nord": {
        "base": [(46, 52, 64), (59, 66, 82)],
        "accents": [(143, 188, 187), (136, 192, 208), (129, 161, 193), (94, 129, 172), (191, 97, 106), (208, 135, 112), (235, 203, 139), (163, 190, 140), (180, 142, 173)]
    },
    "catppuccin-mocha": {
        "base": [(30, 30, 46), (17, 17, 27)],
        "accents": [(245, 194, 231), (203, 166, 247), (237, 135, 150), (238, 153, 160), (245, 169, 127), (238, 212, 159), (166, 227, 161), (148, 226, 213)]
    },
    "dracula": {
        "base": [(40, 42, 54), (68, 71, 90)],
        "accents": [(255, 121, 198), (189, 147, 249), (139, 233, 253), (80, 250, 123), (241, 250, 140), (255, 184, 108), (255, 85, 85)]
    },
    # --- PALETAS CLARAS (LIGHT MODE) ---
    "catppuccin-latte": {
        "base": [(239, 241, 245), (230, 233, 239)], # Base y Mantle
        "accents": [(210, 15, 57), (254, 100, 11), (223, 142, 29), (64, 160, 43), (4, 165, 229), (30, 102, 245), (136, 57, 239)]
    },
    "rose-pine-dawn": {
        "base": [(250, 244, 237), (255, 250, 243)], # Base y Surface
        "accents": [(121, 117, 147), (215, 130, 126), (144, 122, 169), (234, 157, 52), (180, 99, 122), (40, 105, 131), (86, 148, 159)]
    },
    "everforest-light": {
        "base": [(251, 241, 199), (248, 235, 189)], # Soft y Medium Cream
        "accents": [(248, 85, 81), (141, 161, 44), (223, 162, 2), (53, 117, 117), (223, 123, 145), (147, 114, 149), (76, 80, 82)]
    },
    "gruvbox-light": {
        "base": [(251, 241, 199), (235, 219, 178)],
        "accents": [(157, 0, 6), (121, 116, 14), (181, 118, 20), (7, 102, 120), (143, 63, 113), (66, 123, 88), (146, 131, 116)]
    },
}

def to_lab(rgb_list):
    """Convierte una lista de tuplas RGB (0-255) a espacio de color LAB."""
    return [color.rgb2lab(np.array([[c]], dtype=float)/255.0)[0][0] for c in rgb_list]

def calculate_purity(image_path, theme_name):
    theme = THEMES[theme_name]
    bases_lab = to_lab(theme['base'])
    accents_lab = to_lab(theme['accents'])
    all_lab = bases_lab + accents_lab
    is_light = bases_lab[0][0] > 60

    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB').resize((80, 80))
            pixels_rgb = np.array(img).reshape(-1, 3) / 255.0
            pixels_lab = color.rgb2lab(pixels_rgb.reshape(-1, 1, 3)).reshape(-1, 3)
            
            # 1. Puntaje de Fondo (Dominancia)
            base_hits = 0
            for p_lab in pixels_lab:
                dist_to_base = min([np.linalg.norm(p_lab - b) for b in bases_lab])
                if is_light and p_lab[0] > 65 and dist_to_base < 18: base_hits += 1
                elif not is_light and p_lab[0] < 45 and dist_to_base < 15: base_hits += 1
            
            base_score = min(1.0, (base_hits / len(pixels_lab)) / 0.5) * 50 # Max 50 pts

            # 2. Puntaje de Acentos (Cromatismo)
            kmeans = KMeans(n_clusters=6, n_init=3).fit(pixels_rgb)
            centers_lab = color.rgb2lab(kmeans.cluster_centers_.reshape(-1, 1, 3)).reshape(-1, 3)
            
            accent_hits = 0
            penalty = 0
            for c_lab in centers_lab:
                dists = [np.linalg.norm(c_lab - a) for a in accents_lab]
                min_dist = min(dists)
                
                if min_dist < 20:
                    accent_hits += 1
                elif c_lab[0] > 20 and min_dist > 45: # Color intruso chillón
                    penalty += 15

            accent_score = min(1.0, accent_hits / 2) * 50 # Max 50 pts
            
            total_purity = max(0, min(100, int(base_score + accent_score - penalty)))
            return total_purity
    except:
        return 0

def run_purity_filter(folder, theme):
    if theme not in THEMES:
        print(f"Temas: {list(THEMES.keys())}")
        return

    out = os.path.join(folder, f"essence_{theme}")
    os.makedirs(out, exist_ok=True)
    
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"--- Analizando pureza para: {theme.upper()} ---")

    for f in files:
        purity = calculate_purity(os.path.join(folder, f), theme)
        
        # Solo guardamos si tiene más del 60% de pureza (ajustable)
        if purity >= 60:
            new_name = f"[{purity}%]{f}"
            shutil.copy(os.path.join(folder, f), os.path.join(out, new_name))
            print(f"💎 {purity}% - {f}")
        else:
            print(f"❌ {purity}% - {f} (Descartado)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python script.py <carpeta> <tema>")
    else:
        run_purity_filter(sys.argv[1], sys.argv[2])
