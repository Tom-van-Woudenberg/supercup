"""
Sankey diagram creation functions for rowing competition visualization.
Creates interactive flow diagrams showing crew progression through stages.
"""

import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict


# Create 4-column cumulative positioning function (veld → halve finale groups → individual finales → final positions)
def create_four_column_cumulative_sankey(all_race_data):
    """
    4-Column Sankey: Veld Categories → Detailed Halve Finale Nodes → Individual Finales → Final Positions
    Shows complete flow including final placements with field-specific position tracking
    """
    import plotly.graph_objects as go
    from collections import defaultdict
    
    print("Creating 4-column cumulative Sankey (veld → halve finale groups → individual finales → final positions)...")
    
    # Step 1: Collect flows and counts for all four columns
    flows = []
    node_counts = defaultdict(int)
    
    # Process halve finales data for column 1 → column 2 (unlabeled halve finale nodes)
    if 'halve finales' in all_race_data:
        print("Processing halve finales data (veld → unlabeled halve finale nodes):")
        for race_name, crew_entries in all_race_data['halve finales'].items():
            print(f"  Processing: {race_name} ({len(crew_entries)} crews)")
            for entry in crew_entries:
                veld = entry.get('veld', 'Unknown')
                if veld and veld != 'Unknown':
                    source = f"Veld {veld}"
                    # Create unlabeled halve finale nodes
                    if 'ABC' in race_name:
                        target = f"ABC_{veld}"  # Internal identifier, will be empty in labels
                    elif 'DEFG' in race_name:
                        target = f"DEFG_{veld}"  # Internal identifier, will be empty in labels
                    else:
                        target = f"Other_{race_name}_{veld}"  # Fallback
                    
                    flows.append((source, target, 1))
                    node_counts[source] += 1
                    node_counts[target] += 1
    
    # Process finales data for column 2 → column 3 (detailed halve finale nodes → individual finales)
    if 'finales' in all_race_data:
        print("\nProcessing finales data (detailed halve finale nodes → individual finales):")
        for race_name, crew_entries in all_race_data['finales'].items():
            print(f"  Processing: {race_name} ({len(crew_entries)} crews)")
            
            # Extract finale letter (A, B, C, D, E, F)
            if 'A-finale' in race_name:
                target = "Finale A"
                finale_group = "ABC"
            elif 'B-finale' in race_name:
                target = "Finale B"
                finale_group = "ABC"
            elif 'C-finale' in race_name:
                target = "Finale C"
                finale_group = "ABC"
            elif 'D-finale' in race_name:
                target = "Finale D"
                finale_group = "DEFG"
            elif 'E-finale' in race_name:
                target = "Finale E"
                finale_group = "DEFG"
            elif 'F-finale' in race_name:
                target = "Finale F"
                finale_group = "DEFG"
            else:
                continue  # Skip if we can't determine the finale
            
            # Create flows from each veld's detailed halve finale node to this finale
            # Group crews by veld to create proper flows
            veld_counts = defaultdict(int)
            for entry in crew_entries:
                veld = entry.get('veld', 'Unknown')
                if veld and veld != 'Unknown':
                    veld_counts[veld] += 1
            
            # Create flows from detailed halve finale nodes
            for veld, count in veld_counts.items():
                source = f"ABC_{veld}" if finale_group == "ABC" else f"DEFG_{veld}"
                flows.append((source, target, count))
                node_counts[source] += count
                node_counts[target] += count
    
    # Process finales data for column 3 → column 4 (individual finales → final positions with field tracking)
    if 'finales' in all_race_data:
        print("\nProcessing finales positions (individual finales → final positions with field tracking):")
        for race_name, crew_entries in all_race_data['finales'].items():
            print(f"  Processing positions for: {race_name} ({len(crew_entries)} crews)")
            
            # Extract finale letter (A, B, C, D, E, F)
            if 'A-finale' in race_name:
                source = "Finale A"
                position_offset = 0  # A-finale positions 1-6
            elif 'B-finale' in race_name:
                source = "Finale B"
                position_offset = 6  # B-finale positions 7-12
            elif 'C-finale' in race_name:
                source = "Finale C"
                position_offset = 12  # C-finale positions 13-18
            elif 'D-finale' in race_name:
                source = "Finale D"
                position_offset = 18  # D-finale positions 19-24
            elif 'E-finale' in race_name:
                source = "Finale E"
                position_offset = 24  # E-finale positions 25-30
            elif 'F-finale' in race_name:
                source = "Finale F"
                position_offset = 30  # F-finale positions 31-36
            else:
                continue  # Skip if we can't determine the finale
            
            # Sort crew entries by position within this finale
            # Handle both string and integer position values
            def get_position(entry):
                pos = entry.get('pos', '')
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
                    target = f"Position {final_position} ({veld})"
                    flows.append((source, target, 1))
                    node_counts[source] += 1
                    node_counts[target] += 1
    
    print(f"\nFound {len([n for n in node_counts if n.startswith('Veld')])} veld categories")
    print(f"Found {len([n for n in node_counts if n.startswith('Halve')])} detailed halve finale nodes")
    print(f"Found {len([n for n in node_counts if n.startswith('Finale')])} individual finales")
    print(f"Found {len([n for n in node_counts if n.startswith('Position')])} final positions")
    
    # Step 2: Create ordered node lists for all four columns
    # Column 1: Veld categories (ordered)
    veld_order = ['VE 2x', 'VG 2x', 'VG-B 2x', 'VB 2x', 'LVE 2x', 'LVG 2x', 'LVG-B 2x', 'LVB 2x']
    col1_nodes = [f"Veld {v}" for v in veld_order if f"Veld {v}" in node_counts]
    
    # Column 2: Detailed halve finale nodes (grouped by ABC/DEFG, then by veld)
    col2_nodes = []
    abc_nodes = []
    defg_nodes = []
    
    # Separate ABC and DEFG nodes
    for node in node_counts.keys():
        if node.startswith('ABC_'):
            abc_nodes.append(node)
        elif node.startswith('DEFG_'):
            defg_nodes.append(node)
    
    # Sort within each group by veld category using our desired order
    def sort_by_veld(node_list):
        """Sort nodes by veld category according to our desired order"""
        def get_veld_priority(node):
            for i, veld in enumerate(veld_order):
                if veld in node:
                    return i
            return 999  # Unknown veld goes to end
        return sorted(node_list, key=get_veld_priority)
    
    abc_nodes = sort_by_veld(abc_nodes)
    defg_nodes = sort_by_veld(defg_nodes)
    
    # Combine: ABC nodes first, then DEFG nodes
    col2_nodes = abc_nodes + defg_nodes
    
    # Column 3: Individual finales (A, B, C, D, E, F order)
    finale_order = ['Finale A', 'Finale B', 'Finale C', 'Finale D', 'Finale E', 'Finale F']
    col3_nodes = [f for f in finale_order if f in node_counts]
    
    # Column 4: Final positions (sorted by position number)
    col4_nodes = []
    position_nodes = [n for n in node_counts.keys() if n.startswith('Position')]
    # Sort by position number
    def get_position_number(node):
        try:
            return int(node.split('Position ')[1].split(' ')[0])
        except:
            return 999
    col4_nodes = sorted(position_nodes, key=get_position_number)
    
    print(f"\nColumn 1 (Veld): {len(col1_nodes)} nodes")
    print(f"Column 2 (Detailed Halve Nodes): {len(col2_nodes)} nodes")
    print(f"Column 3 (Individual Finales): {len(col3_nodes)} nodes")
    print(f"Column 4 (Final Positions): {len(col4_nodes)} nodes")
    
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
    print("\nColumn 1 (Veld categories):")
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
        if node.startswith('ABC_') or node.startswith('DEFG_'):
            node_labels.append("")  # No label for halve finale nodes
        else:
            node_labels.append(node)  # Regular label for other nodes
    
    # Enhanced color scheme
    node_colors = []
    
    for node in all_nodes:
        if node.startswith('Veld'):
            # Color veld category nodes with their distinct colors
            if 'VE 2x' in node:
                node_colors.append('#E74C3C')  # Bright red for VE 2x
            elif 'VG 2x' in node and 'VG-B' not in node and 'LVG' not in node:
                node_colors.append('#3498DB')  # Bright blue for VG 2x
            elif 'VG-B 2x' in node:
                node_colors.append('#9B59B6')  # Purple for VG-B 2x
            elif 'VB 2x' in node:
                node_colors.append('#F39C12')  # Orange for VB 2x
            elif 'LVG 2x' in node and 'LVG-B' not in node:
                node_colors.append('#1ABC9C')  # Teal for LVG 2x
            elif 'LVG-B 2x' in node:
                node_colors.append('#9B59B6')  # Purple for LVG-B 2x
            elif 'LVB 2x' in node:
                node_colors.append('#2ECC71')  # Green for LVB 2x
            elif 'LVE 2x' in node:
                node_colors.append('#C0392B')  # Dark red for LVE 2x
            else:
                node_colors.append('#95A5A6')  # Gray for unknown veld
        elif node.startswith('ABC_') or node.startswith('DEFG_'):
            # Color halve finale nodes based on their field category (same colors as veld categories)
            if 'VE 2x' in node:
                node_colors.append('#E74C3C')  # Bright red for VE 2x (same as veld)
            elif 'VG 2x' in node and 'VG-B' not in node and 'LVG' not in node:
                node_colors.append('#3498DB')  # Bright blue for VG 2x (same as veld)
            elif 'VG-B 2x' in node:
                node_colors.append('#9B59B6')  # Purple for VG-B 2x (same as veld)
            elif 'VB 2x' in node:
                node_colors.append('#F39C12')  # Orange for VB 2x (same as veld)
            elif 'LVG 2x' in node and 'LVG-B' not in node:
                node_colors.append('#1ABC9C')  # Teal for LVG 2x (same as veld)
            elif 'LVG-B 2x' in node:
                node_colors.append('#9B59B6')  # Purple for LVG-B 2x (same as veld)
            elif 'LVB 2x' in node:
                node_colors.append('#2ECC71')  # Green for LVB 2x (same as veld)
            elif 'LVE 2x' in node:
                node_colors.append('#C0392B')  # Dark red for LVE 2x (same as veld)
            else:
                node_colors.append('#95A5A6')  # Gray for unknown halve finale nodes
        elif node in ['Finale A', 'Finale B', 'Finale C', 'Finale D', 'Finale E', 'Finale F']:
            node_colors.append('#95A5A6')  # Gray for finale nodes (mixed inflows/outflows)
        elif node.startswith('Position'):
            # Color position nodes with the same colors as their corresponding veld categories
            if 'VE 2x' in node:
                node_colors.append('#E74C3C')  # Bright red for VE 2x positions (same as veld)
            elif 'VG 2x' in node and 'VG-B' not in node and 'LVG' not in node:
                node_colors.append('#3498DB')  # Bright blue for VG 2x positions (same as veld)
            elif 'VG-B 2x' in node:
                node_colors.append('#9B59B6')  # Purple for VG-B 2x positions (same as veld)
            elif 'VB 2x' in node:
                node_colors.append('#F39C12')  # Orange for VB 2x positions (same as veld)
            elif 'LVG 2x' in node and 'LVG-B' not in node:
                node_colors.append('#1ABC9C')  # Teal for LVG 2x positions (same as veld)
            elif 'LVG-B 2x' in node:
                node_colors.append('#9B59B6')  # Purple for LVG-B 2x positions (same as veld)
            elif 'LVB 2x' in node:
                node_colors.append('#2ECC71')  # Green for LVB 2x positions (same as veld)
            elif 'LVE 2x' in node:
                node_colors.append('#C0392B')  # Dark red for LVE 2x positions (same as veld)
            else:
                node_colors.append('#95A5A6')  # Gray for unknown positions
        else:
            node_colors.append('#95A5A6')  # Gray for others
    
    # Create color mapping for links - use same veld colors throughout entire flow
    veld_link_colors = {
        'Veld VE 2x': 'rgba(231, 76, 60, 0.6)',
        'Veld VG 2x': 'rgba(52, 152, 219, 0.6)',
        'Veld VG-B 2x': 'rgba(155, 89, 182, 0.6)',
        'Veld VB 2x': 'rgba(243, 156, 18, 0.6)',
        'Veld LVG 2x': 'rgba(26, 188, 156, 0.6)',
        'Veld LVG-B 2x': 'rgba(155, 89, 182, 0.6)',
        'Veld LVB 2x': 'rgba(46, 204, 113, 0.6)',
        'Veld LVE 2x': 'rgba(192, 57, 43, 0.6)',
    }
    
    # Use the same veld colors for halve finale nodes 
    halve_finale_colors = {}
    
    # Add colors for all possible veld combinations in halve finale nodes
    for veld in ['VE 2x', 'VG 2x', 'VG-B 2x', 'VB 2x', 'LVE 2x', 'LVG 2x', 'LVG-B 2x', 'LVB 2x']:
        veld_color = veld_link_colors.get(f'Veld {veld}', 'rgba(128,128,128,0.4)')
        
        # Halve finale colors (new naming scheme)
        halve_finale_colors[f'ABC_{veld}'] = veld_color
        halve_finale_colors[f'DEFG_{veld}'] = veld_color
    
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
        elif source.startswith('Finale') and target.startswith('Position'):
            # For finale-to-position flows, use the field color from the target position
            # Use more specific matching to avoid LVG 2x being matched by VG 2x pattern
            if 'VE 2x' in target:
                link_colors_final.append('rgba(231, 76, 60, 0.6)')  # VE 2x red
            elif 'LVG 2x' in target and 'LVG-B' not in target:
                link_colors_final.append('rgba(26, 188, 156, 0.6)')  # LVG 2x teal
            elif 'LVB 2x' in target:
                link_colors_final.append('rgba(46, 204, 113, 0.6)')  # LVB 2x green
            elif 'LVE 2x' in target:
                link_colors_final.append('rgba(192, 57, 43, 0.6)')  # LVE 2x dark red
            elif 'VG 2x' in target and 'VG-B' not in target and 'LVG' not in target:
                link_colors_final.append('rgba(52, 152, 219, 0.6)')  # VG 2x blue
            elif 'VG-B 2x' in target and 'LVG-B' not in target:
                link_colors_final.append('rgba(155, 89, 182, 0.6)')  # VG-B 2x purple
            elif 'LVG-B 2x' in target:
                link_colors_final.append('rgba(155, 89, 182, 0.6)')  # LVG-B 2x purple
            elif 'VB 2x' in target and 'LVB' not in target:
                link_colors_final.append('rgba(243, 156, 18, 0.6)')  # VB 2x orange
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
    
    fig.update_layout(
        title_text="Complete Flow: Veld Categories → Halve Finale Nodes → Individual Finales → Final Positions",
        font_size=10,
        width=1600,
        height=900,
        margin=dict(t=60, l=60, r=60, b=60)
    )
    
    return fig

# Test the 4-column version