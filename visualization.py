"""
Sankey diagram creation functions for rowing competition visualization.
Creates interactive flow diagrams showing crew progression through stages.
"""

import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict
import re


def detect_competition_format(all_race_data):
    """
    Automatically detect the competition format     print(f"Found {len([n for n in node_counts if n.startswith('Veld')])} veld categories")
      print(f"Column 4 (Eindklassering) - first 10:")
    for node in col4_nodes[:10]:
        pos = col4_positions[node]
        count = node_counts[node]
        position_num = get_position_number(node)
        veld = node.split('(')[1].split(')')[0] if '(' in node else "Unknown"
        print(f"  {node:<30} y={pos['y']:.3f} (pos: {position_num}) [{veld}]")
    if len(col4_nodes) > 10:
        print(f"  ... and {len(col4_nodes)-10} more positions")"Found {len([n for n in node_counts if '_' in n and not n.startswith('Eindklassering')])} detailed halve finale nodes")
    print(f"Found {len([n for n in node_counts if n.startswith('Finale')])} individual finales")
    print(f"Found {len([n for n in node_counts if n.startswith('Eindklassering')])} final positions")d on the data
    Returns configuration for field types, finale groups, and colors
    """
    print("Detecting competition format...")
    
    # Collect all unique veld categories from the data
    veld_categories = set()
    finale_letters = set()
    halve_finale_groups = set()
    
    # Extract veld categories from all race types
    for race_type, races in all_race_data.items():
        for race_name, crew_entries in races.items():
            for entry in crew_entries:
                veld = entry.get('veld', '')
                if veld and veld != 'Unknown':
                    veld_categories.add(veld)
            
            # Extract finale information
            if 'finale' in race_name.lower():
                # Extract finale letter (A, B, C, D, E, F, G, etc.)
                finale_match = re.search(r'([A-G])-finale', race_name, re.IGNORECASE)
                if finale_match:
                    finale_letters.add(finale_match.group(1).upper())
                
                # Extract halve finale groups (ABC, DEFG, DE, etc.)
                halve_match = re.search(r'halve-([A-G]+)-finale', race_name, re.IGNORECASE)
                if halve_match:
                    halve_finale_groups.add(halve_match.group(1).upper())
    
    # Sort veld categories intelligently
    veld_list = sorted(list(veld_categories))
    
    # Detect boat class (2x, 4-, etc.)
    boat_classes = set()
    for veld in veld_list:
        if '2x' in veld:
            boat_classes.add('2x')
        elif '4-' in veld:
            boat_classes.add('4-')
        elif '4+' in veld:
            boat_classes.add('4+')
        elif '8+' in veld:
            boat_classes.add('8+')
    
    # Detect naming convention (VE vs ME, LVG vs LMG, etc.)
    prefix_patterns = {}
    for veld in veld_list:
        # Check main prefix patterns (E, G, G-B, B)
        if 'E' in veld and not veld.startswith('L'):
            if veld.startswith('VE'):
                prefix_patterns['E'] = 'V'
            elif veld.startswith('ME'):
                prefix_patterns['E'] = 'M'
        if 'G' in veld and not veld.startswith('L'):
            if veld.startswith('VG'):
                prefix_patterns['G'] = 'V'
            elif veld.startswith('MG'):
                prefix_patterns['G'] = 'M'
        if 'B' in veld and not veld.startswith('L') and 'G-B' not in veld:
            if veld.startswith('VB'):
                prefix_patterns['B'] = 'V'
            elif veld.startswith('MB'):
                prefix_patterns['B'] = 'M'
        
        # Check L prefix patterns (LE, LG, LG-B, LB)
        if 'LVE' in veld or 'LME' in veld:
            if 'LVE' in veld:
                prefix_patterns['LE'] = 'LV'
            elif 'LME' in veld:
                prefix_patterns['LE'] = 'LM'
        if 'LVG' in veld or 'LMG' in veld:
            if 'LVG' in veld:
                prefix_patterns['LG'] = 'LV'
            elif 'LMG' in veld:
                prefix_patterns['LG'] = 'LM'
        if 'LVB' in veld or 'LMB' in veld:
            if 'LVB' in veld:
                prefix_patterns['LB'] = 'LV'
            elif 'LMB' in veld:
                prefix_patterns['LB'] = 'LM'
    
    # Determine veld ordering based on detected patterns
    boat_class = list(boat_classes)[0] if boat_classes else '2x'
    main_prefix = prefix_patterns.get('E', 'V')  # Default to V if not detected
    l_prefix = prefix_patterns.get('LG', 'LV')   # Default to LV if not detected
    le_prefix = prefix_patterns.get('LE', 'LV')  # For LE fields
    lb_prefix = prefix_patterns.get('LB', 'LV')  # For LB fields
    
    # Create standardized veld order
    base_order = [
        f'{main_prefix}E {boat_class}',
        f'{main_prefix}G {boat_class}',
        f'{main_prefix}G-B {boat_class}',
        f'{main_prefix}B {boat_class}',
        f'{le_prefix}E {boat_class}',
        f'{l_prefix}G {boat_class}',
        f'{l_prefix}G-B {boat_class}',
        f'{lb_prefix}B {boat_class}'
    ]
    
    # Filter to only include categories that exist in data
    veld_order = [v for v in base_order if v in veld_categories]
    # Add any remaining categories not in the standard order
    remaining = [v for v in veld_list if v not in veld_order]
    veld_order.extend(sorted(remaining))
    
    # Determine finale structure
    finale_list = sorted(list(finale_letters))
    
    # Determine halve finale groupings
    halve_groups = sorted(list(halve_finale_groups))
    if not halve_groups:
        # Fallback: infer from finale letters
        if len(finale_list) <= 3:
            halve_groups = ['ABC']
        elif len(finale_list) <= 4:
            halve_groups = ['ABC', 'DE']
        elif len(finale_list) <= 6:
            halve_groups = ['ABC', 'DEFG']
        else:
            halve_groups = ['ABC', 'DEFG']
    
    config = {
        'veld_order': veld_order,
        'boat_class': boat_class,
        'finale_letters': finale_list,
        'halve_finale_groups': halve_groups,
        'prefix_patterns': prefix_patterns
    }
    
    print(f"Detected configuration:")
    print(f"  - Boat class: {boat_class}")
    print(f"  - Veld categories: {len(veld_order)} found")
    print(f"  - Finale letters: {finale_list}")
    print(f"  - Halve finale groups: {halve_groups}")
    print(f"  - Prefix patterns: {prefix_patterns}")
    
    return config


def get_adaptive_colors(config):
    """
    Generate color scheme based on the detected configuration
    """
    boat_class = config['boat_class']
    prefix_patterns = config['prefix_patterns']
    
    # Base color palette - highly distinct colors
    colors = {
        'red_bright': '#E74C3C',      # Bright Red
        'blue_bright': '#3498DB',     # Bright Blue  
        'orange_bright': '#FF8C00',   # Bright Orange
        'green_bright': '#00FF7F',    # Bright Green  
        'hot_pink': '#FF1493',        # Hot Pink
        'brown': '#8B4513',           # Brown
        'red_dark': '#8B0000',        # Dark Red
        'gray': '#95A5A6'             # Gray
    }
    
    # Create adaptive color mapping
    main_prefix = prefix_patterns.get('E', 'V')
    l_prefix = prefix_patterns.get('LG', 'LV')
    le_prefix = prefix_patterns.get('LE', 'LV')
    lb_prefix = prefix_patterns.get('LB', 'LV')
    
    veld_colors = {}
    for veld in config['veld_order']:
        # Use exact matching to prevent substring conflicts
        # Check for L fields first (more specific patterns) with exact matching
        if veld == f'{le_prefix}E {boat_class}':
            veld_colors[veld] = colors['red_dark']
        elif veld == f'{l_prefix}G-B {boat_class}':  # Check LG-B before LG
            veld_colors[veld] = colors['hot_pink']  # Hot Pink for L G-B fields (very distinct)
        elif veld == f'{l_prefix}G {boat_class}':
            veld_colors[veld] = colors['green_bright']
        elif veld == f'{lb_prefix}B {boat_class}':
            veld_colors[veld] = colors['brown']
        # Then check for main fields with exact matching
        elif veld == f'{main_prefix}E {boat_class}':
            veld_colors[veld] = colors['red_bright']
        elif veld == f'{main_prefix}G-B {boat_class}':  # Check MG-B before MG
            veld_colors[veld] = colors['orange_bright']  # Bright Orange for main G-B fields (very distinct from hot pink)
        elif veld == f'{main_prefix}G {boat_class}':
            veld_colors[veld] = colors['blue_bright']
        elif veld == f'{main_prefix}B {boat_class}':
            veld_colors[veld] = colors['gray']
        else:
            veld_colors[veld] = colors['gray']
    
    return veld_colors


def create_adaptive_halve_finale_groups(race_name, config):
    """
    Determine which halve finale group a race belongs to based on configuration
    """
    race_upper = race_name.upper()
    
    # Check each configured halve finale group
    for group in config['halve_finale_groups']:
        if group in race_upper:
            return group
    
    # Fallback: try to infer from finale letters in race name
    if 'ABC' in race_upper:
        return 'ABC'
    elif 'DEFG' in race_upper:
        return 'DEFG'
    elif 'DE' in race_upper:
        return 'DE'
    else:
        return 'OTHER'


def get_finale_group_from_letter(finale_letter, config):
    """
    Determine which halve finale group a finale letter belongs to
    """
    finale_letter = finale_letter.upper()
    
    # Standard groupings based on detected halve finale groups
    if 'ABC' in config['halve_finale_groups']:
        if finale_letter in ['A', 'B', 'C']:
            return 'ABC'
    
    if 'DEFG' in config['halve_finale_groups']:
        if finale_letter in ['D', 'E', 'F', 'G']:
            return 'DEFG'
    
    if 'DE' in config['halve_finale_groups']:
        if finale_letter in ['D', 'E']:
            return 'DE'
    
    # Fallback for other letters
    if finale_letter in ['A', 'B', 'C']:
        return 'ABC'
    elif finale_letter in ['D', 'E']:
        return 'DE'
    elif finale_letter in ['F', 'G']:
        return 'FG'
    else:
        return 'OTHER'


# Create 4-column cumulative positioning function (veld → halve finale groups → individual finales → final positions)
def create_four_column_cumulative_sankey(all_race_data):
    """
    Adaptive 4-Column Sankey: Veld Categories → Detailed Halve Finale Nodes → Individual Finales → Final Positions
    Automatically detects competition format and adapts to different boat classes and naming conventions
    """
    import plotly.graph_objects as go
    from collections import defaultdict
    
    print("Creating adaptive 4-column cumulative Sankey...")
    
    # Step 0: Detect competition format
    config = detect_competition_format(all_race_data)
    veld_colors = get_adaptive_colors(config)
    
    # Step 1: Collect flows and counts for all four columns
    flows = []
    node_counts = defaultdict(int)
    
    # Process halve finales data for column 1 → column 2 (unlabeled halve finale nodes)
    if 'halve finales' in all_race_data:
        print("Processing halve finales data (veld → unlabeled halve finale nodes):")
        for race_name, crew_entries in all_race_data['halve finales'].items():
            print(f"  Processing: {race_name} ({len(crew_entries)} crews)")
            
            # Determine halve finale group adaptively
            halve_group = create_adaptive_halve_finale_groups(race_name, config)
            
            for entry in crew_entries:
                veld = entry.get('veld', 'Unknown')
                if veld and veld != 'Unknown':
                    source = f"Veld {veld}"
                    target = f"{halve_group}_{veld}"  # Internal identifier, will be empty in labels
                    
                    flows.append((source, target, 1))
                    node_counts[source] += 1
                    node_counts[target] += 1
    
    # Process finales data for column 2 → column 3 (detailed halve finale nodes → individual finales)
    if 'finales' in all_race_data:
        print("\nProcessing finales data (detailed halve finale nodes → individual finales):")
        for race_name, crew_entries in all_race_data['finales'].items():
            print(f"  Processing: {race_name} ({len(crew_entries)} crews)")
            
            # Extract finale letter adaptively
            finale_match = re.search(r'([A-G])-finale', race_name, re.IGNORECASE)
            if not finale_match:
                continue
                
            finale_letter = finale_match.group(1).upper()
            target = f"Finale {finale_letter}"
            
            # Determine which halve finale group this finale belongs to
            finale_group = get_finale_group_from_letter(finale_letter, config)
            
            # Create flows from each veld's detailed halve finale node to this finale
            # Group crews by veld to create proper flows
            veld_counts = defaultdict(int)
            for entry in crew_entries:
                veld = entry.get('veld', 'Unknown')
                if veld and veld != 'Unknown':
                    veld_counts[veld] += 1
            
            # Create flows from detailed halve finale nodes
            for veld, count in veld_counts.items():
                source = f"{finale_group}_{veld}"
                flows.append((source, target, count))
                node_counts[source] += count
                node_counts[target] += count
    
    # Process finales data for column 3 → column 4 (individual finales → final positions with field tracking)
    if 'finales' in all_race_data:
        print("\nProcessing finales positions (individual finales → final positions with field tracking):")
        
        # Calculate position offsets based on detected finale structure
        finale_position_offsets = {}
        position_offset = 0
        for finale_letter in sorted(config['finale_letters']):
            finale_position_offsets[finale_letter] = position_offset
            position_offset += 6  # Standard 6 positions per finale
        
        for race_name, crew_entries in all_race_data['finales'].items():
            print(f"  Processing positions for: {race_name} ({len(crew_entries)} crews)")
            
            # Extract finale letter
            finale_match = re.search(r'([A-G])-finale', race_name, re.IGNORECASE)
            if not finale_match:
                continue
                
            finale_letter = finale_match.group(1).upper()
            source = f"Finale {finale_letter}"
            position_offset = finale_position_offsets.get(finale_letter, 0)
            
            # Sort crew entries by position within this finale
            def get_position(entry):
                pos = entry.get('pos', '') or entry.get('pos.', '')
                if isinstance(pos, int):
                    return pos
                elif isinstance(pos, str) and pos.isdigit():
                    return int(pos)
                else:
                    return 999  # Put invalid positions at the end
            
            sorted_entries = sorted(crew_entries, key=get_position)
            
            # Create flows from finale to final positions with field tracking
            for i, entry in enumerate(sorted_entries):
                veld = entry.get('veld', 'Unknown')
                if veld and veld != 'Unknown':
                    final_position = position_offset + i + 1
                    target = f"Eindklassering {final_position} ({veld})"
                    flows.append((source, target, 1))
                    node_counts[source] += 1
                    node_counts[target] += 1
    
    
    print(f"\nFound {len([n for n in node_counts if n.startswith('Veld')])} veld categories")
    print(f"Found {len([n for n in node_counts if '_' in n and not n.startswith('Position')])} detailed halve finale nodes")
    print(f"Found {len([n for n in node_counts if n.startswith('Finale')])} individual finales")
    print(f"Found {len([n for n in node_counts if n.startswith('Position')])} final positions")
    
    # Step 2: Create ordered node lists for all four columns
    # Column 1: Veld categories (using detected order)
    col1_nodes = [f"Veld {v}" for v in config['veld_order'] if f"Veld {v}" in node_counts]
    
    # Column 2: Detailed halve finale nodes (grouped by detected halve finale groups, then by veld)
    col2_nodes = []
    
    # Group nodes by halve finale groups
    group_nodes = {group: [] for group in config['halve_finale_groups']}
    other_nodes = []
    
    for node in node_counts.keys():
        if '_' in node and not node.startswith('Eindklassering') and not node.startswith('Veld'):
            assigned = False
            for group in config['halve_finale_groups']:
                if node.startswith(f"{group}_"):
                    group_nodes[group].append(node)
                    assigned = True
                    break
            if not assigned:
                other_nodes.append(node)
    
    # Sort within each group by veld category using detected order
    def sort_by_veld(node_list):
        """Sort nodes by veld category according to detected order"""
        def get_veld_priority(node):
            for i, veld in enumerate(config['veld_order']):
                if veld in node:
                    return i
            return 999  # Unknown veld goes to end
        return sorted(node_list, key=get_veld_priority)
    
    # Combine all groups in order
    for group in sorted(config['halve_finale_groups']):
        sorted_group = sort_by_veld(group_nodes[group])
        col2_nodes.extend(sorted_group)
    col2_nodes.extend(sort_by_veld(other_nodes))
    
    # Column 3: Individual finales (using detected finale letters)
    finale_order = [f'Finale {letter}' for letter in sorted(config['finale_letters'])]
    col3_nodes = [f for f in finale_order if f in node_counts]
    
    # Column 4: Final positions (sorted by position number)
    col4_nodes = []
    position_nodes = [n for n in node_counts.keys() if n.startswith('Eindklassering')]
    # Sort by position number
    def get_position_number(node):
        try:
            return int(node.split('Eindklassering ')[1].split(' ')[0])
        except:
            return 999
    col4_nodes = sorted(position_nodes, key=get_position_number)
    
    print(f"\nColumn 1 (Veld): {len(col1_nodes)} nodes")
    print(f"Column 2 (Halve Finales): {len(col2_nodes)} nodes")
    print(f"Column 3 (Finales): {len(col3_nodes)} nodes")
    print(f"Column 4 (Eindklassering): {len(col4_nodes)} nodes")
    
    # Step 3: Calculate cumulative positions for all four columns
    def calc_positions(nodes, counts, x_pos):
        total = sum(counts[node] for node in nodes)
        positions = {}
        cumulative = 0
        
        for node in nodes:
            value = counts[node]
            y_center = (cumulative + value/2) / total
            y_pos = max(0.001, min(0.999, y_center))
            positions[node] = {'x': x_pos, 'y': y_pos}
            cumulative += value
            
        return positions
    
    col1_positions = calc_positions(col1_nodes, node_counts, 0.02)  # Left column
    col2_positions = calc_positions(col2_nodes, node_counts, 0.35)  # Second column
    col3_positions = calc_positions(col3_nodes, node_counts, 0.65)  # Third column
    col4_positions = calc_positions(col4_nodes, node_counts, 0.98)  # Right column
    
    all_positions = {**col1_positions, **col2_positions, **col3_positions, **col4_positions}
    
    # Show positioning (first few only to avoid too much output)
    print("\nColumn 1 (Veld categorieën):")
    for node in col1_nodes:
        pos = col1_positions[node]
        count = node_counts[node]
        print(f"  {node:<20} y={pos['y']:.3f} (count: {count})")
    
    print(f"\nColumn 4 (Final Positions) - first 10:")
    for node in col4_nodes[:10]:
        pos = col4_positions[node]
        count = node_counts[node]
        position_num = get_position_number(node)
        veld = node.split('(')[1].split(')')[0] if '(' in node else "Unknown"
        print(f"  {node:<30} y={pos['y']:.3f} (pos: {position_num}) [{veld}]")
    if len(col4_nodes) > 10:
        print(f"  ... and {len(col4_nodes)-10} more positions")
    
    # Step 4: Create Sankey
    all_nodes = col1_nodes + col2_nodes + col3_nodes + col4_nodes
    node_to_index = {node: i for i, node in enumerate(all_nodes)}
    
    # Node data
    node_x = [all_positions[node]['x'] for node in all_nodes]
    node_y = [all_positions[node]['y'] for node in all_nodes]
    
    # Create labels array - empty strings for halve finale nodes
    node_labels = []
    for node in all_nodes:
        # Check if this is a halve finale node (any group prefix followed by underscore)
        is_halve_finale = False
        for group in config['halve_finale_groups']:
            if node.startswith(f'{group}_'):
                is_halve_finale = True
                break
        
        if is_halve_finale:
            node_labels.append("")  # No label for halve finale nodes
        else:
            node_labels.append(node)  # Regular label for other nodes
    
    # Enhanced adaptive color scheme
    node_colors = []
    
    for node in all_nodes:
        # Helper to get veld from node string with precise matching
        def extract_veld(node_str):
            # Sort by length descending to match longer strings first (e.g., LMG-B 4- before MG-B 4-)
            sorted_velds = sorted(config['veld_order'], key=len, reverse=True)
            for veld in sorted_velds:
                # Use more precise matching - check if the veld appears as a complete word
                if f" {veld}" in node_str or node_str.endswith(veld) or f"({veld})" in node_str:
                    return veld
            return None
        
        if node.startswith('Veld'):
            # Color veld category nodes with their detected colors
            veld = extract_veld(node)
            node_colors.append(veld_colors.get(veld, '#95A5A6'))
        elif any(node.startswith(f'{group}_') for group in config['halve_finale_groups']):
            # Color halve finale nodes based on their field category (same colors as veld categories)
            veld = extract_veld(node)
            node_colors.append(veld_colors.get(veld, '#95A5A6'))
        elif node.startswith('Finale'):
            node_colors.append('#95A5A6')  # Gray for finale nodes (mixed inflows/outflows)
        elif node.startswith('Eindklassering'):
            # Color position nodes with the same colors as their corresponding veld categories
            veld = extract_veld(node)
            node_colors.append(veld_colors.get(veld, '#95A5A6'))
        else:
            node_colors.append('#95A5A6')  # Gray for others
    
    
    # Create adaptive color mapping for links
    veld_link_colors = {}
    for veld, color_hex in veld_colors.items():
        # Convert hex to rgba
        rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
        rgba = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.6)'
        veld_link_colors[f'Veld {veld}'] = rgba
    
    # Use the same colors for halve finale nodes 
    halve_finale_colors = {}
    for veld in config['veld_order']:
        rgba_color = veld_link_colors.get(f'Veld {veld}', 'rgba(128,128,128,0.4)')
        # Add colors for all halve finale group combinations
        for group in config['halve_finale_groups']:
            halve_finale_colors[f'{group}_{veld}'] = rgba_color
    
    # Combine all link colors
    all_link_colors = {**veld_link_colors, **halve_finale_colors}
    
    # Links with enhanced colors
    flow_dict = defaultdict(int)
    for source, target, value in flows:
        if source in node_to_index and target in node_to_index:
            flow_dict[(source, target)] += value
    
    link_sources = [node_to_index[s] for s, t in flow_dict.keys()]
    link_targets = [node_to_index[t] for s, t in flow_dict.keys()]
    link_values = list(flow_dict.values())
    
    # Color links based on source and target
    link_colors_final = []
    for source, target in flow_dict.keys():
        if source in all_link_colors:
            # Use source-based coloring for veld and halve finale flows
            link_colors_final.append(all_link_colors[source])
        elif source.startswith('Finale') and target.startswith('Eindklassering'):
            # For finale-to-position flows, use the field color from the target position adaptively
            # Sort by length descending to match longer strings first (e.g., LMG-B 4- before MG-B 4-)
            target_veld = None
            sorted_velds = sorted(config['veld_order'], key=len, reverse=True)
            for veld in sorted_velds:
                # Use more precise matching - check if the veld appears as a complete word
                if f" {veld}" in target or target.endswith(veld) or f"({veld})" in target:
                    target_veld = veld
                    break
            
            if target_veld and target_veld in veld_colors:
                # Convert hex to rgba for the target veld
                color_hex = veld_colors[target_veld]
                rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
                rgba = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.6)'
                link_colors_final.append(rgba)
            else:
                link_colors_final.append('rgba(128,128,128,0.4)')  # Default gray
        else:
            link_colors_final.append('rgba(128,128,128,0.4)')  # Default gray
    
    # Create figure
    fig = go.Figure(data=[go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=4,
            thickness=12,
            line=dict(color="black", width=1),
            label=node_labels,
            color=node_colors,
            x=node_x,
            y=node_y
        ),
        link=dict(
            source=link_sources,
            target=link_targets,
            value=link_values,
            color=link_colors_final
        )
    )])
    
    # Determine prefix for title
    main_prefix = config['prefix_patterns'].get('E', 'V')
    
    fig.update_layout(
        title_text=f"Ploegenprogressie {main_prefix}Sc {config['boat_class']}: Veld → Halve Finales → Finales → Eindklassering",
        font_size=10,
        width=900,
        height=600,
        margin=dict(t=60, l=60, r=60, b=60)
    )
    
    return fig

# Test the 4-column version