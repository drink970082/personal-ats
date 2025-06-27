"""CSS styling for the application."""

CUSTOM_CSS = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>ATS Dashboard</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
        <script type="importmap">
        {
          "imports": {
            "@material/web/": "https://esm.run/@material/web/"
          }
        }
        </script>
        <script type="module">
          import '@material/web/all.js';
          import {styles as typescaleStyles} from '@material/web/typography/md-typescale-styles.js';

          document.adoptedStyleSheets.push(typescaleStyles.styleSheet);
        </script>
        <style>
            /* --- Material 3 Dark Theme Color Palette --- */
            :root {
                --md-sys-color-primary-rgb: 168, 199, 250;
                --md-sys-color-primary: #a8c7fa;
                --md-sys-color-on-primary: #0d3058;
                --md-sys-color-surface-container: #212429;
                --md-sys-color-surface-container-high: #2c2f33;
                --md-sys-color-surface-container-highest: #373a3e;
                --md-sys-color-surface: #131416;
                --md-sys-color-on-surface: #e2e2e6;
                --md-sys-color-on-surface-variant: #c2c7ce;
                --md-sys-color-outline: #8c9199;
                --md-sys-color-outline-variant: #42474e;
                --md-sys-color-error: #f2b8b5;
            }
            
            /* --- Base Styles --- */
            body {
                background-color: var(--md-sys-color-surface) !important;
                color: var(--md-sys-color-on-surface) !important;
                font-family: 'Roboto', sans-serif;
                font-size: 14px;
            }
            h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
                color: var(--md-sys-color-on-surface) !important;
            }
            .fade-in { 
                animation: fadeIn 0.4s ease-in-out; 
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* --- Component Containers --- */
            .card-component {
                background-color: var(--md-sys-color-surface-container);
                border: 1px solid var(--md-sys-color-outline-variant);
                border-radius: 12px;
                padding: 1.25rem;
            }

            /* --- Form Controls --- */
            .form-control, .form-select, .Select-control {
                background-color: var(--md-sys-color-surface-container-highest) !important;
                border: 1px solid var(--md-sys-color-outline-variant) !important;
                border-radius: 4px !important;
                color: var(--md-sys-color-on-surface) !important;
                padding: 0.5rem 0.75rem !important;
                transition: all 0.2s ease-in-out !important;
                height: 38px !important;
                min-height: 38px !important;
            }
            .form-control:focus, .form-select:focus, .Select-control:focus-within {
                box-shadow: 0 0 0 1px var(--md-sys-color-primary) !important;
                border-color: var(--md-sys-color-primary) !important;
                background-color: var(--md-sys-color-surface-container-highest) !important;
            }
            .form-control::placeholder { 
                color: var(--md-sys-color-on-surface-variant) !important; 
                opacity: 1; 
            }
            .Select-input input { color: var(--md-sys-color-on-surface) !important; }
            .Select-value-label, .Select-placeholder { 
                color: var(--md-sys-color-on-surface-variant) !important; 
            }
            .Select-menu-outer {
                background-color: var(--md-sys-color-surface-container-highest) !important;
                border: 1px solid var(--md-sys-color-outline-variant) !important;
                border-radius: 4px !important;
            }
            .Select-option {
                background-color: var(--md-sys-color-surface-container-highest);
                color: var(--md-sys-color-on-surface);
            }
            .Select-option.is-focused {
                background-color: var(--md-sys-color-primary) !important;
                color: var(--md-sys-color-on-primary) !important;
            }

            /* --- Button Styles --- */
            .btn-primary {
                background-color: var(--md-sys-color-primary) !important;
                color: var(--md-sys-color-on-primary) !important;
                border: none !important;
                border-radius: 20px !important;
                font-weight: 500;
                padding: 0.5rem 1.25rem;
            }
            .btn-m3-outline {
                background-color: transparent !important;
                border: 1px solid var(--md-sys-color-outline) !important;
                color: var(--md-sys-color-primary) !important;
                border-radius: 20px !important;
                font-weight: 500;
                padding: 0.4rem 1rem;
                font-size: 13px;
                line-height: 1.5;
                transition: background-color 0.2s ease;
            }
            .btn-m3-outline:hover {
                background-color: rgba(var(--md-sys-color-primary-rgb), 0.08) !important;
            }
            .btn-m3-text-danger {
                background-color: transparent !important;
                border: 1px solid var(--md-sys-color-error) !important;
                color: var(--md-sys-color-error) !important;
                border-radius: 20px !important;
                font-weight: 500;
                padding: 0.4rem 1rem;
                font-size: 13px;
                line-height: 1.5;
                transition: background-color 0.2s ease;
            }
            .btn-m3-text-danger:hover {
                background-color: rgba(242, 184, 181, 0.08) !important;
            }

            /* --- Stats Cards --- */
            .stats-card {
                background-color: var(--md-sys-color-surface-container-high);
                border: 1px solid var(--md-sys-color-outline-variant);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 110px;
            }
            .stat-number { 
                font-size: 1.75rem; 
                font-weight: 500; 
                color: var(--md-sys-color-primary); 
            }
            .stat-label { 
                font-size: 0.75rem; 
                color: var(--md-sys-color-on-surface-variant); 
                text-transform: uppercase; 
                letter-spacing: 0.8px; 
                line-height: 1.4; 
                margin: 0 auto; 
            }
            
            /* --- Table Styles --- */
            .table {
                --bs-table-bg: var(--md-sys-color-surface-container);
                --bs-table-color: var(--md-sys-color-on-surface);
                --bs-table-border-color: var(--md-sys-color-outline-variant);
                --bs-table-hover-bg: var(--md-sys-color-surface-container-high);
                --bs-table-hover-color: var(--md-sys-color-on-surface);
                --bs-table-striped-bg: var(--md-sys-color-surface-container);
                --bs-table-striped-color: var(--md-sys-color-on-surface);
                vertical-align: middle;
            }
            .table > :not(caption) > * > * { padding: 0.75rem 0.75rem; }
            .status-cell { display: flex; align-items: center; gap: 8px; }
            .status-indicator { 
                width: 8px; 
                height: 8px; 
                border-radius: 50%; 
                flex-shrink: 0; 
            }
            .status-indicator.status-applied { background-color: #5d8eff; }
            .status-indicator.status-online-assessment { background-color: #f29e4c; }
            .status-indicator.status-interviewing { background-color: #f76f8e; }
            .status-indicator.status-offer { background-color: #54c184; }
            .status-indicator.status-rejected { background-color: #909da2; }

            /* --- Tab Styles --- */
            .nav-tabs { border-bottom: 1px solid var(--md-sys-color-outline-variant) !important; }
            .nav-tabs .nav-link { 
                background: transparent; 
                border: none; 
                color: var(--md-sys-color-on-surface-variant); 
                transition: all 0.2s ease;
            }
            .nav-tabs .nav-link.active {
                color: var(--md-sys-color-primary) !important;
                background-color: rgba(var(--md-sys-color-primary-rgb), 0.04) !important;
                border-bottom: 2px solid var(--md-sys-color-primary) !important;
                border-radius: 4px 4px 0 0 !important;
            }
            
            /* --- Filter/Search Row --- */
            .filter-search-row {
                padding: 0 1rem;
                margin: 1rem 0;
            }
            
            /* --- Table Spacing --- */
            .table-responsive {
                margin-bottom: 0rem !important;
            }
            
            /* --- Pagination Styles --- */
            .pagination-select {
                height: 24px !important;
                min-height: 24px !important;
                font-size: 0.875rem !important;
                padding: 0 0.5rem !important;
            }
            .pagination-btn {
                background-color: transparent !important;
                border: 1px solid var(--md-sys-color-outline-variant) !important;
                color: var(--md-sys-color-on-surface-variant) !important;
                border-radius: 6px !important;
                font-weight: 400 !important;
                padding: 0.25rem 0.5rem !important;
                font-size: 0.875rem !important;
                min-width: 32px !important;
            }
            .pagination-btn:hover {
                background-color: var(--md-sys-color-surface-container-high) !important;
                border-color: var(--md-sys-color-outline) !important;
            }
            .pagination-btn-active {
                background-color: var(--md-sys-color-surface-container-highest) !important;
                border: 1px solid var(--md-sys-color-primary) !important;
                color: var(--md-sys-color-primary) !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
            }
            
            /* --- In-Table Controls --- */
            .table-dropdown {
                font-size: 13px !important;
                height: 34px !important;
                min-height: 34px !important;
                padding-top: 0.35rem !important;
                padding-bottom: 0.35rem !important;
            }
            
            /* --- Notes Textarea --- */
            .notes-textarea {
                min-height: 40px !important;
                resize: none !important;
                scrollbar-width: thin;
                scrollbar-color: var(--md-sys-color-outline-variant) transparent;
            }

            /* --- Custom Scrollbar for Webkit Browsers --- */
            .notes-textarea::-webkit-scrollbar {
                width: 8px;
            }
            .notes-textarea::-webkit-scrollbar-track {
                background: transparent;
            }
            .notes-textarea::-webkit-scrollbar-thumb {
                background-color: var(--md-sys-color-outline-variant);
                border-radius: 4px;
            }
            
            /* --- Form Textarea --- */
            .form-notes-textarea {
                min-height: 80px !important;
                resize: vertical !important;
            }
        </style>
    </head>
    <body> {%app_entry%} <footer> {%config%} {%scripts%} {%renderer%} </footer> </body>
</html>
""" 