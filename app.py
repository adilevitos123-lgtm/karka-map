import sqlite3
import folium
import json
import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

@app.route('/api/search')
def api_search():
    gush = request.args.get('gush')
    chelka = request.args.get('chelka')
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            if props.get('gush') == gush and props.get('chelka') == chelka:
                return jsonify({"status": "success", "feature": feature})
    return jsonify({"status": "not_found"})

@app.route('/map-only')
def map_only():
    # יצירת מפה ארצית חלקה
    m = folium.Map(location=[31.5, 34.85], zoom_start=8, control_scale=True)
    
    # 1. חיבור לשכבת התחדשות עירונית / פינוי בינוי מ-GIS משרד השיכון והבינוי
    folium.WmsTileLayer(
        url="https://wms.gov.il/govmap/wms",
        layers="URBAN_RENEWAL",
        fmt="image/png",
        transparent=True,
        name="התחדשות עירונית / פינוי בינוי",
        overlay=True,
        show=True
    ).add_to(m)

    # 2. חיבור לשכבת מבנים לשימור ומבנים מסוכנים (מערכת תכנון ארצית של מינהל התכנון)
    folium.WmsTileLayer(
        url="https://gis.inter.moin.gov.il/arcgis/services/Xplan/MapServer/WMSServer",
        layers="Preservation_Buildings,Dangerous_Buildings",
        fmt="image/png",
        transparent=True,
        name="מבנים לשימור ומסוכנים",
        overlay=True,
        show=True
    ).add_to(m)

    # אם קיים קובץ מקומי עבור עסקאות פריסייל מיוחדות שלך, נטען גם אותו
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        def style_by_property(feature):
            prop_type = feature['properties'].get('type', '').lower()
            if 'presale' in prop_type or 'פריסייל' in prop_type:
                return {'fillColor': '#ffc107', 'color': '#ffc107', 'weight': 2, 'fillOpacity': 0.6}
            return {'fillColor': '#1D4ED8', 'color': '#1D4ED8', 'weight': 1, 'fillOpacity': 0.4}

        folium.GeoJson(
            geojson_data,
            name="פרויקטים ופריסייל בלעדיים",
            style_function=style_by_property,
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["שם:"], localize=True)
        ).add_to(m)

    # הוספת בורר שכבות בפינת המפה שמאפשר למשתמש להדליק/לכבות כל שכבה
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    return m._repr_html_()

@app.route('/')
def map_home():
    premium_file_path = 'karka-premium-2026.html'
    if os.path.exists(premium_file_path):
        with open(premium_file_path, 'r', encoding='utf-8') as f:
            html_page = f.read()
        return render_template_string(html_page)
    return "Error: File not found."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)