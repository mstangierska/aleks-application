"""
Interactive Map Application for London Hospitals offering Haematology Rotations
Features:
- Hospital locations with Google ratings
- Commute times from various London neighborhoods
- Cost of living data (average 1 room in 2-bedroom flat)
- Number of room advertisements
- Rail/road works alerts
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import folium
from folium import plugins
import json
import random

app = Flask(__name__)
CORS(app)

# London hospitals with haematology rotations
HOSPITALS = {
    "Royal Free Hospital": {
        "trust": "Royal Free London NHS Foundation Trust",
        "area": "Hampstead",
        "postcode": "NW3 2QG",
        "lat": 51.5507,
        "lon": -0.1644,
        "google_rating": 3.3
    },
    "North Middlesex Hospital": {
        "trust": "Royal Free London NHS Foundation Trust",
        "area": "Edmonton",
        "postcode": "N18 1QX",
        "lat": 51.6147,
        "lon": -0.0639,
        "google_rating": 2.3
    },
    "University College Hospital": {
        "trust": "UCLH NHS Foundation Trust",
        "area": "Bloomsbury",
        "postcode": "NW1 2BU",
        "lat": 51.5246,
        "lon": -0.1340,
        "google_rating": 3.7
    },
    "St Bartholomew's Hospital": {
        "trust": "Barts Health NHS Trust",
        "area": "City of London",
        "postcode": "EC1A 7BE",
        "lat": 51.5184,
        "lon": -0.0998,
        "google_rating": 4
    },
    "Royal London Hospital": {
        "trust": "Barts Health NHS Trust",
        "area": "Whitechapel",
        "postcode": "E1 1FR",
        "lat": 51.5176,
        "lon": -0.0599,
        "google_rating": 3.1
    },
    "Whipps Cross Hospital": {
        "trust": "Barts Health NHS Trust",
        "area": "Leytonstone",
        "postcode": "E11 1NR",
        "lat": 51.5763,
        "lon": 0.0103,
        "google_rating": 2.7
    },
    "Hammersmith Hospital": {
        "trust": "Imperial College Healthcare NHS Trust",
        "area": "Hammersmith",
        "postcode": "W12 0HS",
        "lat": 51.5188,
        "lon": -0.2266,
        "google_rating": 4.1
    },
    "Charing Cross Hospital": {
        "trust": "Imperial College Healthcare NHS Trust",
        "area": "Hammersmith",
        "postcode": "W6 8RF",
        "lat": 51.4881,
        "lon": -0.2217,
        "google_rating": 3.6
    },
    "Northwick Park Hospital": {
        "trust": "London North West University Healthcare NHS Trust",
        "area": "Harrow",
        "postcode": "HA1 3UJ",
        "lat": 51.5777,
        "lon": -0.3186,
        "google_rating": 2.5
    },
    "Ealing Hospital": {
        "trust": "London North West University Healthcare NHS Trust",
        "area": "Southall",
        "postcode": "UB1 3HW",
        "lat": 51.5098,
        "lon": -0.3575,
        "google_rating": 2.7
    },
    "King's College Hospital": {
        "trust": "King's College Hospital NHS Foundation Trust",
        "area": "Denmark Hill",
        "postcode": "SE5 9RS",
        "lat": 51.4681,
        "lon": -0.0930,
        "google_rating": 3.6
    },
    "Princess Royal University Hospital": {
        "trust": "King's College Hospital NHS Foundation Trust",
        "area": "Bromley",
        "postcode": "BR6 8ND",
        "lat": 51.3473,
        "lon": 0.0492,
        "google_rating": 3.5
    },
    "St Helier Hospital": {
        "trust": "Epsom and St Helier University Hospitals NHS Trust",
        "area": "Carshalton",
        "postcode": "SM5 1AA",
        "lat": 51.3628,
        "lon": -0.1829,
        "google_rating": 3.0
    },
    "Epsom Hospital": {
        "trust": "Epsom and St Helier University Hospitals NHS Trust",
        "area": "Epsom",
        "postcode": "KT18 7EG",
        "lat": 51.3283,
        "lon": -0.2570,
        "google_rating": 3.6
    },
    "Croydon University Hospital": {
        "trust": "Croydon Health Services NHS Trust",
        "area": "Croydon",
        "postcode": "CR7 7YE",
        "lat": 51.3939,
        "lon": -0.0859,
        "google_rating": 2.8
    },
    # Major hospitals outside London with haematology rotations
    "Queen's Medical Centre (Nottingham)": {
        "trust": "Nottingham University Hospitals NHS Trust",
        "area": "Nottingham",
        "postcode": "NG7 2UH",
        "lat": 52.9408,
        "lon": -1.1856,
        "google_rating": 3.8,
        "region": "East Midlands",
        "haematology_rotations": 60
    },
    "Leicester Royal Infirmary": {
        "trust": "University Hospitals of Leicester NHS Trust",
        "area": "Leicester",
        "postcode": "LE1 5WW",
        "lat": 52.6219,
        "lon": -1.1397,
        "google_rating": 3.5,
        "region": "East Midlands",
        "haematology_rotations": 33
    },
    "Royal Derby Hospital": {
        "trust": "University Hospitals of Derby and Burton NHS Trust",
        "area": "Derby",
        "postcode": "DE22 3NE",
        "lat": 52.9190,
        "lon": -1.4913,
        "google_rating": 3.6,
        "region": "East Midlands",
        "haematology_rotations": 21
    },
    "Northampton General Hospital": {
        "trust": "Northampton General Hospital NHS Trust",
        "area": "Northampton",
        "postcode": "NN1 5BD",
        "lat": 52.2448,
        "lon": -0.8814,
        "google_rating": 3.4,
        "region": "East Midlands",
        "haematology_rotations": 18
    },
    "Addenbrooke's Hospital (Cambridge)": {
        "trust": "Cambridge University Hospitals NHS Foundation Trust",
        "area": "Cambridge",
        "postcode": "CB2 0QQ",
        "lat": 52.1751,
        "lon": 0.1406,
        "google_rating": 4.2,
        "region": "East of England",
        "haematology_rotations": 7
    }
}

# London neighborhoods for commute analysis
NEIGHBORHOODS = {
    "Camden": {"lat": 51.5390, "lon": -0.1426, "rent_1br": 950, "ads": 45, "crime_rate": 147.2},
    "Islington": {"lat": 51.5465, "lon": -0.1058, "rent_1br": 920, "ads": 52, "crime_rate": 129.8},
    "Hackney": {"lat": 51.5450, "lon": -0.0553, "rent_1br": 880, "ads": 68, "crime_rate": 134.2},
    "Tower Hamlets": {"lat": 51.5099, "lon": -0.0059, "rent_1br": 950, "ads": 73, "crime_rate": 142.6},
    "Southwark": {"lat": 51.4743, "lon": -0.0764, "rent_1br": 820, "ads": 68, "crime_rate": 138.9},
    "Lambeth": {"lat": 51.4607, "lon": -0.1163, "rent_1br": 840, "ads": 58, "crime_rate": 131.5},
    "Wandsworth": {"lat": 51.4571, "lon": -0.1919, "rent_1br": 890, "ads": 56, "crime_rate": 89.2},
    "Hammersmith & Fulham": {"lat": 51.4927, "lon": -0.2339, "rent_1br": 900, "ads": 49, "crime_rate": 95.6},
    "Kensington & Chelsea": {"lat": 51.4991, "lon": -0.1938, "rent_1br": 1350, "ads": 32, "crime_rate": 110.4},
    "Westminster": {"lat": 51.4975, "lon": -0.1357, "rent_1br": 1200, "ads": 38, "crime_rate": 198.5},
    "Brent": {"lat": 51.5588, "lon": -0.2817, "rent_1br": 820, "ads": 64, "crime_rate": 118.4},
    "Ealing": {"lat": 51.5130, "lon": -0.3089, "rent_1br": 780, "ads": 38, "crime_rate": 87.3},
    "Barnet": {"lat": 51.6252, "lon": -0.1517, "rent_1br": 850, "ads": 48, "crime_rate": 68.9},
    "Haringey": {"lat": 51.5906, "lon": -0.1110, "rent_1br": 800, "ads": 59, "crime_rate": 121.7},
    "Newham": {"lat": 51.5255, "lon": 0.0352, "rent_1br": 720, "ads": 82, "crime_rate": 125.8},
    "Lewisham": {"lat": 51.4415, "lon": -0.0117, "rent_1br": 770, "ads": 63, "crime_rate": 111.3},
    "Greenwich": {"lat": 51.4892, "lon": 0.0648, "rent_1br": 790, "ads": 54, "crime_rate": 108.6},
    "Croydon": {"lat": 51.3762, "lon": -0.0982, "rent_1br": 680, "ads": 76, "crime_rate": 98.7},
    "Bromley": {"lat": 51.4039, "lon": 0.0198, "rent_1br": 750, "ads": 52, "crime_rate": 62.4},
    "Kingston upon Thames": {"lat": 51.4123, "lon": -0.3007, "rent_1br": 830, "ads": 44, "crime_rate": 78.3},
    "Bexley": {"lat": 51.4549, "lon": 0.1505, "rent_1br": 700, "ads": 41, "crime_rate": 71.5},
    "Harrow": {"lat": 51.5898, "lon": -0.3346, "rent_1br": 810, "ads": 36, "crime_rate": 74.8},
    "Hillingdon": {"lat": 51.5441, "lon": -0.4760, "rent_1br": 740, "ads": 29, "crime_rate": 92.1},
    "Hounslow": {"lat": 51.4746, "lon": -0.3680, "rent_1br": 760, "ads": 34, "crime_rate": 96.5}
}

# Simulated commute times (in minutes) via public transport
def calculate_commute_time(neighborhood, hospital):
    """Calculate approximate commute time based on distance and London transport"""
    import math
    
    n_lat, n_lon = NEIGHBORHOODS[neighborhood]["lat"], NEIGHBORHOODS[neighborhood]["lon"]
    h_lat, h_lon = HOSPITALS[hospital]["lat"], HOSPITALS[hospital]["lon"]
    
    # Haversine distance
    lat1, lon1, lat2, lon2 = map(math.radians, [n_lat, n_lon, h_lat, h_lon])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance_km = 6371 * c
    
    # Approximate: 5-6 km per 15 minutes on average in London (accounting for connections)
    base_time = (distance_km / 5.5) * 15
    # Add random variation for different routes
    variation = random.uniform(-3, 5)
    return int(base_time + variation)

# Current rail/road works affecting London (simulated data based on typical TfL disruptions)
TRANSPORT_DISRUPTIONS = [
    {
        "type": "rail",
        "line": "Northern Line",
        "status": "Part Closure",
        "description": "Kennington to Moorgate closed weekends until April 2026 for upgrades",
        "severity": "high",
        "affected_hospitals": ["St Bartholomew's Hospital", "Royal London Hospital", "King's College Hospital"]
    },
    {
        "type": "rail",
        "line": "Piccadilly Line",
        "status": "Minor Delays",
        "description": "Signal failures at Hammersmith causing delays",
        "severity": "medium",
        "affected_hospitals": ["Hammersmith Hospital", "Charing Cross Hospital"]
    },
    {
        "type": "road",
        "location": "A406 North Circular",
        "status": "Roadworks",
        "description": "Major roadworks near Brent Cross until June 2026",
        "severity": "medium",
        "affected_hospitals": ["North Middlesex Hospital", "Northwick Park Hospital"]
    },
    {
        "type": "rail",
        "line": "Elizabeth Line",
        "status": "Good Service",
        "description": "All stations operational with excellent connections",
        "severity": "low",
        "affected_hospitals": []
    },
    {
        "type": "road",
        "location": "A23 Purley Way",
        "status": "Lane Closures",
        "description": "Resurfacing works affecting southbound traffic to Croydon",
        "severity": "medium",
        "affected_hospitals": ["Croydon University Hospital"]
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rotations')
def rotations_page():
    """New page showing all 1563 rotations with filtering"""
    return render_template('rotations.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/map')
def show_map():
    return render_template('map.html')

@app.route('/api/hospitals')
def get_hospitals():
    return jsonify(HOSPITALS)

@app.route('/api/hospitals_extended')
def get_hospitals_extended():
    """Get extended hospital list with all UK hospitals offering haematology"""
    import json
    try:
        with open('hospitals_extended.json', 'r') as f:
            hospitals = json.load(f)
        return jsonify(hospitals)
    except FileNotFoundError:
        return jsonify({"error": "Extended hospital data not found"}), 404

@app.route('/api/rotations')
def get_all_rotations():
    """Get ALL 1563 rotation programs with full details"""
    import json
    try:
        with open('all_rotations.json', 'r') as f:
            rotations = json.load(f)
        return jsonify(rotations)
    except FileNotFoundError:
        return jsonify({"error": "Rotation data not found"}), 404

@app.route('/api/rotations/filter')
def filter_rotations():
    """Filter rotations by specialty, region, etc."""
    import json
    try:
        with open('all_rotations.json', 'r') as f:
            rotations = json.load(f)
        
        # Get filter parameters
        specialty = request.args.get('specialty', '').lower()
        region = request.args.get('region', '')
        location = request.args.get('location', '')
        
        filtered = rotations
        
        if specialty and specialty != 'all':
            specialty_field = f'has_{specialty}'
            filtered = [r for r in filtered if r.get(specialty_field, False)]
        
        if region and region != 'all':
            filtered = [r for r in filtered if r['region'] == region]
        
        if location and location != 'all':
            filtered = [r for r in filtered if r.get('location_name', '') == location]
        
        return jsonify(filtered)
    except FileNotFoundError:
        return jsonify({"error": "Rotation data not found"}), 404

@app.route('/api/neighborhoods')
def get_neighborhoods():
    return jsonify(NEIGHBORHOODS)

@app.route('/api/commute/<neighborhood>/<hospital>')
def get_commute(neighborhood, hospital):
    if neighborhood in NEIGHBORHOODS and hospital in HOSPITALS:
        time = calculate_commute_time(neighborhood, hospital)
        return jsonify({
            "neighborhood": neighborhood,
            "hospital": hospital,
            "commute_time_minutes": time
        })
    return jsonify({"error": "Invalid neighborhood or hospital"}), 404

@app.route('/api/hospital_commutes/<hospital>')
def get_hospital_commutes(hospital):
    """Get all neighborhood commute times for a specific hospital"""
    if hospital not in HOSPITALS:
        return jsonify({"error": "Invalid hospital"}), 404
    
    commutes = {}
    for neighborhood in NEIGHBORHOODS.keys():
        time = calculate_commute_time(neighborhood, hospital)
        commutes[neighborhood] = {
            "commute_time": time,
            "rent": NEIGHBORHOODS[neighborhood]["rent_1br"],
            "ads": NEIGHBORHOODS[neighborhood]["ads"],
            "crime_rate": NEIGHBORHOODS[neighborhood]["crime_rate"],
            "lat": NEIGHBORHOODS[neighborhood]["lat"],
            "lon": NEIGHBORHOODS[neighborhood]["lon"]
        }
    
    return jsonify(commutes)

@app.route('/api/disruptions')
def get_disruptions():
    return jsonify(TRANSPORT_DISRUPTIONS)

@app.route('/api/stats')
def get_stats():
    """Get statistics about neighborhoods"""
    rents = [n["rent_1br"] for n in NEIGHBORHOODS.values()]
    crime_rates = [n["crime_rate"] for n in NEIGHBORHOODS.values()]
    
    import statistics
    return jsonify({
        "rent": {
            "mean": statistics.mean(rents),
            "median": statistics.median(rents),
            "min": min(rents),
            "max": max(rents),
            "stdev": statistics.stdev(rents)
        },
        "crime": {
            "mean": statistics.mean(crime_rates),
            "median": statistics.median(crime_rates),
            "min": min(crime_rates),
            "max": max(crime_rates),
            "stdev": statistics.stdev(crime_rates)
        },
        "neighborhoods_count": len(NEIGHBORHOODS),
        "hospitals_count": len(HOSPITALS)
    })

@app.route('/api/borough_polygons')
def get_borough_polygons():
    """Get London borough polygon boundaries"""
    import json
    try:
        # Try real GeoJSON first
        with open('london_boroughs_real.json', 'r') as f:
            geojson = json.load(f)
        return jsonify(geojson)
    except FileNotFoundError:
        # Fall back to simplified polygons
        try:
            with open('london_borough_polygons.json', 'r') as f:
                polygons = json.load(f)
            return jsonify(polygons)
        except FileNotFoundError:
            return jsonify({"error": "Polygon data not found"}), 404

@app.route('/api/transport_modes')
def get_transport_modes():
    """Get transport mode information for neighborhoods"""
    import json
    try:
        with open('transport_data.json', 'r') as f:
            transport = json.load(f)
        return jsonify(transport)
    except FileNotFoundError:
        return jsonify({"error": "Transport data not found"}), 404

@app.route('/api/specialties')
def get_specialties():
    """Get specialty information for hospitals"""
    import json
    try:
        with open('hospital_specialties.json', 'r') as f:
            specialties = json.load(f)
        return jsonify(specialties)
    except FileNotFoundError:
        return jsonify({"error": "Specialties data not found"}), 404

@app.route('/histograms')
def show_histograms():
    """Display rent and crime rate histograms"""
    return render_template('histograms.html')

@app.route('/hospitals')
def hospitals_network():
    """Hospital network view page"""
    return render_template('hospitals.html')

@app.route('/api/generate_map')
def generate_map():
    # Create a folium map centered on London
    m = folium.Map(
        location=[51.5074, -0.1278],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add hospitals as markers
    for hospital_name, hospital_data in HOSPITALS.items():
        # Create popup content with hospital details
        popup_html = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="color: #0066cc; margin-bottom: 8px;">{hospital_name}</h4>
            <p style="margin: 4px 0;"><strong>Trust:</strong> {hospital_data['trust']}</p>
            <p style="margin: 4px 0;"><strong>Area:</strong> {hospital_data['area']}</p>
            <p style="margin: 4px 0;"><strong>Postcode:</strong> {hospital_data['postcode']}</p>
            <p style="margin: 4px 0;"><strong>Google Rating:</strong> 
                <span style="color: #f39c12;">⭐ {hospital_data['google_rating']}/5.0</span>
            </p>
        </div>
        """
        
        # Determine marker color based on rating
        if hospital_data['google_rating'] >= 4.0:
            icon_color = 'green'
        elif hospital_data['google_rating'] >= 3.5:
            icon_color = 'orange'
        else:
            icon_color = 'red'
        
        folium.Marker(
            location=[hospital_data['lat'], hospital_data['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{hospital_name} - Rating: {hospital_data['google_rating']}",
            icon=folium.Icon(color=icon_color, icon='plus-sign', prefix='glyphicon')
        ).add_to(m)
    
    # Add neighborhoods as circle markers
    for neighborhood, data in NEIGHBORHOODS.items():
        popup_html = f"""
        <div style="font-family: Arial; width: 220px;">
            <h4 style="color: #27ae60; margin-bottom: 8px;">{neighborhood}</h4>
            <p style="margin: 4px 0;"><strong>Avg. Rent (1 room):</strong> £{data['rent_1br']}/month</p>
            <p style="margin: 4px 0;"><strong>Available Ads:</strong> {data['ads']} listings</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{neighborhood}",
            color='blue',
            fill=True,
            fillColor='lightblue',
            fillOpacity=0.6
        ).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 280px; height: auto;
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
        <h4 style="margin-top:0;">Map Legend</h4>
        <p><span style="color: green;">🏥 Green Hospital</span> - Rating ≥ 4.0</p>
        <p><span style="color: orange;">🏥 Orange Hospital</span> - Rating 3.5-3.9</p>
        <p><span style="color: red;">🏥 Red Hospital</span> - Rating < 3.5</p>
        <p><span style="color: blue;">🔵 Blue Circles</span> - Neighborhoods</p>
        <p style="margin-top: 10px; font-size: 12px; color: #666;">
            Click markers for details including commute times, rent, and listings
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save to templates
    m.save('/workspace/templates/map.html')
    
    return jsonify({"status": "success", "message": "Map generated successfully"})

@app.route('/api/hospitals_from_rotations')
def get_hospitals_from_rotations():
    """Extract individual hospitals from rotation descriptions and create hospital-centric view"""
    try:
        import re
        import json
        
        # Load rotations data
        with open('all_rotations.json', 'r') as f:
            all_rotations_data = json.load(f)
        
        # Pattern to match hospital names like "Nottingham (NUH)" or "Derby (UHDB)"
        hospital_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([A-Z]+)\)'
        
        hospital_data = {}
        hospital_connections = {}
        
        for rotation in all_rotations_data:
            desc = rotation.get('description', '')
            matches = re.findall(hospital_pattern, desc)
            
            # Extract unique hospitals from this rotation
            rotation_hospitals = []
            for hospital_full, hospital_abbr in matches:
                hospital_key = f"{hospital_full} ({hospital_abbr})"
                rotation_hospitals.append(hospital_key)
                
                # Initialize hospital data if not exists
                if hospital_key not in hospital_data:
                    hospital_data[hospital_key] = {
                        'name': hospital_key,
                        'full_name': hospital_full,
                        'abbreviation': hospital_abbr,
                        'rotation_ids': [],  # Just store IDs, not full rotation data
                        'specialties': set(),
                        'lat': rotation['lat'],
                        'lon': rotation['lon'],
                        'region': rotation['region'],
                        'location_name': rotation['location_name'],
                        'google_rating': rotation['google_rating'],
                        'total_positions': 0
                    }
                
                # Add rotation ID and count positions
                hospital_data[hospital_key]['rotation_ids'].append(rotation['id'])
                hospital_data[hospital_key]['total_positions'] += rotation.get('places_available', 0)
                
                # Track specialties
                for spec in ['haematology', 'cardiology', 'respiratory', 'gastroenterology', 
                            'endocrinology', 'neurology', 'renal', 'geriatric', 'icu']:
                    if rotation.get(f'has_{spec}', False):
                        hospital_data[hospital_key]['specialties'].add(spec)
            
            # Create connections between hospitals in the same rotation
            for i, hosp1 in enumerate(rotation_hospitals):
                for hosp2 in rotation_hospitals[i+1:]:
                    conn_key = tuple(sorted([hosp1, hosp2]))
                    if conn_key not in hospital_connections:
                        hospital_connections[conn_key] = {
                            'count': 0,
                            'sample_programme': rotation['programme_name']
                        }
                    hospital_connections[conn_key]['count'] += 1
        
        # Convert sets to lists and add counts
        for hospital in hospital_data.values():
            hospital['specialties'] = list(hospital['specialties'])
            hospital['rotation_count'] = len(hospital['rotation_ids'])
            del hospital['rotation_ids']  # Remove IDs to reduce size
        
        # Format connections (reduced size)
        connections_list = []
        for (hosp1, hosp2), data in hospital_connections.items():
            connections_list.append({
                'hospital1': hosp1,
                'hospital2': hosp2,
                'shared_rotations': data['count'],
                'sample_programme': data['sample_programme']
            })
        
        return jsonify({
            'hospitals': list(hospital_data.values()),
            'connections': connections_list,
            'total_hospitals': len(hospital_data),
            'total_connections': len(connections_list)
        })
        
    except Exception as e:
        print(f"Error in get_hospitals_from_rotations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    os.makedirs('/workspace/templates', exist_ok=True)
    app.run(host='0.0.0.0', port=12000, debug=False, use_reloader=False)
