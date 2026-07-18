MOCK_FACILITIES = [
    {
        "id": "demo-facility-1",
        "name": "Metro General Hospital",
        "type": "Acute Care Hospital",
        "state": "TX",
        "city": "Austin",
        "address": "100 Medical Center Dr, Austin, TX",
        "claimedCapabilities": ["ICU", "Emergency"],
        "trustScore": 86,
        "trustLevel": "High",
        "bedCount": 320,
        "summary": "Strong evidence for ICU and emergency capability based on mock licensing and capacity signals.",
        "dataQualityFlags": ["Missing NICU evidence"],
        "scoreReasons": [
            {
                "label": "License evidence",
                "description": "Mock license record includes ICU and emergency services.",
                "impact": "positive",
            },
            {
                "label": "Capacity signal",
                "description": "Mock bed profile includes adult critical care capacity.",
                "impact": "positive",
            },
            {
                "label": "NICU gap",
                "description": "No mock source currently supports NICU capability.",
                "impact": "negative",
            },
        ],
        "facilityChecks": [
            {
                "name": "ICU",
                "isPresent": True,
                "evidence": "Mock state license lists adult ICU beds.",
            },
            {
                "name": "NICU",
                "isPresent": False,
                "evidence": "No mock neonatal intensive care evidence found.",
            },
            {
                "name": "Emergency",
                "isPresent": True,
                "evidence": "Mock facility profile lists 24/7 emergency department.",
            },
            {
                "name": "Trauma Center",
                "isPresent": False,
                "evidence": "No mock trauma designation evidence found.",
            },
        ],
    },
    {
        "id": "demo-facility-2",
        "name": "Lakeview Children's Medical Center",
        "type": "Children's Hospital",
        "state": "IL",
        "city": "Chicago",
        "address": "45 Lakeview Ave, Chicago, IL",
        "claimedCapabilities": ["NICU", "Emergency"],
        "trustScore": 74,
        "trustLevel": "Medium",
        "bedCount": 180,
        "summary": "NICU evidence is present, but emergency capability needs stronger supporting records.",
        "dataQualityFlags": ["Weak emergency claim"],
        "scoreReasons": [
            {
                "label": "NICU designation",
                "description": "Mock pediatric profile includes neonatal intensive care capability.",
                "impact": "positive",
            },
            {
                "label": "Emergency evidence is weak",
                "description": "Emergency claim appears in one mock source only.",
                "impact": "negative",
            },
        ],
        "facilityChecks": [
            {
                "name": "ICU",
                "isPresent": False,
                "evidence": "No mock adult ICU capability found.",
            },
            {
                "name": "NICU",
                "isPresent": True,
                "evidence": "Mock pediatric registry lists NICU service line.",
            },
            {
                "name": "Emergency",
                "isPresent": True,
                "evidence": "Mock provider directory claims emergency services.",
            },
            {
                "name": "Trauma Center",
                "isPresent": False,
                "evidence": "No mock trauma designation evidence found.",
            },
        ],
    },
    {
        "id": "demo-facility-3",
        "name": "Rural Valley Health",
        "type": "Critical Access Hospital",
        "state": "CO",
        "city": "Salida",
        "address": "12 Valley Route, Salida, CO",
        "claimedCapabilities": ["Emergency"],
        "trustScore": 48,
        "trustLevel": "Low",
        "bedCount": None,
        "summary": "Emergency claim exists, but capacity is missing and coordinate evidence is suspicious.",
        "dataQualityFlags": ["Missing capacity", "Suspicious coordinates"],
        "scoreReasons": [
            {
                "label": "Emergency claim",
                "description": "Mock claim exists but is not backed by multiple sources.",
                "impact": "neutral",
            },
            {
                "label": "Missing capacity",
                "description": "Mock capacity data is unavailable.",
                "impact": "negative",
            },
            {
                "label": "Coordinate issue",
                "description": "Mock geocode is far from the stated city centroid.",
                "impact": "negative",
            },
        ],
        "facilityChecks": [
            {
                "name": "ICU",
                "isPresent": False,
                "evidence": "No mock ICU evidence found.",
            },
            {
                "name": "NICU",
                "isPresent": False,
                "evidence": "No mock NICU evidence found.",
            },
            {
                "name": "Emergency",
                "isPresent": True,
                "evidence": "Mock facility listing claims emergency service.",
            },
            {
                "name": "Trauma Center",
                "isPresent": False,
                "evidence": "No mock trauma designation evidence found.",
            },
        ],
    },
]


MOCK_DATA_QUALITY_ISSUES = [
    {
        "facilityId": "demo-facility-1",
        "facilityName": "Metro General Hospital",
        "issue": "Missing NICU evidence",
        "severity": "Medium",
    },
    {
        "facilityId": "demo-facility-2",
        "facilityName": "Lakeview Children's Medical Center",
        "issue": "Weak emergency claim",
        "severity": "Medium",
    },
    {
        "facilityId": "demo-facility-3",
        "facilityName": "Rural Valley Health",
        "issue": "Suspicious coordinates",
        "severity": "High",
    },
    {
        "facilityId": "demo-facility-3",
        "facilityName": "Rural Valley Health",
        "issue": "Missing capacity",
        "severity": "High",
    },
]
