import json

geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "בית הראשונים - מבנה לשימור",
                "description": "נכס היסטורי לשימור, לב המושבה פרדס חנה.",
                "type": "שימור",
                "gush": "10020",
                "chelka": "45"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [34.9854, 32.4812]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "name": "מתחם חלקה חמה - מרכז כרכור",
                "description": "פוטנציאל פינוי בינוי / תמ\"א 8 פקעה.",
                "type": "הזדמנות",
                "gush": "10025",
                "chelka": "12"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [34.9912, 32.4845]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "name": "גוש 10022 חלקה 80",
                "description": "קרקע בייעוד מגורים א'. זכויות בניה לא מנוצלות.",
                "type": "חלקה",
                "gush": "10022",
                "chelka": "80"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [34.9820, 32.4820],
                    [34.9840, 32.4820],
                    [34.9840, 32.4840],
                    [34.9820, 32.4840],
                    [34.9820, 32.4820]
                ]]
            }
        }
    ]
}

with open('layers_data.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=4)

print("קובץ המידע המורחב נוצר בהצלחה!")