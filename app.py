from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Real Gujarat Revenue Department average residential benchmarks (Converted to per SqFt)
JANTRI_DEFAULTS = {
    "Ahmedabad": 4460,
    "Gandhinagar": 3900,
    "Surat": 3530,
    "Vadodara": 2780,
    "Rajkot": 2410
}

# Load ML assets safely with failover support
HAS_ML = False
model = None
le_district = None
districts = sorted(list(JANTRI_DEFAULTS.keys()))

try:
    import pandas as pd
    import numpy as np
    import joblib
    try:
        model = joblib.load('random_forest_house_model.pkl')
        le_district = joblib.load('district_encoder.pkl')
        districts = sorted(list(le_district.classes_))
        HAS_ML = True
        print("[ML Core] Machine Learning Model loaded successfully.")
    except Exception as e:
        print(f"[ML Warning] ML Asset Loading Failure: {e}")
except ImportError as e:
    print(f"[ML Info] Package pandas/numpy/joblib not found. Using fallback mathematical estimation: {e}")

@app.route('/')
def home():
    return render_template('index.html', districts=districts)

@app.route('/debug_log', methods=['POST'])
def debug_log():
    try:
        from flask import request
        data = request.get_json()
        log_msg = data.get('log', '')
        with open('js_debug.log', 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_jantri', methods=['GET'])
def get_jantri():
    # API endpoint to serve true default Jantri data asynchronously to the UI front-end
    district = request.args.get('district')
    default_rate = JANTRI_DEFAULTS.get(district, 3000)
    return jsonify({'default_jantri': default_rate})

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print(f"[BACKEND] Predict payload: {data}")
        
        district_name = data.get('district')
        jantri = float(data.get('jantri'))
        sqft = float(data.get('sqft'))
        bhk = int(data.get('bhk'))
        furnishing_tier = int(data.get('furnishing_status')) # 0=Unfurnished, 1=Semi-Furnished, 2=Fully Furnished
        age = int(data.get('age'))
        has_lift = int(data.get('lift'))
        floor = int(data.get('floor'))
        construction_status = data.get('construction_status') # 'ready' or 'under_construction'
        
        if HAS_ML:
            # 1. Map text districts safely to matching model index arrays
            try:
                encoded_dist = list(le_district.classes_).index(district_name)
            except:
                encoded_dist = 0
                
            # Translate the three UI choices into the binary status column the core model was trained on
            # 0 = Unfurnished/Semi, 1 = Premium Fully Furnished
            model_furnished_flag = 1 if furnishing_tier == 2 else 0
            
            # 2. Package clean structured row for the ML model input matrix
            input_data = pd.DataFrame([{
                'district': encoded_dist,
                'jantri_rate_per_sqft': jantri,
                'total_sqft': sqft,
                'bhk': bhk,
                'furnished_status': model_furnished_flag,
                'age_of_building_years': age,
                'lift_available': has_lift,
                'floor_no': floor
            }])
            
            # 3. Pull model base structural value
            base_prediction = float(model.predict(input_data)[0])
        else:
            # Fallback heuristic calculation matching model behaviors:
            # base price correlates to Jantri * Area (divided by 1 Lakh to get valuation in Lakhs)
            base_prediction = (jantri * sqft / 100000) * 1.25
            
            # Adjust based on structural details: BHK gives scaling modifier
            bhk_mod = 1.0 + (bhk - 2) * 0.15
            # Age depreciates valuation slightly
            age_mod = max(0.65, 1.0 - (age * 0.015))
            
            base_prediction = base_prediction * bhk_mod * age_mod
        
        # 4. FIXED INDEPENDENT MULTI-TIER INTERIOR PREMIUM RULES
        furniture_premium = 0.0
        if furnishing_tier == 1: # Semi-Furnished Flat Package Addition
            furniture_premium = 1.50 * bhk  # Scales cleanly by room index (e.g. ₹3 Lakhs for a 2BHK)
        elif furnishing_tier == 2: # Premium Fully Furnished Flat Fixed Packages
            if bhk == 1: furniture_premium = 2.50
            elif bhk == 2: furniture_premium = 4.50
            elif bhk == 3: furniture_premium = 6.50
            else: furniture_premium = 9.00
                
        # 5. Accessibility premium parameters
        lift_penalty = 0.0
        lift_premium = 0.0
        if floor > 3 and has_lift == 0:
            lift_penalty = -5.50 * (floor - 3)
        elif has_lift == 1:
            lift_premium = 0.50 * floor

        # Aggregate inputs baseline price matrix
        calculated_price = base_prediction + lift_premium + furniture_premium + lift_penalty
        
        # 6. DYNAMIC PIPELINE VALUE DEPRECIATION / FUTURE PREMIUM RULES
        appreciation_forecast = 0.0
        project_note = "Ready to move asset footprint."
        
        if construction_status == 'under_construction':
            # Properties under construction sell at a discount today but appreciate upon handover.
            # We apply an immediate risk reduction discount factor of 8% for buying early.
            calculated_price = calculated_price * 0.92
            
            # Forecast the future finished valuation index over a baseline 3-year construction cycle
            # Real estate across prime Gujarat economic nodes appreciates at approximately 7.5% per annum compounds.
            future_compounded = calculated_price * ((1 + 0.075) ** 3)
            appreciation_forecast = future_compounded - calculated_price
            project_note = "Future estimation model incorporates an 8% under-construction structural entry markdown."

        # 7. Compute baseline legal valuation floor parameter via Jantri formulation
        jantri_floor_limit = (jantri * sqft / 100000)
        safety_applied = False
        if calculated_price < jantri_floor_limit:
            calculated_price = jantri_floor_limit * 1.15
            safety_applied = True

        return jsonify({
            'success': True,
            'final_price': round(calculated_price, 2),
            'base_structural': round(base_prediction, 2),
            'furniture_addon': round(furniture_premium, 2),
            'elevation_delta': round(lift_premium + lift_penalty, 2),
            'future_appreciation': round(appreciation_forecast, 2),
            'project_note': project_note,
            'safety_applied': safety_applied
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)