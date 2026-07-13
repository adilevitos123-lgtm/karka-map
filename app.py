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
    # יצירת המפה במיקוד ארצי מלא (מרכז המדינה, זום רחב)
    m = folium.Map(location=[31.5, 34.85], zoom_start=8, control_scale=True)
    
    # 1. חיבור ל-API הרשמי של התחדשות עירונית (פינוי בינוי ותמ"א) - מינהל התכנון
    # משתמשים בשירות מפות דינמי מבוסס Esri שלא נחסם בדפדפנים
    folium.TileLayer(
        tiles='https://gis.inter.moin.gov.il/arcgis/rest/services/Xplan/MapServer/tile/{z}/{y}/{x}',
        attr='מינהל התכנון - התחדשות עירונית',
        name='התחדשות עירונית ופינוי בינוי (ארצי)',
        overlay=True,
        control=True,
        show=True,
        opacity=0.75
    ).add_to(m)

    # 2. חיבור ל-API של שכבת מבנים לשימור ומבנים מסוכנים הרשמית
    folium.TileLayer(
        tiles='https://gis.inter.moin.gov.il/arcgis/rest/services/Public/MapServer/tile/{z}/{y}/{x}',
        attr='מערכת GIS לאומית - מבנים לשימור ומסוכנים',
        name='מבנים לשימור ומסוכנים',
        overlay=True,
        control=True,
        show=True,
        opacity=0.7
    ).add_to(m)

    # במידה ויש לך קובץ מקומי של עסקאות פריסייל/בלעדיות שלך, נטען אותו בצבע ייחודי
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        folium.GeoJson(
            geojson_data,
            name="פרויקטים ופריסייל בלעדיים",
            style_function=lambda x: {
                'fillColor': '#ffc107', # צבע אמבר/צהוב לפי מפתח הצבעים באתר שלך
                'color': '#ffc107',
                'weight': 2,
                'fillOpacity': 0.6
            }
        ).add_to(m)

    # הוספת תפריט בורר השכבות בפינה הימנית העליונה של המפה
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