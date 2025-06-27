"""Data utilities for generating mock data and data manipulation."""

import random
import pandas as pd
from datetime import datetime, timedelta
from config.constants import COMPANIES, JOB_TITLES, CATEGORIES, STATUSES


def generate_mock_data(num_records=50):
    """Generate mock application data for testing and development."""
    data = []
    for i in range(num_records):
        company = random.choice(COMPANIES)
        title = random.choice(JOB_TITLES)
        
        # Ensure unique combinations
        while any(app['company_name'] == company and app['job_title'] == title for app in data):
            company = random.choice(COMPANIES)
            title = random.choice(JOB_TITLES)
        
        # Random date within last 6 months
        date_applied = datetime.now() - timedelta(days=random.randint(1, 180))
        
        # Status progression logic for realistic data
        num_days_since = (datetime.now() - date_applied).days
        
        if num_days_since <= 3:
            status = "Applied"
        elif num_days_since <= 10:
            status = random.choice(["Applied", "Online Assessment"])
        elif num_days_since <= 30:
            status = random.choice([
                "Applied", "Online Assessment", 
                "Interviewing: 1st round", "Interviewing: 2nd round", "Rejected"
            ])
        else:
            status = random.choice(STATUSES)
        
        category = random.choice(CATEGORIES)
        notes = random.choice([
            "", "Great company culture", "Competitive salary", 
            "Remote-friendly", "Fast-growing startup", "Good benefits package"
        ])
        
        data.append({
            'id': i + 1,
            'company_name': company,
            'job_title': title,
            'application_url': f"https://{company.lower()}.com/careers",
            'date_applied': date_applied.strftime('%Y-%m-%d'),
            'category': category,
            'status': status,
            'notes': notes,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return data


def generate_status_history(applications_data):
    """Generate realistic status history for applications."""
    history_data = []
    history_id = 1
    
    for app in applications_data:
        app_id = app['id']
        date_applied = datetime.strptime(app['date_applied'], '%Y-%m-%d')
        current_status = app['status']
        
        # Always start with "Applied"
        history_data.append({
            'id': history_id,
            'application_id': app_id,
            'status': 'Applied',
            'timestamp': date_applied.strftime('%Y-%m-%d %H:%M:%S')
        })
        history_id += 1
        
        # Add progression based on current status
        if current_status != "Applied":
            days_elapsed = (datetime.now() - date_applied).days
            
            if current_status == "Online Assessment":
                # Add Online Assessment after 3-7 days
                oa_date = date_applied + timedelta(days=random.randint(3, 7))
                history_data.append({
                    'id': history_id,
                    'application_id': app_id,
                    'status': 'Online Assessment',
                    'timestamp': oa_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                history_id += 1
                
            elif "Interviewing" in current_status:
                # Add progression through interview rounds
                current_date = date_applied
                
                # Possibly add OA first
                if random.choice([True, False]):
                    current_date += timedelta(days=random.randint(3, 7))
                    history_data.append({
                        'id': history_id,
                        'application_id': app_id,
                        'status': 'Online Assessment',
                        'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    history_id += 1
                
                # Add interview rounds up to current
                round_num = int(current_status.split("round")[0].split(":")[-1].strip()[0])
                for r in range(1, round_num + 1):
                    current_date += timedelta(days=random.randint(5, 14))
                    history_data.append({
                        'id': history_id,
                        'application_id': app_id,
                        'status': f'Interviewing: {r}{"st" if r==1 else "nd" if r==2 else "rd" if r==3 else "th"} round',
                        'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    history_id += 1
                    
            elif current_status in ["Rejected", "Offer"]:
                # Add some progression before final status
                current_date = date_applied
                
                # Random progression
                if days_elapsed > 7 and random.choice([True, False]):
                    current_date += timedelta(days=random.randint(3, 7))
                    history_data.append({
                        'id': history_id,
                        'application_id': app_id,
                        'status': 'Online Assessment',
                        'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    history_id += 1
                
                if days_elapsed > 14 and random.choice([True, False]):
                    current_date += timedelta(days=random.randint(7, 14))
                    history_data.append({
                        'id': history_id,
                        'application_id': app_id,
                        'status': 'Interviewing: 1st round',
                        'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    history_id += 1
                
                # Final status
                if current_date != date_applied:
                    current_date += timedelta(days=random.randint(3, 10))
                    history_data.append({
                        'id': history_id,
                        'application_id': app_id,
                        'status': current_status,
                        'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    history_id += 1
    
    return history_data


def calculate_kpis(applications_data):
    """Calculate KPI metrics from applications data."""
    total_applied = len(applications_data)
    
    # Count by status
    status_counts = {}
    for app in applications_data:
        status = app['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate specific KPIs
    applied = total_applied
    rejected = status_counts.get('Rejected', 0)
    offered = status_counts.get('Offer', 0)
    active = total_applied - rejected - offered
    online_assessment = status_counts.get('Online Assessment', 0)
    
    # Count all interviewing statuses
    interviewing = sum(count for status, count in status_counts.items() 
                      if 'Interviewing' in status)
    
    return {
        'Applied': applied,
        'Active': active,
        'Online Assessment': online_assessment,
        'Interviewing': interviewing,
        'Rejected': rejected,
        'Offered': offered
    }


def get_status_color_class(status):
    """Get CSS class for status indicator color."""
    if status == "Applied":
        return "status-applied"
    elif status == "Online Assessment":
        return "status-online-assessment"
    elif "Interviewing" in status:
        return "status-interviewing"
    elif status == "Offer":
        return "status-offer"
    elif status == "Rejected":
        return "status-rejected"
    else:
        return "status-applied" 