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
    # מרכוז ארצי מלא עם זום היקפי
    m = folium.Map(location=[31.5, 34.85], zoom_start=8, control_scale=True)
    
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # פונקציה חכמה שקובעת את צבע הנכס לפי הסוג שלו בתוך ה-GeoJSON
        def style_by_property(feature):
            prop_type = feature['properties'].get('type', '').lower()
            
            # הגדרת צבעים (מתואם לריבוע ה-Legend שבאתר שלך)
            if 'presale' in prop_type or 'פריסייל' in prop_type:
                color = '#ffc107'  # צהוב/אמבר לפריסייל
            elif 'pinui' in prop_type or 'פינוי' in prop_type or 'התחדשות' in prop_type:
                color = '#6f42c1'  # סגול לפינוי בינוי / התחדשות עירונית
            else:
                color = '#1D4ED8'  # כחול ברירת מחדל לנכסים רגילים/זמינים
                
            return {
                'fillColor': color,
                'color': color,
                'weight': 2,
                'fillOpacity': 0.6
            }
        
        folium.GeoJson(
            geojson_data,
            name="שכבות נדלן ארציות",
            style_function=style_by_property,
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "type"], 
                aliases=["שם נכס/מגרש:", "סוג עסקה:"], 
                localize=True
            ),
            popup=folium.GeoJsonPopup(
                fields=["description"], 
                aliases=["סטטוס משפטי:"], 
                localize=True
            )
        ).add_to(m)
        
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