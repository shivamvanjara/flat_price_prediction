# 🏘️ Gujarat Real Estate Property Listings Dataset

A dataset of **400 real property listings** scraped from across major districts of Gujarat, India — including Jantri rate, area, configuration, building age, and pricing details. Useful for **real estate price prediction (ML), market analysis, valuation comparison studies, and PropTech applications**.

---

## 📂 File

| File | Description |
|---|---|
| `gujarat_property_listings.csv` | 400 property records with pricing, area, and building attributes |

---

## 📊 Dataset Schema

| Column | Type | Description |
|---|---|---|
| `property_id` | string | Unique identifier for each property (e.g. `PROP_0001`) |
| `district` | string | District/city where the property is located (e.g. Rajkot, Vadodara, Gandhinagar, Surat, Ahmedabad) |
| `jantri_rate_per_sqft` | float | Government-declared minimum Jantri rate for the property (₹ per sq.ft) |
| `total_sqft` | integer | Total built-up area of the property (sq.ft) |
| `bhk` | integer | Number of bedrooms (BHK configuration) |
| `furnished_status` | binary (0/1) | `1` = Furnished, `0` = Unfurnished |
| `age_of_building_years` | integer | Age of the building in years |
| `lift_available` | binary (0/1) | `1` = Lift available, `0` = No lift |
| `floor_no` | integer | Floor number on which the property is located |
| `price_lakhs` | float | Listed sale price of the property (in ₹ Lakhs) |

**Sample row:**
```csv
property_id,district,jantri_rate_per_sqft,total_sqft,bhk,furnished_status,age_of_building_years,lift_available,floor_no,price_lakhs
PROP_0001,Rajkot,2758.39,3051,4,0,1,1,11,125.41
```

---

## 🗺️ Coverage

**Districts included:** Rajkot, Vadodara, Gandhinagar, Surat, Ahmedabad

**Records:** 400 properties

**Price range:** ~₹35 Lakhs – ₹200+ Lakhs (varies by district, area, and BHK)

---

## 💡 Potential Use Cases

- **Price prediction modeling** — train regression models (e.g. price vs. sqft, BHK, age, Jantri rate)
- **Jantri rate vs. market price comparison** — analyze the gap between government valuation and actual sale price by district
- **Feature importance analysis** — understand which attributes (lift, furnishing, floor, age) most influence price
- **District-wise market benchmarking**

---

## ⚠️ Notes & Limitations

- Data was scraped from publicly listed property sources; listing prices may differ from final transaction/registered values.
- `jantri_rate_per_sqft` reflects the government minimum valuation at time of scraping and may not match the latest official revision — always cross-check with [Garvi Gujarat](https://garvi.gujarat.gov.in) for current rates.
- Some fields (e.g. exact locality/area name, listing date, source URL) are not included in this version — consider this if higher granularity is needed.
- As with any scraped dataset, duplicate or stale listings may be present; recommended to deduplicate before training models.

---

## 🤝 Contributing

Contributions adding more districts, locality-level granularity, listing dates, or source metadata are welcome via pull request.

---

## 📄 License

For research and educational use. Verify any pricing or valuation data against official sources before using in real transactions.
