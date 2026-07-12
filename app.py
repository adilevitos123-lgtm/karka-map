import sqlite3
import folium
import json
import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

def get_saved_layers():
    layers = []
    try:
        conn = sqlite3.connect('karka')
        c = conn.cursor()
        query = "SELECT label, layer_name FROM layers WHERE layer_name IN ('mivnim_leShimur', 'parcels', 'tama8_pol_expire', 'Mivnim')"
        layers = c.execute(query).fetchall()
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
    return layers

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
                
    return jsonify({"status": "not_found", "message": "חלקה לא נמצאה באזור פרדס חנה"})

@app.route('/')
def map_home():
    # יצירת המפה עם הגדרות מלאות שמאפשרות זום ותזוזה חלקה
    m = folium.Map(
        location=[32.4833, 34.9833], 
        zoom_start=14, 
        control_scale=True,
        zoom_control=True,
        scrollWheelZoom=True,
        dragging=True
    )
    
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        folium.GeoJson(
            geojson_data,
            name="שכבות נדלן חמות",
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["שם נכס/מגרש:"], localize=True),
            popup=folium.GeoJsonPopup(fields=["description"], aliases=["סטטוס משפטי:"], localize=True)
        ).add_to(m)

    m.get_root().html.add_child(folium.Element("<script>window.mymap = null;</script>"))
    
    # הגדרת רוחב וגובה של 100% למפה הפנימית כדי שלא תיחתך על ידי ה-CSS של אתר הפרימיום
    m.branca_by_id['folium_id'].width = '100%'
    m.branca_by_id['folium_id'].height = '100%'
    
    map_html = m._repr_html_()
    map_html = map_html.replace('var map_', 'window.mymap = map_')
    map_html = map_html.replace('L.map(\'map_', 'window.mymap = L.map(\'map_')

    premium_file_path = 'karka-premium-2026.html'
    if os.path.exists(premium_file_path):
        with open(premium_file_path, 'r', encoding='utf-8') as f:
            html_page = f.read()
        
        # החלפה חכמה של הדיב כולל סגירתו כדי למנוע כפל אלמנטים שחוסם את חווית המשתמש
        if 'id="mapContainer"></div>' in html_page:
            html_page = html_page.replace('id="mapContainer"></div>', f'id="mapContainer" style="position:relative; overflow:visible;">{map_html}</div>')
        elif 'id="mapContainer">' in html_page:
            html_page = html_page.replace('id="mapContainer">', f'id="mapContainer" style="position:relative; overflow:visible;">{map_html}')
        
        return render_template_string(html_page)
    else:
        return f"שגיאה: הקובץ {premium_file_path} לא נמצא."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)