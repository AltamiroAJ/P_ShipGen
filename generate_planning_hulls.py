#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Planning Hull Database Generator

This script generates databases of planning hulls ranging from 6 to 30 meters
with variable parameters. All hulls have:
- Hard-chine design
- Deadrise angle ranging from 10 to 30 degrees

Four separate databases are created:
1. 5 ships
2. 50 ships
3. 100 ships
4. 150 ships

Output includes:
- CSV files with all parameters needed for OpenPlaning resistance calculations
- 3D STL geometry files for each hull
"""

import numpy as np
import os
import sys
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from HullParameterization import Hull_Parameterization

# Create output directories
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'generated_hulls')
CSV_DIR = os.path.join(OUTPUT_DIR, 'csv_databases')
GEOMETRY_DIR = os.path.join(OUTPUT_DIR, 'stl_geometries')

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(GEOMETRY_DIR, exist_ok=True)


def generate_random_hull_inputs(LOA_min=6.0, LOA_max=30.0, deadrise_min=10.0, deadrise_max=30.0):
    """
    Generate random hull input parameters for a planning hull.
    
    Parameters:
    -----------
    LOA_min : float
        Minimum length overall in meters
    LOA_max : float
        Maximum length overall in meters
    deadrise_min : float
        Minimum deadrise angle in degrees
    deadrise_max : float
        Maximum deadrise angle in degrees
    
    Returns:
    --------
    inputs : numpy array
        Vector of 45 parameters for hull generation
    """
    
    # Generate LOA (Length Overall)
    LOA = np.random.uniform(LOA_min, LOA_max)
    
    # Length ratios (fractions of LOA)
    # Lb: bow taper length (typically 15-25% of LOA for planning hulls)
    Lb_ratio = np.random.uniform(0.15, 0.25)
    # Ls: stern taper length (typically 10-20% of LOA for planning hulls)
    Ls_ratio = np.random.uniform(0.10, 0.20)
    
    # Beam to Length ratio (Bd/LOA) - typically 0.20-0.35 for planning hulls
    # This ensures realistic beam values
    Bd_LOA_ratio = np.random.uniform(0.20, 0.35)
    Bd = Bd_LOA_ratio * LOA
    
    # Depth to Length ratio (Dd/LOA) - typically 0.08-0.15 for planning hulls
    Dd_LOA_ratio = np.random.uniform(0.08, 0.15)
    Dd = Dd_LOA_ratio * LOA
    
    # Stern beam ratio (Bs/Bd) - typically 0.7-0.95 for planning hulls
    Bs_Bd_ratio = np.random.uniform(0.70, 0.95)
    
    # Waterline depth ratio (WL/Dd) - typically 0.6-0.85
    WL_Dd_ratio = np.random.uniform(0.60, 0.85)
    
    # Chine beam (Bc) - typically 0.7-0.95 of half beam at deck
    # Bc should be less than Bd (half beam at deck)
    Bc_Bd_ratio = np.random.uniform(0.70, 0.90)
    Bc = Bc_Bd_ratio * Bd  # Bc as absolute value, not ratio to LOA
    
    # DEADRISE ANGLE (Beta) - KEY PARAMETER: 10 to 30 degrees
    Beta = np.random.uniform(deadrise_min, deadrise_max)
    
    # Chine radius ratio (Rc/Bc) - small for hard chine (0.01-0.05)
    Rc_Bc_ratio = np.random.uniform(0.01, 0.05)
    
    # Keel radius ratio (Rk/Dd) - small for hard chine (0.01-0.03)
    Rk_Dd_ratio = np.random.uniform(0.01, 0.03)
    
    # Bow form parameters (dimensionless shape factors)
    BOW_0 = np.random.uniform(0.8, 1.2)
    BOW_1 = np.random.uniform(0.8, 1.2)
    
    # Baseline keel position (fraction of Dd)
    BK_z_ratio = np.random.uniform(0.0, 0.1)
    
    # Bow curvature
    Kappa_BOW = np.random.uniform(0.5, 1.5)
    
    # Delta bow parameters
    DELTA_BOW_0 = np.random.uniform(0.8, 1.2)
    DELTA_BOW_1 = np.random.uniform(0.8, 1.2)
    
    # Drift angle parameters
    DRIFT_0 = np.random.uniform(0.8, 1.2)
    DRIFT_1 = np.random.uniform(0.8, 1.2)
    DRIFT_2 = np.random.uniform(-5.0, 5.0)
    
    # End point flags (binary)
    bit_EP_S = 1
    bit_EP_T = 1
    
    # Transom slope
    TRANS_0 = np.random.uniform(-0.1, 0.1)
    
    # Stern skeg height (fraction of Dd)
    SK_z_ratio = np.random.uniform(0.0, 0.15)
    
    # Stern curvature
    Kappa_STERN = np.random.uniform(0.5, 1.5)
    
    # Delta stern parameters
    DELTA_STERN_0 = np.random.uniform(0.8, 1.2)
    DELTA_STERN_1 = np.random.uniform(0.8, 1.2)
    
    # Transom deadrise (similar to main deadrise)
    Beta_trans = Beta + np.random.uniform(-5.0, 5.0)
    Beta_trans = np.clip(Beta_trans, 5.0, 35.0)
    
    # Transom chine beam ratio (as fraction of Bc)
    Bc_trans_Bc_ratio = np.random.uniform(0.8, 1.0)
    
    # Transom radii (small for hard chine)
    Rc_trans_Bc_ratio = np.random.uniform(0.01, 0.05)
    Rk_trans_Dd_ratio = np.random.uniform(0.01, 0.03)
    
    # Bulb flags (typically 0 for planning hulls)
    bit_BB = 0
    bit_SB = 0
    
    # Bulb parameters (set to zeros if no bulb)
    Lbb = 0.0
    Hbb = 0.0
    Bbb = 0.0
    Lbbm = 0.0
    Rbb = 0.0
    Kappa_SB = 0.0
    Lsb = 0.0
    HSBOA = 0.0
    Hsb = 0.0
    Bsb = 0.0
    Lsbm = 0.0
    Rsb = 0.0
    
    # Assemble input vector (45 parameters)
    # Note: The Hull_Parameterization class expects certain parameters as ratios and others as absolute values
    # Based on HullParameterization.py lines 71-80:
    #   - inputs[3] (Bd) is divided by 2.0 and multiplied by LOA -> so it should be a ratio to LOA
    #   - inputs[4] (Dd) is multiplied by LOA -> so it should be a ratio to LOA  
    #   - inputs[7] (Bc) is divided by 2.0 and multiplied by LOA -> so it should be a ratio to LOA
    inputs = np.array([
        LOA,              # 0: Length Overall [m]
        Lb_ratio,         # 1: Bow taper ratio (fraction of LOA)
        Ls_ratio,         # 2: Stern taper ratio (fraction of LOA)
        Bd_LOA_ratio,     # 3: Beam at deck ratio (fraction of LOA)
        Dd_LOA_ratio,     # 4: Depth at deck ratio (fraction of LOA)
        Bs_Bd_ratio,      # 5: Stern beam ratio (fraction of Bd)
        WL_Dd_ratio,      # 6: Waterline depth ratio (fraction of Dd)
        Bc_Bd_ratio,      # 7: Chine beam ratio (fraction of Bd)
        Beta,             # 8: Deadrise angle (DEGREES) - KEY PARAMETER
        Rc_Bc_ratio,      # 9: Chine radius ratio (fraction of Bc)
        Rk_Dd_ratio,      # 10: Keel radius ratio (fraction of Dd)
        BOW_0,            # 11: Bow form parameter 0
        BOW_1,            # 12: Bow form parameter 1
        BK_z_ratio,       # 13: Baseline keel z-position (fraction of Dd)
        Kappa_BOW,        # 14: Bow curvature
        DELTA_BOW_0,      # 15: Delta bow parameter 0
        DELTA_BOW_1,      # 16: Delta bow parameter 1
        DRIFT_0,          # 17: Drift parameter 0
        DRIFT_1,          # 18: Drift parameter 1
        DRIFT_2,          # 19: Drift parameter 2
        bit_EP_S,         # 20: End point flag S
        bit_EP_T,         # 21: End point flag T
        TRANS_0,          # 22: Transom slope
        SK_z_ratio,       # 23: Stern skeg height (fraction of Dd)
        Kappa_STERN,      # 24: Stern curvature
        DELTA_STERN_0,    # 25: Delta stern parameter 0
        DELTA_STERN_1,    # 26: Delta stern parameter 1
        Beta_trans,       # 27: Transom deadrise [degrees]
        Bc_trans_Bc_ratio,# 28: Transom chine beam ratio (fraction of Bc)
        Rc_trans_Bc_ratio,   # 29: Transom chine radius ratio
        Rk_trans_Dd_ratio,   # 30: Transom keel radius ratio
        bit_BB,           # 31: Bulb bow flag
        bit_SB,           # 32: Bulb stern flag
        Lbb,              # 33: Bulb bow length
        Hbb,              # 34: Bulb bow height
        Bbb,              # 35: Bulb bow beam
        Lbbm,             # 36: Bulb bow mid length
        Rbb,              # 37: Bulb bow radius
        Kappa_SB,         # 38: Stern bulb curvature
        Lsb,              # 39: Stern bulb length
        HSBOA,            # 40: Stern bulb OA height
        Hsb,              # 41: Stern bulb height
        Bsb,              # 42: Stern bulb beam
        Lsbm,             # 43: Stern bulb mid length
        Rsb               # 44: Stern bulb radius
    ])
    
    return inputs


def calculate_hull_properties(hull):
    """
    Calculate key hull properties for resistance calculations.
    
    Returns a dictionary with all relevant parameters for OpenPlaning.
    """
    properties = {}
    
    # Basic dimensions
    properties['LOA'] = hull.LOA
    properties['LWL'] = hull.LOA - hull.Lb - hull.Ls  # Approximate waterline length
    properties['Beam'] = 2.0 * hull.Bd  # Full beam
    properties['Draft'] = hull.WL
    properties['Depth'] = hull.Dd
    
    # Deadrise angles
    properties['Deadrise'] = hull.Beta
    properties['Deadrise_Transom'] = hull.Beta_trans
    
    # Ratios
    properties['L_B_ratio'] = properties['LOA'] / properties['Beam']
    properties['B_T_ratio'] = properties['Beam'] / properties['Draft']
    properties['L_T_ratio'] = properties['LOA'] / properties['Draft']
    
    # Areas and volumes (if calculable)
    try:
        properties['Waterplane_Area'] = hull.Calc_WaterPlaneArea()
        properties['Wetted_Surface'] = hull.Calc_WettedSurface(hull.WL)
        properties['Displacement_Volume'] = hull.Calc_Volumes()
        
        # Block coefficient
        if properties['Wetted_Surface'] > 0:
            properties['CB'] = hull.Calc_CB(hull.WL)
        else:
            properties['CB'] = 0.0
    except Exception as e:
        properties['Waterplane_Area'] = 0.0
        properties['Wetted_Surface'] = 0.0
        properties['Displacement_Volume'] = 0.0
        properties['CB'] = 0.0
    
    # Longitudinal center of flotation
    try:
        lcf = hull.Calc_LCFs()
        properties['LCF'] = lcf[0] if len(lcf) > 0 else 0.0
    except:
        properties['LCF'] = 0.0
    
    # Prismatic coefficient (approximate)
    if properties['Wetted_Surface'] > 0 and properties['LWL'] > 0:
        properties['CP'] = properties['Displacement_Volume'] / (properties['LWL'] * properties['Waterplane_Area']) if properties['Waterplane_Area'] > 0 else 0.0
    else:
        properties['CP'] = 0.0
    
    return properties


def generate_hull_database(num_ships, database_name, LOA_min=6.0, LOA_max=30.0, 
                          deadrise_min=10.0, deadrise_max=30.0, seed=None):
    """
    Generate a database of hull designs.
    
    Parameters:
    -----------
    num_ships : int
        Number of ships to generate
    database_name : str
        Name of the database file
    LOA_min : float
        Minimum length overall in meters
    LOA_max : float
        Maximum length overall in meters
    deadrise_min : float
        Minimum deadrise angle in degrees
    deadrise_max : float
        Maximum deadrise angle in degrees
    seed : int, optional
        Random seed for reproducibility
    
    Returns:
    --------
    success_count : int
        Number of successfully generated hulls
    """
    
    if seed is not None:
        np.random.seed(seed)
    
    print(f"\n{'='*80}")
    print(f"Generating {database_name} with {num_ships} ships")
    print(f"LOA range: {LOA_min} - {LOA_max} meters")
    print(f"Deadrise range: {deadrise_min} - {deadrise_max} degrees")
    print(f"{'='*80}\n")
    
    # CSV header for OpenPlaning resistance calculations
    csv_header = [
        'Hull_ID', 'LOA', 'LWL', 'Beam', 'Draft', 'Depth',
        'Deadrise_deg', 'Deadrise_Transom_deg',
        'L_B_ratio', 'B_T_ratio', 'L_T_ratio',
        'Waterplane_Area', 'Wetted_Surface', 'Displacement_Volume',
        'CB', 'CP', 'LCF',
        'Lb_ratio', 'Ls_ratio', 'Bs_Bd_ratio', 'WL_Dd_ratio',
        'Bc_LOA_ratio', 'Beta', 'Rc_Bc_ratio', 'Rk_Dd_ratio',
        'Kappa_BOW', 'Kappa_STERN', 'Beta_trans', 'Bc_trans_LOA_ratio',
        'bit_BB', 'bit_SB'
    ]
    
    successful_hulls = []
    failed_count = 0
    
    for i in range(num_ships):
        hull_id = f"{database_name}_H{i+1:04d}"
        
        try:
            # Generate random inputs
            inputs = generate_random_hull_inputs(
                LOA_min=LOA_min, LOA_max=LOA_max,
                deadrise_min=deadrise_min, deadrise_max=deadrise_max
            )
            
            # Create hull
            hull = Hull_Parameterization(inputs)
            
            # Check constraints
            constraints_violated = False
            
            # Verify deadrise is in range
            if not (deadrise_min <= hull.Beta <= deadrise_max):
                constraints_violated = True
            
            # Additional constraint checks can be added here
            
            if not constraints_violated:
                # Calculate properties
                props = calculate_hull_properties(hull)
                
                # Add hull ID and basic ratios to properties
                props['Hull_ID'] = hull_id
                props['Lb_ratio'] = inputs[1]
                props['Ls_ratio'] = inputs[2]
                props['Bs_Bd_ratio'] = inputs[5]
                props['WL_Dd_ratio'] = inputs[6]
                props['Bc_LOA_ratio'] = inputs[7]
                props['Beta'] = inputs[8]
                props['Rc_Bc_ratio'] = inputs[9]
                props['Rk_Dd_ratio'] = inputs[10]
                props['Kappa_BOW'] = inputs[14]
                props['Kappa_STERN'] = inputs[24]
                props['Beta_trans'] = inputs[27]
                props['Bc_trans_LOA_ratio'] = inputs[28]
                props['bit_BB'] = inputs[31]
                props['bit_SB'] = inputs[32]
                
                successful_hulls.append(props)
                
                # Generate STL geometry
                try:
                    stl_filename = os.path.join(GEOMETRY_DIR, f"{hull_id}.stl")
                    hull.gen_stl(
                        NUM_WL=50,
                        PointsPerWL=300,
                        bit_AddTransom=1,
                        bit_AddDeckLid=0,
                        namepath=stl_filename.replace('.stl', '')
                    )
                    print(f"  [{i+1}/{num_ships}] {hull_id}: LOA={props['LOA']:.2f}m, "
                          f"Beam={props['Beam']:.2f}m, Beta={props['Deadrise']:.1f}° - STL saved")
                except Exception as e:
                    print(f"  [{i+1}/{num_ships}] {hull_id}: LOA={props['LOA']:.2f}m, "
                          f"Beam={props['Beam']:.2f}m, Beta={props['Deadrise']:.1f}° - STL failed: {str(e)}")
            else:
                failed_count += 1
                print(f"  [{i+1}/{num_ships}] {hull_id}: Constraints violated, skipping")
                
        except Exception as e:
            failed_count += 1
            print(f"  [{i+1}/{num_ships}] {hull_id}: Generation failed - {str(e)}")
    
    # Write CSV database
    if successful_hulls:
        csv_filepath = os.path.join(CSV_DIR, f"{database_name}.csv")
        
        with open(csv_filepath, 'w') as f:
            # Write header
            f.write(','.join(csv_header) + '\n')
            
            # Write data rows
            for hull_data in successful_hulls:
                row = [
                    hull_data['Hull_ID'],
                    f"{hull_data['LOA']:.6f}",
                    f"{hull_data['LWL']:.6f}",
                    f"{hull_data['Beam']:.6f}",
                    f"{hull_data['Draft']:.6f}",
                    f"{hull_data['Depth']:.6f}",
                    f"{hull_data['Deadrise']:.6f}",
                    f"{hull_data['Deadrise_Transom']:.6f}",
                    f"{hull_data['L_B_ratio']:.6f}",
                    f"{hull_data['B_T_ratio']:.6f}",
                    f"{hull_data['L_T_ratio']:.6f}",
                    f"{hull_data['Waterplane_Area']:.6f}",
                    f"{hull_data['Wetted_Surface']:.6f}",
                    f"{hull_data['Displacement_Volume']:.6f}",
                    f"{hull_data['CB']:.6f}",
                    f"{hull_data['CP']:.6f}",
                    f"{hull_data['LCF']:.6f}",
                    f"{hull_data['Lb_ratio']:.6f}",
                    f"{hull_data['Ls_ratio']:.6f}",
                    f"{hull_data['Bs_Bd_ratio']:.6f}",
                    f"{hull_data['WL_Dd_ratio']:.6f}",
                    f"{hull_data['Bc_LOA_ratio']:.6f}",
                    f"{hull_data['Beta']:.6f}",
                    f"{hull_data['Rc_Bc_ratio']:.6f}",
                    f"{hull_data['Rk_Dd_ratio']:.6f}",
                    f"{hull_data['Kappa_BOW']:.6f}",
                    f"{hull_data['Kappa_STERN']:.6f}",
                    f"{hull_data['Beta_trans']:.6f}",
                    f"{hull_data['Bc_trans_LOA_ratio']:.6f}",
                    str(int(hull_data['bit_BB'])),
                    str(int(hull_data['bit_SB']))
                ]
                f.write(','.join(row) + '\n')
        
        print(f"\n✓ Database saved to: {csv_filepath}")
        print(f"✓ Successfully generated {len(successful_hulls)} hulls")
        if failed_count > 0:
            print(f"✗ Failed to generate {failed_count} hulls")
        
        return len(successful_hulls)
    else:
        print(f"\n✗ No hulls were successfully generated!")
        return 0


def main():
    """Main function to generate all four databases."""
    
    print("="*80)
    print("PLANNING HULL DATABASE GENERATOR")
    print("="*80)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"CSV databases: {CSV_DIR}")
    print(f"STL geometries: {GEOMETRY_DIR}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Define database configurations
    databases = [
        {'name': 'planning_hulls_005', 'count': 5, 'seed': 42},
        {'name': 'planning_hulls_050', 'count': 50, 'seed': 43},
        {'name': 'planning_hulls_100', 'count': 100, 'seed': 44},
        {'name': 'planning_hulls_150', 'count': 150, 'seed': 45}
    ]
    
    results = []
    
    for db_config in databases:
        success_count = generate_hull_database(
            num_ships=db_config['count'],
            database_name=db_config['name'],
            LOA_min=6.0,
            LOA_max=30.0,
            deadrise_min=10.0,
            deadrise_max=30.0,
            seed=db_config['seed']
        )
        results.append({
            'name': db_config['name'],
            'target': db_config['count'],
            'actual': success_count
        })
    
    # Print summary
    print("\n" + "="*80)
    print("GENERATION SUMMARY")
    print("="*80)
    print(f"{'Database':<30} {'Target':>10} {'Generated':>10} {'Success Rate':>15}")
    print("-"*80)
    
    total_target = 0
    total_generated = 0
    
    for result in results:
        success_rate = (result['actual'] / result['target'] * 100) if result['target'] > 0 else 0
        print(f"{result['name']:<30} {result['target']:>10} {result['actual']:>10} {success_rate:>14.1f}%")
        total_target += result['target']
        total_generated += result['actual']
    
    print("-"*80)
    overall_rate = (total_generated / total_target * 100) if total_target > 0 else 0
    print(f"{'TOTAL':<30} {total_target:>10} {total_generated:>10} {overall_rate:>14.1f}%")
    print("="*80)
    
    print(f"\nAll databases and geometries saved to: {OUTPUT_DIR}")
    print("\nCSV files contain parameters for OpenPlaning resistance calculations:")
    print("  - Main dimensions (LOA, LWL, Beam, Draft, Depth)")
    print("  - Deadrise angles (main and transom)")
    print("  - Dimensional ratios (L/B, B/T, L/T)")
    print("  - Hydrostatic properties (Areas, Volumes, Coefficients)")
    print("  - Parameterization parameters for regeneration")
    
    print("\nSTL files contain 3D geometry for visualization and CFD analysis.")
    print("="*80)


if __name__ == "__main__":
    main()
