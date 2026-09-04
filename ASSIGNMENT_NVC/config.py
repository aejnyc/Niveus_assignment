"""TEST_NAME_LOOKUP = {
    "Haemoglobin":"HAEMOGLOBIN",
    "Hb":"HAEMOGLOBIN",
    "haemoglobin":"HAEMOGLOBIN"

    "TOTAL WBC COUNT":"WHITE BLOOD CELL COUNT",
    "Total WBC Count":"WHITE BLOOD CELL COUNT",
    "WBC COUNT":"WHITE BLOOD CELL COUNT",

    "CREATININE":"Serum Creatinine", 
    "SERUM":"Serum Creatinine",
    "SERUM CREATININE":"Serum Creatinine",
    "Serum Creatinine":"Serum Creatinine",

    "Na+":"SODIUM",
    "SODIUM":"SODIUM",
    "Sodium":"SODIUM",

    "K+":"POTASSIUM",
    "POTASSIUM":"POTASSIUM",
    "Potassium":"POTASSIUM",

    "RBC":"Red Blood Cell Count (RBC)",
    "RBC COUNT":"Red Blood Cell Count (RBC)",

    "PLATELET COUNT":"Platelet Count",
    "Platelet Count":"Platelet Count",

    "ALBUMIN":"ALBUMIN",

    "HAEMATOCRIT":"HEMATOCRIT",
    "Haematocrit (PCV)":"HEMATOCRIT",

    "PROCALCITONIN":"Procalcitonin",
    "PROCALCITONIN (PCT)":"Procalcitonin",

    "CREATININE":"CREATININE",
    "Creatinine":"CREATININE",

    "C-REACTIVE PROTEIN (CRP)":"C-REACTIVE PROTEIN",
    "CRP":"C-REACTIVE PROTEIN",

    "ALANINE AMINOTRANSFERASE":"ALANINE AMINOTRANSFERASE",
    "ALT (SGPT)":"ALANINE AMINOTRANSFERASE",

    "ASPARTATE AMINOTRANSFERASE":"ASPARTATE AMINOTRANSFERASE",
    "AST (SGOT)":"ASPARTATE AMINOTRANSFERASE",

    "URIC ACID":"URIC ACID",
    "Uric Acid":"URIC ACID",

    "CALCIUM":"CALCIUM",
    "Ca2+ (Calcium)":"CALCIUM",

    "HGB":"HEMOGLOBIN",
    "Hb":"HEMOGLOBIN",

    "Filtration Rate":"Estimated Glomerular Filtration Rate (eGFR)",
    "eGFR - ESTIMATED GLOMERULAR FILTRATION RATE":"Estimated Glomerular Filtration Rate (eGFR)",

    "BLOOD UREA NITROGEN":"Urea Nitrogen (BUN)",
    "UREA":"Urea Nitrogen (BUN)"
    
}"""

# config.py

# 1. Test Name Mapping (FR-2.1)
TEST_NAME_LOOKUP = {
    "haemoglobin": "Hemoglobin",
    "hemoglobin": "Hemoglobin",
    "aemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "hgb": "Hemoglobin",
    "wbc": "WBC",
    "white blood cell": "WBC",
    "white blood cells": "WBC",
    "wbc count": "WBC",
    "tlc": "WBC",
    "total leucocyte count": "WBC",
    "platelets": "Platelets",
    "platelet count": "Platelets",
    "plt": "Platelets",
    "platelet": "Platelets"
}

# 2. Target Tests for Fixed 5-Column Schema (FR-2.2)
CANONICAL_TARGET_TESTS = ["Hemoglobin", "WBC", "Platelets"]

# 3. Standard Canonical Units
CANONICAL_UNITS = {
    "Hemoglobin": "g/dL",
    "WBC": "cells/cu.mm",
    "Platelets": "cells/cu.mm"
}

# 4. Range and Outlier Boundaries (FR-3)
TEST_BOUNDARIES = {
    "Hemoglobin": {"min_range": 12.0, "max_range": 17.5, "min_outlier": 2.0, "max_outlier": 25.0},
    "WBC": {"min_range": 4000.0, "max_range": 11000.0, "min_outlier": 100.0, "max_outlier": 100000.0},
    "Platelets": {"min_range": 150000.0, "max_range": 450000.0, "min_outlier": 5000.0, "max_outlier": 2000000.0}
}