import sqlite3
import folium
import json
import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

def get_saved_layers():
    layers = []
    try:
        conn = sqlite3.connect('karka.db')
        c = conn.cursor()
        query = "SELECT label, layer_name FROM layers WHERE layer_name IN ('mivnim_leShimur', 'parcels', 'tama8_pol_expire', 'Mivnim')"
        layers = c.execute(query).fetchall()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
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

@app.route('/map-only')
def map_only():
    # יצירת המפה המדויקת שממוקדת ישירות בפרדס חנה ומאפשרת זום חופשי
    m = folium.Map(location=[32.4833, 34.9833], zoom_start=14, control_scale=True)
    
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        folium.GeoJson(
            geojson_data,
            name="שכבות נדלן חמות",
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["שם נכס/מגרש:"], localize=True),
            popup=folium.GeoJsonPopup(fields=["description"], aliases=["סטטוס משפטי:"], localize=True)
        ).add_to(m)
        
    return m._repr_html_()

@app.route('/')
def map_home():
    premium_file_path = 'karka-premium-2026.html'
    if os.path.exists(premium_file_path):
        with open(premium_file_path, 'r', encoding='utf-8') as f:
            html_page = f.read()
        
        iframe_tag = '<iframe src="/map-only" style="width:100%; height:100%; border:none; overflow:hidden;"></iframe>'
        
        # פתרון חלופי וגורף: נחפש את ה-mapContainer בכל וריאציה אפשרית ונזריק לתוכו את המפה החדשה
        if 'id="mapContainer"' in html_page:
            # פירוק ה-HTML לשני חלקים בדיוק במקום שבו האלמנט מתחיל, והזרקת המפה פנימה
            parts = html_page.split('id="mapContainer"', 1)
            # מציאה של סגירת התגית > הראשונה שאחרי ה-ID והזרקת ה-iframe מיד אחריה
            subparts = parts[1].split('>', 1)
            html_page = parts[0] + 'id="mapContainer"' + subparts[0] + '>' + iframe_tag + subparts[1]
            
        return render_template_string(html_page)
    else:
        return f"Error: {premium_file_path} not found."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)