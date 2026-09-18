"""
generate_assets.py - Generate crisp modern SVG item icons for seed data
"""
import os

os.makedirs("static/images/items", exist_ok=True)

svgs = {
    "laptop_bag.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="strapGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#334155"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" rx="24" fill="#0f172a"/>
  <!-- Handle -->
  <path d="M75 55 C75 35 125 35 125 55" stroke="#475569" stroke-width="8" fill="none" stroke-linecap="round"/>
  <!-- Bag Body -->
  <rect x="40" y="55" width="120" height="100" rx="14" fill="url(#bgGrad)" stroke="#38bdf8" stroke-width="2.5"/>
  <!-- Front pocket -->
  <rect x="52" y="95" width="96" height="50" rx="8" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
  <!-- Zipper line -->
  <line x1="52" y1="85" x2="148" y2="85" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 2"/>
  <!-- Red keychain / tag -->
  <circle cx="145" cy="85" r="4" fill="#ef4444"/>
  <rect x="143" y="89" width="4" height="20" rx="2" fill="#ef4444"/>
  <!-- HP logo badge -->
  <circle cx="100" cy="120" r="14" fill="#0284c7"/>
  <text x="100" y="125" font-family="sans-serif" font-weight="900" font-size="12" fill="#ffffff" text-anchor="middle" font-style="italic">hp</text>
</svg>""",

    "silver_laptop.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="screenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1e2e"/>
      <stop offset="100%" stop-color="#11111b"/>
    </linearGradient>
    <linearGradient id="metalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#e2e8f0"/>
      <stop offset="50%" stop-color="#cbd5e1"/>
      <stop offset="100%" stop-color="#94a3b8"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" rx="24" fill="#0f172a"/>
  <!-- Screen Lid -->
  <rect x="42" y="42" width="116" height="80" rx="8" fill="url(#metalGrad)" stroke="#64748b" stroke-width="2"/>
  <rect x="48" y="48" width="104" height="68" rx="4" fill="url(#screenGrad)"/>
  <!-- Terminal code on screen -->
  <line x1="56" y1="62" x2="85" y2="62" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
  <line x1="56" y1="72" x2="110" y2="72" stroke="#a855f7" stroke-width="2" stroke-linecap="round"/>
  <line x1="56" y1="82" x2="95" y2="82" stroke="#22c55e" stroke-width="2" stroke-linecap="round"/>
  <!-- Base Keyboard Base -->
  <path d="M25 125 L175 125 L165 145 L35 145 Z" fill="url(#metalGrad)" stroke="#64748b" stroke-width="1.5"/>
  <!-- Trackpad -->
  <rect x="85" y="132" width="30" height="9" rx="2" fill="#94a3b8"/>
  <!-- Octocat sticker -->
  <circle cx="132" cy="135" r="5" fill="#f43f5e"/>
  <text x="132" y="138" font-size="6" fill="#ffffff" text-anchor="middle">★</text>
  <!-- Base Bottom Notch -->
  <rect x="90" y="145" width="20" height="3" rx="1.5" fill="#64748b"/>
</svg>""",

    "airpods.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="caseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#e2e8f0"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" rx="24" fill="#0f172a"/>
  <!-- Silicone Sleeve (Blue) -->
  <rect x="52" y="60" width="96" height="88" rx="30" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
  <!-- Case Body -->
  <rect x="58" y="66" width="84" height="76" rx="24" fill="url(#caseGrad)"/>
  <!-- Lid Split Line -->
  <line x1="58" y1="92" x2="142" y2="92" stroke="#cbd5e1" stroke-width="2"/>
  <!-- LED Indicator light -->
  <circle cx="100" cy="104" r="3" fill="#22c55e"/>
  <!-- Astronaut Graphic -->
  <circle cx="100" cy="122" r="10" fill="#38bdf8"/>
  <circle cx="100" cy="120" r="5" fill="#0f172a"/>
  <path d="M96 122 Q100 126 104 122" stroke="#38bdf8" stroke-width="1.5" fill="none"/>
</svg>""",

    "calculator.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="24" fill="#0f172a"/>
  <!-- Calculator Body -->
  <rect x="55" y="32" width="90" height="136" rx="14" fill="#1e293b" stroke="#475569" stroke-width="2"/>
  <!-- Solar & LCD Screen -->
  <rect x="66" y="44" width="68" height="26" rx="4" fill="#94a3b8"/>
  <rect x="68" y="46" width="64" height="22" rx="2" fill="#a3e635" opacity="0.85"/>
  <text x="128" y="62" font-family="monospace" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="end">991.00</text>
  <!-- Keys Grid -->
  <g fill="#334155" stroke="#475569">
    <rect x="66" y="80" width="14" height="10" rx="2"/>
    <rect x="84" y="80" width="14" height="10" rx="2"/>
    <rect x="102" y="80" width="14" height="10" rx="2"/>
    <rect x="120" y="80" width="14" height="10" rx="2"/>
    
    <rect x="66" y="96" width="14" height="10" rx="2"/>
    <rect x="84" y="96" width="14" height="10" rx="2"/>
    <rect x="102" y="96" width="14" height="10" rx="2"/>
    <rect x="120" y="96" width="14" height="10" rx="2"/>

    <rect x="66" y="112" width="14" height="10" rx="2" fill="#0284c7"/>
    <rect x="84" y="112" width="14" height="10" rx="2" fill="#0284c7"/>
    <rect x="102" y="112" width="14" height="10" rx="2" fill="#0284c7"/>
    <rect x="120" y="112" width="14" height="10" rx="2" fill="#f43f5e"/>

    <rect x="66" y="128" width="14" height="10" rx="2"/>
    <rect x="84" y="128" width="14" height="10" rx="2"/>
    <rect x="102" y="128" width="14" height="10" rx="2"/>
    <rect x="120" y="128" width="14" height="10" rx="2"/>
    
    <rect x="66" y="144" width="32" height="10" rx="2"/>
    <rect x="102" y="144" width="32" height="10" rx="2" fill="#10b981"/>
  </g>
  <!-- Hand marked RN -->
  <text x="135" y="162" font-family="sans-serif" font-size="7" font-weight="bold" fill="#facc15">RN</text>
</svg>""",

    "water_bottle.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="24" fill="#0f172a"/>
  <!-- Cap & Handle -->
  <rect x="86" y="28" width="28" height="16" rx="4" fill="#334155"/>
  <path d="M100 28 C85 28 85 16 100 16 C115 16 115 28 100 28" stroke="#334155" stroke-width="5" fill="none" stroke-linecap="round"/>
  <!-- Neck -->
  <rect x="82" y="44" width="36" height="14" rx="2" fill="#1e293b"/>
  <!-- Flask Body (Cobalt Blue) -->
  <rect x="68" y="58" width="64" height="114" rx="18" fill="#1d4ed8" stroke="#3b82f6" stroke-width="2"/>
  <!-- Highlight shine -->
  <path d="M76 68 L76 158" stroke="#60a5fa" stroke-width="4" stroke-linecap="round" opacity="0.6"/>
  <!-- Bottom Dent detail -->
  <path d="M116 166 Q122 168 126 164" stroke="#0f172a" stroke-width="3" fill="none"/>
  <!-- Hydro Flask logo silhouette -->
  <circle cx="100" cy="105" r="8" fill="#ffffff" opacity="0.9"/>
  <path d="M96 117 Q100 120 104 117" stroke="#ffffff" stroke-width="2" fill="none"/>
</svg>""",

    "id_card.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="24" fill="#0f172a"/>
  <!-- Lanyard String -->
  <path d="M100 10 L100 48" stroke="#3b82f6" stroke-width="8"/>
  <rect x="92" y="48" width="16" height="10" rx="2" fill="#94a3b8"/>
  <!-- Badge Card -->
  <rect x="45" y="56" width="110" height="124" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>
  <!-- Top Blue Band -->
  <rect x="45" y="56" width="110" height="28" rx="8" fill="#1e3a8a"/>
  <text x="100" y="74" font-family="sans-serif" font-weight="bold" font-size="9" fill="#ffffff" text-anchor="middle">CAMPUS ID</text>
  <!-- Photo Avatar -->
  <rect x="58" y="92" width="36" height="42" rx="4" fill="#e2e8f0"/>
  <circle cx="76" cy="106" r="8" fill="#94a3b8"/>
  <path d="M64 130 C64 120 88 120 88 130" fill="#94a3b8"/>
  <!-- Details lines -->
  <line x1="102" y1="96" x2="145" y2="96" stroke="#0f172a" stroke-width="3"/>
  <line x1="102" y1="106" x2="135" y2="106" stroke="#64748b" stroke-width="2"/>
  <line x1="102" y1="116" x2="140" y2="116" stroke="#64748b" stroke-width="2"/>
  <line x1="102" y1="126" x2="130" y2="126" stroke="#2563eb" stroke-width="2"/>
  <!-- Barcode -->
  <g fill="#0f172a">
    <rect x="58" y="148" width="3" height="18"/>
    <rect x="64" y="148" width="6" height="18"/>
    <rect x="73" y="148" width="2" height="18"/>
    <rect x="78" y="148" width="5" height="18"/>
    <rect x="86" y="148" width="4" height="18"/>
    <rect x="93" y="148" width="2" height="18"/>
    <rect x="98" y="148" width="7" height="18"/>
    <rect x="108" y="148" width="3" height="18"/>
    <rect x="114" y="148" width="5" height="18"/>
    <rect x="122" y="148" width="2" height="18"/>
    <rect x="127" y="148" width="6" height="18"/>
    <rect x="136" y="148" width="4" height="18"/>
  </g>
</svg>"""
}

for filename, content in svgs.items():
    with open(os.path.join("static/images/items", filename), "w", encoding="utf-8") as f:
        f.write(content.strip())

print("All SVG assets successfully created.")
