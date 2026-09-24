from typing import Dict

THEMES: Dict[str, dict] = {
    "catppuccin_mocha": {
        "name": "Catppuccin Mocha (Pastel Dark)",
        "accent": "#cba6f7",          # Mauve
        "accent_secondary": "#89b4fa",# Blue
        "accent_glow": "rgba(203, 166, 247, 0.4)",
        "bg_glass": "rgba(30, 30, 46, {opacity})",   # Base
        "bg_card": "rgba(24, 24, 37, 0.78)",         # Mantle
        "bg_active_card": "rgba(203, 166, 247, 0.22)",
        "border_color": "rgba(203, 166, 247, 0.35)",
        "border_active": "#cba6f7",
        "text_primary": "#cdd6f4",     # Text
        "text_secondary": "#b4befe",   # Lavender
        "text_muted": "#6c7086",       # Overlay0
        "alert_now": "#f38ba8",        # Red
        "warning_soon": "#fab387",     # Peach
    },
    "catppuccin_macchiato": {
        "name": "Catppuccin Macchiato (Warm Dark)",
        "accent": "#f5a97f",          # Peach
        "accent_secondary": "#eed49f",# Yellow
        "accent_glow": "rgba(245, 169, 127, 0.4)",
        "bg_glass": "rgba(36, 39, 58, {opacity})",   # Base
        "bg_card": "rgba(30, 32, 48, 0.78)",         # Mantle
        "bg_active_card": "rgba(245, 169, 127, 0.22)",
        "border_color": "rgba(245, 169, 127, 0.35)",
        "border_active": "#f5a97f",
        "text_primary": "#cad3f5",
        "text_secondary": "#f4dbd6",
        "text_muted": "#6e738d",
        "alert_now": "#ed8796",
        "warning_soon": "#eed49f",
    },
    "catppuccin_latte": {
        "name": "Catppuccin Latte (Light Pastel)",
        "accent": "#8839ef",          # Mauve
        "accent_secondary": "#1e66f5",# Blue
        "accent_glow": "rgba(136, 57, 239, 0.3)",
        "bg_glass": "rgba(239, 241, 245, {opacity})",
        "bg_card": "rgba(230, 233, 239, 0.88)",
        "bg_active_card": "rgba(136, 57, 239, 0.18)",
        "border_color": "rgba(136, 57, 239, 0.35)",
        "border_active": "#8839ef",
        "text_primary": "#4c4f69",
        "text_secondary": "#7287fd",
        "text_muted": "#9ca0b0",
        "alert_now": "#d20f39",
        "warning_soon": "#df8e1d",
    },
    "cyber_cyan": {
        "name": "Cyber Cyan (Default HUD)",
        "accent": "#00f3ff",
        "accent_secondary": "#0099ff",
        "accent_glow": "rgba(0, 243, 255, 0.4)",
        "bg_glass": "rgba(10, 16, 26, {opacity})",
        "bg_card": "rgba(15, 23, 42, 0.65)",
        "bg_active_card": "rgba(0, 243, 255, 0.16)",
        "border_color": "rgba(0, 243, 255, 0.35)",
        "border_active": "#00f3ff",
        "text_primary": "#f0fdff",
        "text_secondary": "#7dd3fc",
        "text_muted": "#475569",
        "alert_now": "#ff3366",
        "warning_soon": "#ffaa00",
    },
    "msi_amber": {
        "name": "MSI Amber (Hardware Monitor)",
        "accent": "#ffaa00",
        "accent_secondary": "#ff6600",
        "accent_glow": "rgba(255, 170, 0, 0.4)",
        "bg_glass": "rgba(18, 14, 10, {opacity})",
        "bg_card": "rgba(35, 25, 15, 0.65)",
        "bg_active_card": "rgba(255, 170, 0, 0.18)",
        "border_color": "rgba(255, 170, 0, 0.35)",
        "border_active": "#ffaa00",
        "text_primary": "#fffbf0",
        "text_secondary": "#fcd34d",
        "text_muted": "#786047",
        "alert_now": "#ff2244",
        "warning_soon": "#ffd700",
    },
    "emerald_green": {
        "name": "Emerald Matrix (Islamic Cyber)",
        "accent": "#00ff88",
        "accent_secondary": "#10b981",
        "accent_glow": "rgba(0, 255, 136, 0.4)",
        "bg_glass": "rgba(8, 20, 16, {opacity})",
        "bg_card": "rgba(12, 32, 24, 0.65)",
        "bg_active_card": "rgba(0, 255, 136, 0.18)",
        "border_color": "rgba(0, 255, 136, 0.35)",
        "border_active": "#00ff88",
        "text_primary": "#f0fdf4",
        "text_secondary": "#6ee7b7",
        "text_muted": "#3f6251",
        "alert_now": "#ff3366",
        "warning_soon": "#ffbb00",
    },
    "stealth_crimson": {
        "name": "Stealth Crimson (Rogue Cyber)",
        "accent": "#ff2a5f",
        "accent_secondary": "#e11d48",
        "accent_glow": "rgba(255, 42, 95, 0.4)",
        "bg_glass": "rgba(20, 10, 14, {opacity})",
        "bg_card": "rgba(36, 16, 24, 0.65)",
        "bg_active_card": "rgba(255, 42, 95, 0.20)",
        "border_color": "rgba(255, 42, 95, 0.35)",
        "border_active": "#ff2a5f",
        "text_primary": "#fff1f2",
        "text_secondary": "#fda4af",
        "text_muted": "#6b4f59",
        "alert_now": "#ff003c",
        "warning_soon": "#ffaa00",
    },
}

def get_theme(theme_name: str, opacity: float = 0.92) -> dict:
    th = THEMES.get(theme_name, THEMES["cyber_cyan"]).copy()
    th["bg_glass"] = th["bg_glass"].format(opacity=f"{opacity:.2f}")
    return th

def get_overlay_stylesheet(theme_dict: dict) -> str:
    """Generates the QSS stylesheet for the HUD overlay window."""
    return f"""
    #HUDContainer {{
        background-color: {theme_dict["bg_glass"]};
        border: 1px solid {theme_dict["border_color"]};
        border-radius: 8px;
    }}
    
    #TopDragBar {{
        background: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }}
    
    #AppTitle {{
        color: {theme_dict["accent"]};
        font-family: 'Consolas', 'Cascadia Code', 'Segoe UI', monospace;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1.5px;
    }}
    
    #StatusBadge {{
        color: {theme_dict["text_secondary"]};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 10px;
    }}
    
    #NextPrayerTitle {{
        color: {theme_dict["text_muted"]};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 2px;
    }}
    
    #NextPrayerValue {{
        color: {theme_dict["accent"]};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 19px;
        font-weight: 900;
        letter-spacing: 1px;
    }}
    
    #CountdownDisplay {{
        color: {theme_dict["text_primary"]};
        font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 2px;
    }}
    
    #CountdownDisplay[isWarning="true"] {{
        color: {theme_dict["warning_soon"]};
    }}
    
    #CountdownDisplay[isAlert="true"] {{
        color: {theme_dict["alert_now"]};
    }}
    
    #AlertBanner {{
        background-color: {theme_dict["alert_now"]};
        color: #ffffff;
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1.5px;
        padding: 3px 6px;
        border-radius: 4px;
    }}
    
    /* Individual Prayer Cards */
    .PrayerCard {{
        background-color: {theme_dict["bg_card"]};
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 5px;
        padding: 4px 6px;
    }}
    
    .PrayerCard[isNext="true"] {{
        background-color: {theme_dict["bg_active_card"]};
        border: 1px solid {theme_dict["border_active"]};
    }}
    
    .PrayerCard[isPast="true"] {{
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.03);
    }}
    
    .PrayerCardName {{
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 9px;
        font-weight: bold;
        letter-spacing: 0.8px;
        color: {theme_dict["text_secondary"]};
    }}
    
    .PrayerCardName[isNext="true"] {{
        color: {theme_dict["accent"]};
    }}
    
    .PrayerCardName[isPast="true"] {{
        color: {theme_dict["text_muted"]};
    }}
    
    .PrayerCardTime {{
        font-family: 'Consolas', 'Cascadia Code', monospace;
        font-size: 13px;
        font-weight: bold;
        color: {theme_dict["text_primary"]};
    }}
    
    .PrayerCardTime[isNext="true"] {{
        color: {theme_dict["accent"]};
    }}
    
    .PrayerCardTime[isPast="true"] {{
        color: {theme_dict["text_muted"]};
    }}
    
    /* Footer & Controls */
    #FooterBar {{
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}
    
    #DateLabel {{
        color: {theme_dict["text_muted"]};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 10px;
    }}
    
    #TimeLabel {{
        color: {theme_dict["text_secondary"]};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 10px;
        font-weight: bold;
    }}
    
    /* Header Buttons */
    QPushButton#HeaderBtn {{
        background-color: rgba(30, 41, 59, 0.85);
        color: {theme_dict["text_primary"]};
        border: 1px solid {theme_dict["border_color"]};
        border-radius: 4px;
        font-family: 'Segoe UI', 'Consolas', sans-serif;
        font-size: 11px;
        font-weight: bold;
        padding: 2px 4px;
    }}
    
    QPushButton#HeaderBtn:hover {{
        background-color: {theme_dict["accent"]};
        color: #0f172a;
        border: 1px solid {theme_dict["accent"]};
    }}
    
    QPushButton#HeaderBtn:pressed {{
        background-color: {theme_dict["accent_secondary"]};
        color: #ffffff;
    }}

    #ThirdNightLabel {{
        color: {theme_dict["text_secondary"]};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 10px;
        padding: 2px 4px;
    }}
    
    #ThirdNightLabel[isActive="true"] {{
        color: #00ff88;
        font-weight: bold;
        background-color: rgba(0, 255, 136, 0.12);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 4px;
    }}
    
    /* General Buttons */
    QToolButton, QPushButton {{
        background-color: transparent;
        color: {theme_dict["text_secondary"]};
        border: none;
        border-radius: 4px;
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 11px;
        padding: 2px 4px;
    }}
    """
