"""
Data processing functions for rowing competition analysis.
Handles Excel import and race data extraction with slag information.
"""

import pandas as pd


def process_race_data_with_slag(df):
    """
    Enhanced function to process race data that properly captures:
    - Slag information (appears as header before each race section)
    - Crew data rows 
    - Crew member names (appears in row after each crew)
    
    Args:
        df: Raw pandas DataFrame from Excel import
        
    Returns:
        dict: Dictionary containing processed DataFrames for each race type
    """
    
    # Helper function to identify race type
    def get_race_type(race_name):
        if pd.isna(race_name) or not isinstance(race_name, str):
            return None
        race_name_lower = race_name.lower()
        if 'voorwedstrijd' in race_name_lower:
            return 'voorwedstrijden'
        elif 'challenge' in race_name_lower:
            return 'challenges'
        elif 'halve' in race_name_lower and 'finale' in race_name_lower:
            return 'halve finales'
        elif 'finale' in race_name_lower:
            return 'finales'
        else:
            return 'other'
    
    # Helper function to extract race number
    def extract_race_numbers(race_name, race_type):
        race_number = None
        race_sub_number = None
        
        if 'race' in race_name.lower():
            try:
                race_number = int(race_name.split('race')[1].split('-')[0].strip())
            except:
                pass
        
        try:
            if race_type == 'voorwedstrijden' and 'voorwedstrijd' in race_name.lower():
                race_sub_number = int(race_name.split('voorwedstrijd')[1].strip().split()[0])
            elif race_type == 'challenges' and 'challenge' in race_name.lower():
                race_sub_number = int(race_name.split('challenge')[1].strip().split()[0])
            elif race_type == 'halve finales' and 'finale' in race_name.lower():
                race_sub_number = int(race_name.split('finale')[1].strip().split()[0])
            elif race_type == 'finales' and 'finale' in race_name.lower():
                if '-finale' in race_name.lower():
                    race_sub_number = race_name.split('-finale')[0].split()[-1]
        except:
            pass
            
        return race_number, race_sub_number
    
    # Add race type column
    df['race_type'] = df.iloc[:, 0].apply(get_race_type)
    
    # Process each race type
    race_types = ['voorwedstrijden', 'challenges', 'halve finales', 'finales']
    datasets = {}
    
    for race_type in race_types:
        race_data_list = []
        race_rows = df[df['race_type'] == race_type].index.tolist()
        
        for race_idx in race_rows:
            race_name = df.iloc[race_idx, 0]
            race_number, race_sub_number = extract_race_numbers(race_name, race_type)
            
            # Look for the slag header and then process crew data
            slag_found = False
            crew_counter = 0
            
            for i in range(race_idx + 1, min(race_idx + 50, len(df))):
                if i >= len(df):
                    break
                    
                current_row = df.iloc[i]
                
                # Check for slag header
                if not slag_found:
                    for val in current_row.values:
                        if pd.notna(val) and str(val).strip().lower() == 'slag':
                            slag_found = True
                            break
                    continue
                
                # After finding slag, look for crew data
                if slag_found:
                    first_col = str(current_row.iloc[0]).strip()
                    
                    # Stop if we hit the next race
                    if pd.notna(current_row.iloc[0]) and any(x in str(current_row.iloc[0]).lower() 
                                                            for x in ['race', 'voorwedstrijd', 'challenge', 'finale']):
                        break
                    
                    # Check if this is a crew data row (has position number)
                    if first_col.isdigit():
                        crew_counter += 1
                        crew_row = current_row.copy()
                        
                        # Get crew member name from next row if available
                        crew_member_name = ""
                        if i + 1 < len(df):
                            next_row = df.iloc[i + 1]
                            # The crew member name appears in the 'ploeg' column (index 2) of the next row
                            if pd.notna(next_row.iloc[2]) and not str(next_row.iloc[0]).strip().isdigit():
                                crew_member_name = str(next_row.iloc[2]).strip()
                        
                        # Add metadata
                        crew_row['race_name'] = race_name
                        crew_row['race_number'] = race_number
                        crew_row['race_sub_number'] = race_sub_number
                        crew_row['race_type'] = race_type
                        crew_row['crew_member'] = crew_member_name
                        crew_row['crew_unique_id'] = f"{crew_row.iloc[1]}_{race_sub_number}_{crew_counter}"  # code_race_position
                        
                        race_data_list.append(crew_row)
        
        # Create dataframe with proper headers
        if race_data_list:
            race_df = pd.DataFrame(race_data_list)
            # Apply standard headers (excluding time columns col_5 to col_12)
            headers = ['pos.', 'code', 'ploeg', 'veld', 'baan', 'next_round']
            column_mapping = {}
            for i, header in enumerate(headers):
                if i in race_df.columns:
                    column_mapping[i] = header
            for col in ['race_name', 'race_number', 'race_sub_number', 'race_type', 'crew_member', 'crew_unique_id']:
                if col in race_df.columns:
                    column_mapping[col] = col
            race_df = race_df.rename(columns=column_mapping)
            
            # Keep only the relevant columns (remove time columns)
            columns_to_keep = ['pos.', 'code', 'ploeg', 'veld', 'baan', 'next_round', 
                             'race_name', 'race_number', 'race_sub_number', 'race_type', 
                             'crew_member', 'crew_unique_id']
            race_df = race_df[[col for col in columns_to_keep if col in race_df.columns]]
            datasets[race_type] = race_df
        else:
            datasets[race_type] = pd.DataFrame()
    
    return datasets


def load_and_process_excel(file_path):
    """
    Load Excel file and process race data.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        dict: Processed datasets by race type
    """
    # Import the Excel file without header assumption
    df = pd.read_excel(file_path, header=None)
    
    # Process the data
    datasets = process_race_data_with_slag(df)
    
    return datasets
