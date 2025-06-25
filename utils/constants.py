# Application constants

# Status options for applications
STATUS_OPTIONS = [
    "Applied", "Online Assessment", "1st round", "2nd round", "3rd round", 
    "4th round", "5th round", "6th round", "Offer", "Declined", "Rejected"
]

# Category options for applications
CATEGORY_OPTIONS = [
    {"label": "SWE/SDE", "value": "SWE/SDE"},
    {"label": "MLE", "value": "MLE"},
    {"label": "Quant Analyst", "value": "Quant Analyst"},
    {"label": "Quant Dev", "value": "Quant Dev"},
    {"label": "DS", "value": "DS"},
    {"label": "DA", "value": "DA"},
    {"label": "Others", "value": "Others"},
]

# Default category
DEFAULT_CATEGORY = "SWE/SDE"

# Pagination options
PAGE_SIZE_OPTIONS = [
    {"label": "5", "value": 5},
    {"label": "10", "value": 10},
    {"label": "25", "value": 25},
    {"label": "50", "value": 50},
]

DEFAULT_PAGE_SIZE = 10

# Chart colors
CHART_COLORS = {
    'Applied': '#007bff',
    'Online Assessment': '#ffc107',
    '1st round': '#17a2b8',
    '2nd round': '#28a745',
    '3rd round': '#6f42c1',
    '4th round': '#fd7e14',
    '5th round': '#e83e8c',
    '6th round': '#6c757d',
    'Offer': '#28a745',
    'Declined': '#dc3545',
    'Rejected': '#dc3545',
    'No Response': '#6c757d'
} 