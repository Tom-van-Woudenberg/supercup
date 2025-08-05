"""
Crew progression tracking functions for rowing competition analysis.
Handles tracking crews through different competition stages.
"""

import pandas as pd
from collections import defaultdict


def extract_veld(veld_value):
    """
    Extract veld category from veld column value.
    
    Args:
        veld_value: Raw veld value from data
        
    Returns:
        str: Standardized veld category
    """
    if pd.isna(veld_value):
        return 'Unknown'
    
    veld_str = str(veld_value).strip()
    
    # Look for specific veld patterns - order matters, check more specific patterns first
    if 'LVG-B' in veld_str:
        return 'LVG-B'
    elif 'VG-B' in veld_str:
        return 'VG-B'
    elif 'LVE' in veld_str:
        return 'LVE'
    elif 'LVG' in veld_str:
        return 'LVG'
    elif 'LVB' in veld_str:
        return 'LVB'
    elif 'VE' in veld_str:
        return 'VE'
    elif 'VG' in veld_str:
        return 'VG'
    elif 'VB' in veld_str:
        return 'VB'
    elif 'MVG-B' in veld_str:
        return 'MVG-B'
    elif 'MG-B' in veld_str:
        return 'MG-B'
    elif 'MVE' in veld_str:
        return 'MVE'
    elif 'MVG' in veld_str:
        return 'MVG'
    elif 'MVB' in veld_str:
        return 'MVB'
    elif 'ME' in veld_str:
        return 'ME'
    elif 'MG' in veld_str:
        return 'MG'
    elif 'MB' in veld_str:
        return 'MB'
    else:
        return veld_str if veld_str not in ['', 'nan', 'None'] else 'Other'


def track_crew_progression_with_slag(all_race_data):
    """
    Track crew progression using consistent crew identifiers across all stages.
    
    Args:
        all_race_data: Dictionary containing race data organized by race type and race name
        
    Returns:
        dict: Dictionary mapping consistent crew_id to progression information
    """
    crew_progression = {}
    
    stage_names = {
        'voorwedstrijden': 'Voorwedstrijden',
        'challenges': 'Challenges', 
        'halve finales': 'Halve Finales',
        'finales': 'Finales'
    }
    
    for race_type, stage_name in stage_names.items():
        race_data = all_race_data.get(race_type, {})
        
        # Process all races in this stage
        for race_name, crew_entries in race_data.items():
            for entry in crew_entries:
                crew_code = entry.get('code')
                ploeg_name = entry.get('ploeg')
                veld_value = entry.get('veld')
                crew_member = entry.get('crew_member', '')
                race_sub_number = entry.get('race_sub_number', 'Unknown')
                
                # Create consistent crew identifier based on code and crew member
                # This ensures same crew is tracked across all stages
                consistent_crew_id = f"{crew_code}_{crew_member.replace(' ', '_')}" if crew_member else crew_code
                
                if crew_code and consistent_crew_id:
                    veld = extract_veld(veld_value)
                    
                    if consistent_crew_id not in crew_progression:
                        crew_progression[consistent_crew_id] = {
                            'code': crew_code,
                            'ploeg': ploeg_name,
                            'veld': veld,
                            'crew_member': crew_member,
                            'stages': {}
                        }
                    
                    # Create stage identifier
                    if stage_name == 'Finales':
                        stage_id = f"{stage_name} ({race_sub_number})"
                    else:
                        stage_id = f"{stage_name} {race_sub_number}"
                    
                    crew_progression[consistent_crew_id]['stages'][stage_name] = stage_id
    
    return crew_progression


def analyze_crew_progression(crew_progressions):
    """
    Analyze crew progression data and generate summary statistics.
    
    Args:
        crew_progressions: Dictionary from track_crew_progression_with_slag()
        
    Returns:
        dict: Analysis results including veld distribution and stage participation
    """
    # Count by veld
    veld_distribution = defaultdict(int)
    for crew_id, progression in crew_progressions.items():
        veld_distribution[progression['veld']] += 1
    
    # Check progression through stages  
    stage_participation = defaultdict(int)
    for crew_id, progression in crew_progressions.items():
        for stage in progression['stages']:
            stage_participation[stage] += 1
    
    # Find crews that don't make it to finales
    crews_not_in_finales = []
    for crew_id, progression in crew_progressions.items():
        if 'Finales' not in progression['stages']:
            last_stage = list(progression['stages'].keys())[-1] if progression['stages'] else 'None'
            crews_not_in_finales.append({
                'ploeg': progression['ploeg'],
                'crew_member': progression['crew_member'],
                'veld': progression['veld'],
                'last_stage': last_stage
            })
    
    return {
        'total_crews': len(crew_progressions),
        'veld_distribution': dict(veld_distribution),
        'stage_participation': dict(stage_participation),
        'crews_not_in_finales': crews_not_in_finales
    }
