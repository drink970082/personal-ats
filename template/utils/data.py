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
        num_days_since = (datetime.now() - date_applied).days
        
        # Create realistic status progression based on days elapsed
        status = "Applied"  # Default
        
        # Define realistic progression paths with more in-progress states
        if num_days_since > 2:  # At least 2 days old
            # 60% chance of progression from Applied
            if random.random() < 0.6:
                # Path 1: Applied -> Online Assessment (40% chance)
                if random.random() < 0.4:
                    status = "Online Assessment"
                    
                    # From OA, what happens next? (mostly stay in progress)
                    if num_days_since > 8:
                        if random.random() < 0.4:  # Only 40% proceed quickly to interview
                            status = "Interviewing: 1st round"
                            
                            # Continue interview progression (slower progression)
                            if num_days_since > 25:
                                if random.random() < 0.3:  # Only 30% proceed to 2nd round
                                    status = "Interviewing: 2nd round"
                                    
                                    if num_days_since > 45:
                                        if random.random() < 0.25:  # 25% proceed to 3rd round
                                            status = "Interviewing: 3rd round"
                                            
                                            if num_days_since > 65:
                                                if random.random() < 0.15:  # 15% get offer, 85% rejected
                                                    status = "Offer"
                                                elif random.random() < 0.3:  # 30% rejected, 70% stay in 3rd round
                                                    status = "Rejected"
                                        elif random.random() < 0.2:  # 20% rejected after 2nd round
                                            status = "Rejected"
                                elif random.random() < 0.15:  # 15% rejected after 1st round
                                    status = "Rejected"
                        elif random.random() < 0.1:  # 10% rejected after OA
                            status = "Rejected"
                
                # Path 2: Applied -> Direct to Interview (25% chance)
                elif random.random() < 0.25:
                    status = "Interviewing: 1st round"
                    
                    if num_days_since > 12:
                        if random.random() < 0.35:  # 35% proceed to 2nd round
                            status = "Interviewing: 2nd round"
                            
                            if num_days_since > 30:
                                if random.random() < 0.3:  # 30% proceed to 3rd round
                                    status = "Interviewing: 3rd round"
                                    
                                    if num_days_since > 50:
                                        if random.random() < 0.2:  # 20% get offer
                                            status = "Offer"
                                        elif random.random() < 0.25:  # 25% rejected
                                            status = "Rejected"
                                elif random.random() < 0.2:  # 20% rejected after 2nd round
                                    status = "Rejected"
                        elif random.random() < 0.15:  # 15% rejected after 1st round
                            status = "Rejected"
                
                # Path 3: Applied -> Direct Rejection (35% chance, but only for older applications)
                else:
                    if num_days_since > 21:  # Only reject after 3 weeks
                        if random.random() < 0.4:  # 40% get rejected eventually
                            status = "Rejected"
        
        category = random.choice(CATEGORIES)
        notes = random.choice([
            "", "Great company culture", "Competitive salary", 
            "Remote-friendly", "Fast-growing startup", "Good benefits package",
            "Interesting tech stack", "Strong team", "Good work-life balance"
        ])
        
        data.append({
            'id': i + 1,
            'company_name': company,
            'job_title': title,
            'application_url': f"https://{company.lower().replace(' ', '').replace('.', '')}.com/careers",
            'date_applied': date_applied.strftime('%Y-%m-%d'),
            'category': category,
            'status': status,
            'notes': notes,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return data


def generate_status_history(applications_data):
    """Generate realistic status history for applications that matches their final status."""
    history_data = []
    history_id = 1
    
    for app in applications_data:
        app_id = app['id']
        date_applied = datetime.strptime(app['date_applied'], '%Y-%m-%d')
        final_status = app['status']
        current_date = date_applied
        
        # Always start with "Applied"
        history_data.append({
            'id': history_id,
            'application_id': app_id,
            'status': 'Applied',
            'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
        })
        history_id += 1
        
        # Generate progression based on final status
        if final_status == "Applied":
            # Just applied, no progression yet
            pass
            
        elif final_status == "Online Assessment":
            # Applied -> Online Assessment
            current_date += timedelta(days=random.randint(3, 8))
            history_data.append({
                'id': history_id,
                'application_id': app_id,
                'status': 'Online Assessment',
                'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
            })
            history_id += 1
            
        elif "Interviewing" in final_status:
            # Extract round number (e.g., "Interviewing: 2nd round" -> 2)
            round_match = final_status.split(":")[-1].strip()
            round_text = round_match.split()[0]  # e.g., "2nd"
            # Extract just the number part
            round_num = int(''.join(filter(str.isdigit, round_text)))
            
            # Decide if they went through OA first (50% chance)
            if random.choice([True, False]):
                current_date += timedelta(days=random.randint(3, 8))
                history_data.append({
                    'id': history_id,
                    'application_id': app_id,
                    'status': 'Online Assessment',
                    'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                history_id += 1
            
            # Add interview rounds up to the final round
            for r in range(1, round_num + 1):
                current_date += timedelta(days=random.randint(7, 14))
                round_suffix = "st" if r == 1 else "nd" if r == 2 else "rd" if r == 3 else "th"
                history_data.append({
                    'id': history_id,
                    'application_id': app_id,
                    'status': f'Interviewing: {r}{round_suffix} round',
                    'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                history_id += 1
                
        elif final_status == "Rejected":
            # Create a realistic rejection path
            rejection_paths = [
                # Path 1: Applied -> Rejected (direct rejection)
                [],
                # Path 2: Applied -> OA -> Rejected
                ['Online Assessment'],
                # Path 3: Applied -> OA -> 1st interview -> Rejected
                ['Online Assessment', 'Interviewing: 1st round'],
                # Path 4: Applied -> 1st interview -> Rejected (no OA)
                ['Interviewing: 1st round'],
                # Path 5: Applied -> OA -> 1st -> 2nd -> Rejected
                ['Online Assessment', 'Interviewing: 1st round', 'Interviewing: 2nd round'],
                # Path 6: Applied -> 1st -> 2nd -> Rejected
                ['Interviewing: 1st round', 'Interviewing: 2nd round'],
                # Path 7: Applied -> OA -> 1st -> 2nd -> 3rd -> Rejected
                ['Online Assessment', 'Interviewing: 1st round', 'Interviewing: 2nd round', 'Interviewing: 3rd round']
            ]
            
            # Choose path based on how long ago they applied
            days_elapsed = (datetime.now() - date_applied).days
            if days_elapsed < 14:
                # Recent applications - likely direct rejection or after OA
                path = random.choice(rejection_paths[:3])
            elif days_elapsed < 30:
                # Medium time - could be rejected after 1-2 rounds
                path = random.choice(rejection_paths[:5])
            else:
                # Older applications - could go through full process
                path = random.choice(rejection_paths)
            
            # Add the progression steps
            for step in path:
                if step == 'Online Assessment':
                    current_date += timedelta(days=random.randint(3, 8))
                else:  # Interview rounds
                    current_date += timedelta(days=random.randint(7, 14))
                
                history_data.append({
                    'id': history_id,
                    'application_id': app_id,
                    'status': step,
                    'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                history_id += 1
            
            # Finally add the rejection
            current_date += timedelta(days=random.randint(1, 7))
            history_data.append({
                'id': history_id,
                'application_id': app_id,
                'status': 'Rejected',
                'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
            })
            history_id += 1
            
        elif final_status == "Offer":
            # Create a realistic offer path - offers usually come after multiple rounds
            offer_paths = [
                # Path 1: Applied -> OA -> 1st -> 2nd -> Offer
                ['Online Assessment', 'Interviewing: 1st round', 'Interviewing: 2nd round'],
                # Path 2: Applied -> OA -> 1st -> 2nd -> 3rd -> Offer
                ['Online Assessment', 'Interviewing: 1st round', 'Interviewing: 2nd round', 'Interviewing: 3rd round'],
                # Path 3: Applied -> 1st -> 2nd -> 3rd -> Offer (no OA)
                ['Interviewing: 1st round', 'Interviewing: 2nd round', 'Interviewing: 3rd round'],
                # Path 4: Applied -> OA -> 1st -> 2nd -> 3rd -> 4th -> Offer
                ['Online Assessment', 'Interviewing: 1st round', 'Interviewing: 2nd round', 'Interviewing: 3rd round', 'Interviewing: 4th round']
            ]
            
            path = random.choice(offer_paths)
            
            # Add the progression steps
            for step in path:
                if step == 'Online Assessment':
                    current_date += timedelta(days=random.randint(3, 8))
                else:  # Interview rounds
                    current_date += timedelta(days=random.randint(7, 14))
                
                history_data.append({
                    'id': history_id,
                    'application_id': app_id,
                    'status': step,
                    'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                history_id += 1
            
            # Finally add the offer
            current_date += timedelta(days=random.randint(1, 5))
            history_data.append({
                'id': history_id,
                'application_id': app_id,
                'status': 'Offer',
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


def seed_database_with_mock_data(data_service, num_applications: int = 20):
    """Seed database with mock data and realistic status histories."""
    print(f"🌱 Seeding database with {num_applications} mock applications...")
    
    # Generate mock applications
    mock_data = generate_mock_data(num_applications)
    
    # First, add all applications to get their IDs
    success_count = 0
    application_ids = []
    for app_data in mock_data:
        # Remove id field as it will be auto-generated
        form_data = {k: v for k, v in app_data.items() if k != 'id'}
        result = data_service.add_application(form_data)
        if result['success']:
            success_count += 1
            application_ids.append(result['id'])
            # Update the mock data with the real ID for history generation
            app_data['id'] = result['id']
    
    # Generate and add realistic status histories
    print(f"🔄 Generating realistic status histories...")
    history_data = generate_status_history(mock_data)
    
    # Clear existing status history (which only has "Applied" entries) and add realistic ones
    history_count = 0
    try:
        with data_service.db.get_connection() as conn:
            # Clear auto-generated status histories
            for app_id in application_ids:
                conn.execute("DELETE FROM status_history WHERE application_id = ?", (app_id,))
            
            # Add realistic status histories
            for history_entry in history_data:
                conn.execute('''
                    INSERT INTO status_history (application_id, status, timestamp)
                    VALUES (?, ?, ?)
                ''', (
                    history_entry['application_id'],
                    history_entry['status'],
                    history_entry['timestamp']
                ))
                history_count += 1
            conn.commit()
            
        print(f"✅ Successfully added {success_count}/{num_applications} applications")
        print(f"✅ Successfully generated {history_count} status history entries")
        
    except Exception as e:
        print(f"⚠️ Error generating status histories: {e}")
    
    return success_count 