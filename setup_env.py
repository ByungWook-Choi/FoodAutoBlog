import os
import urllib.request
from config import FONT_PATH, FONT_URL, FONTS_DIR
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

def ensure_korean_font():
    """
    Ensures NanumGothic font is downloaded and registered in matplotlib.
    This works on both Linux (GitHub Actions) and Windows without system installation.
    """
    if not os.path.exists(FONT_PATH):
        print(f"Downloading Korean font to {FONT_PATH}...")
        os.makedirs(FONTS_DIR, exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        print("Font downloaded successfully.")
        
    # Add font to Matplotlib font manager
    fm.fontManager.addfont(FONT_PATH)
    
    # Set it as the default font
    prop = fm.FontProperties(fname=FONT_PATH)
    plt.rc('font', family=prop.get_name())
    plt.rcParams['axes.unicode_minus'] = False # Fix minus sign rendering

    print(f"Matplotlib default font set to: {prop.get_name()}")
    
if __name__ == "__main__":
    ensure_korean_font()
