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
        print(f"שגיאה בקריאת בסיס הנתונים: {e}")
    return layers

@app.route('/api/search')
def api_search():
    """נקודת קצה לחיפוש חלקה לפי גוש וחלקה מתוך הנתונים"""
    gush = request.args.get('gush')
    chelka = request.args.get('chelka')
    
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            if props.get('gush') == gush and props.get('chelka') == chelka:
                # מחזיר את המאפיינים והגיאומטריה של החלקה שנמצאה
                return jsonify({"status": "success", "feature": feature})
                
    return jsonify({"status": "not_found", "message": "חלקה לא נמצאה באזור פרדס חנה"})

@app.route('/')
def map_home():
    # יצירת מפה ממוקדת על פרדס חנה
    m = folium.Map(location=[32.4833, 34.9833], zoom_start=14, control_scale=True)
    
    if os.path.exists('layers_data.geojson'):
        with open('layers_data.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # צביעת פוליגונים של חלקות ונקודות עניין
        folium.GeoJson(
            geojson_data,
            name="שכבות נדלן חמות",
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["שם נכס/מגרש:"], localize=True),
            popup=folium.GeoJsonPopup(fields=["description"], aliases=["סטטוס משפטי:"], localize=True)
        ).add_to(m)

    # יצירת משתנה מפה ייחודי ל-JavaScript כדי שנוכל לשלוט בה מבחוץ
    m.get_root().html.add_child(folium.Element("<script>window.mymap = null;</script>"))
    map_html = m._repr_html_()
    
    # הזרקת מזהה המפה לתוך חלון ה-window של הדפדפן
    map_html = map_html.replace('var map_', 'window.mymap = map_')
    map_html = map_html.replace('L.map(\'map_', 'window.mymap = L.map(\'map_')

    db_layers = get_saved_layers()
    layers_html = ""
    for label, name in db_layers:
        layers_html += f'<div class="layer-item">{label} <span class="badge success">מחובר</span></div>'

    html_page = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>קרקע - מפת איתור הזדמנויות</title>
        <style>
            body {{ margin: 0; padding: 0; font-family: system-ui, sans-serif; display: flex; height: 100vh; }}
            .sidebar {{ width: 350px; background: #1e293b; color: white; padding: 25px; box-sizing: border-box; box-shadow: 2px 0 10px rgba(0,0,0,0.1); z-index: 1000; overflow-y: auto; }}
            .map-container {{ flex-grow: 1; height: 100%; }}
            h1 {{ color: #38bdf8; font-size: 24px; margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 15px; }}
            .search-box {{ background: #334155; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .search-box input {{ width: 100%; padding: 8px; margin: 5px 0 10px 0; border-radius: 4px; border: 1px solid #475569; background: #1e293b; color: white; box-sizing: border-box; }}
            .search-box button {{ width: 100%; padding: 10px; background: #0ea5e9; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
            .search-box button:hover {{ background: #0284c7; }}
            .layer-item {{ background: #334155; padding: 12px; margin: 10px 0; border-radius: 8px; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }}
            .badge {{ background: #0ea5e9; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
            .badge.success {{ background: #10b981; }}
            p {{ color: #94a3b8; font-size: 14px; }}
        </style>
        <script>
            async function searchParcel() {{
                const gush = document.getElementById('gush_input').value;
                const chelka = document.getElementById('chelka_input').value;
                if(!gush || !chelka) {{ alert('נא להזין גם גוש וגם חלקה'); return; }}
                
                const response = await fetch(`/api/search?gush=${{gush}}&chelka=${{chelka}}`);
                const data = await response.json();
                
                if(data.status === 'success') {{
                    const geom = data.feature.geometry;
                    let coords;
                    if(geom.type === 'Point') {{
                        coords = [geom.coordinates[1], geom.coordinates[0]];
                    }} else if(geom.type === 'Polygon') {{
                        // מציאת נקודת האמצע של הפוליגון לצורך התמרכזות
                        coords = [geom.coordinates[0][0][1], geom.coordinates[0][0][0]];
                    }}
                    
                    if(window.mymap) {{
                        // טיסה חלקה של המפה למיקום החלקה החדש
                        window.mymap.flyTo(coords, 17);
                        L.popup()
                            .setLatLng(coords)
                            .setContent(`<b>חלקה אותרה בהצלחה!</b><br>${{data.feature.properties.name}}<br>${{data.feature.properties.description}}`)
                            .openOn(window.mymap);
                    }}
                }} else {{
                    alert(data.message);
                }}
            }}
        </script>
    </head>
    <body>
        <div class="sidebar">
            <h1>מערכת קרקע</h1>
            
            <div class="search-box">
                <label>🔎 איתור חלקה בטאבו</label>
                <input type="text" id="gush_input" placeholder="הזן מספר גוש (לדוגמה: 10022)">
                <input type="text" id="chelka_input" placeholder="הזן מספר חלקה (לדוגמה: 80)">
                <button onclick="searchParcel()">חפש נכס במערכת</button>
            </div>

            <p>שכבות מנוע ממוקדות מתוך בסיס הנתונים:</p>
            {layers_html}
        </div>
        <div class="map-container">
            {map_html}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_page)

if __name__ == '__main__':
    # התאמת הפורט לסביבת ענן ציבורית
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)