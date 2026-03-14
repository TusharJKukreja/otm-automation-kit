"""
Utility: CSV Batch Converter with ISO Country Code Upgrade
Description: Converts 2-letter ISO country codes to 3-letter codes across multiple CSV files.
"""
import os
import io
import pandas as pd

# Country code mapping dictionary (2-letter to 3-letter)
COUNTRY_CODE_MAPPING = {
    'AD': 'AND', 'AE': 'ARE', 'AF': 'AFG', 'AG': 'ATG', 'AI': 'AIA', 'AL': 'ALB',
    'AM': 'ARM', 'AN': 'ANT', 'AO': 'AGO', 'AQ': 'ATA', 'AR': 'ARG', 'AS': 'ASM',
    'AT': 'AUT', 'AU': 'AUS', 'AW': 'ABW', 'AX': 'ALA', 'AZ': 'AZE', 'BA': 'BIH',
    'BB': 'BRB', 'BD': 'BGD', 'BE': 'BEL', 'BF': 'BFA', 'BG': 'BGR', 'BH': 'BHR',
    'BI': 'BDI', 'BJ': 'BEN', 'BL': 'BLM', 'BM': 'BMU', 'BN': 'BRN', 'BO': 'BOL',
    'BQ': 'BES', 'BR': 'BRA', 'BS': 'BHS', 'BT': 'BTN', 'BV': 'BVT', 'BW': 'BWA',
    'BY': 'BLR', 'BZ': 'BLZ', 'CA': 'CAN', 'CC': 'CCK', 'CD': 'COD', 'CF': 'CAF',
    'CG': 'COG', 'CH': 'CHE', 'CI': 'CIV', 'CK': 'COK', 'CL': 'CHL', 'CM': 'CMR',
    'CN': 'CHN', 'CO': 'COL', 'CR': 'CRI', 'CU': 'CUB', 'CV': 'CPV', 'CW': 'CUW',
    'CX': 'CXR', 'CY': 'CYP', 'CZ': 'CZE', 'DE': 'DEU', 'DJ': 'DJI', 'DK': 'DNK',
    'DM': 'DMA', 'DO': 'DOM', 'DZ': 'DZA', 'EC': 'ECU', 'EE': 'EST', 'EG': 'EGY',
    'EH': 'ESH', 'ER': 'ERI', 'ES': 'ESP', 'ET': 'ETH', 'FI': 'FIN', 'FJ': 'FJI',
    'FK': 'FLK', 'FM': 'FSM', 'FO': 'FRO', 'FR': 'FRA', 'FX': 'FXX', 'GA': 'GAB',
    'GB': 'GBR', 'GD': 'GRD', 'GE': 'GEO', 'GF': 'GUF', 'GG': 'GGY', 'GH': 'GHA',
    'GI': 'GIB', 'GL': 'GRL', 'GM': 'GMB', 'GN': 'GIN', 'GP': 'GLP', 'GQ': 'GNQ',
    'GR': 'GRC', 'GS': 'SGS', 'GT': 'GTM', 'GU': 'GUM', 'GW': 'GNB', 'GY': 'GUY',
    'HK': 'HKG', 'HM': 'HMD', 'HN': 'HND', 'HR': 'HRV', 'HT': 'HTI', 'HU': 'HUN',
    'ID': 'IDN', 'IE': 'IRL', 'IL': 'ISR', 'IM': 'IMN', 'IN': 'IND', 'IO': 'IOT',
    'IQ': 'IRQ', 'IR': 'IRN', 'IS': 'ISL', 'IT': 'ITA', 'JE': 'JEY', 'JM': 'JAM',
    'JO': 'JOR', 'JP': 'JPN', 'KE': 'KEN', 'KG': 'KGZ', 'KH': 'KHM', 'KI': 'KIR',
    'KM': 'COM', 'KN': 'KNA', 'KP': 'PRK', 'KR': 'KOR', 'KW': 'KWT', 'KY': 'CYM',
    'KZ': 'KAZ', 'LA': 'LAO', 'LB': 'LBN', 'LC': 'LCA', 'LI': 'LIE', 'LK': 'LKA',
    'LR': 'LBR', 'LS': 'LSO', 'LT': 'LTU', 'LU': 'LUX', 'LV': 'LVA', 'LY': 'LBY',
    'MA': 'MAR', 'MC': 'MCO', 'MD': 'MDA', 'ME': 'MNE', 'MF': 'MAF', 'MG': 'MDG',
    'MH': 'MHL', 'MK': 'MKD', 'ML': 'MLI', 'MM': 'MMR', 'MN': 'MNG', 'MO': 'MAC',
    'MP': 'MNP', 'MQ': 'MTQ', 'MR': 'MRT', 'MS': 'MSR', 'MT': 'MLT', 'MU': 'MUS',
    'MV': 'MDV', 'MW': 'MWI', 'MX': 'MEX', 'MY': 'MYS', 'MZ': 'MOZ', 'NA': 'NAM',
    'NC': 'NCL', 'NE': 'NER', 'NF': 'NFK', 'NG': 'NGA', 'NI': 'NIC', 'NL': 'NLD',
    'NO': 'NOR', 'NP': 'NPL', 'NR': 'NRU', 'NU': 'NIU', 'NZ': 'NZL', 'OM': 'OMN',
    'PA': 'PAN', 'PE': 'PER', 'PF': 'PYF', 'PG': 'PNG', 'PH': 'PHL', 'PK': 'PAK',
    'PL': 'POL', 'PM': 'SPM', 'PN': 'PCN', 'PR': 'PRI', 'PS': 'PSE', 'PT': 'PRT',
    'PW': 'PLW', 'PY': 'PRY', 'QA': 'QAT', 'RE': 'REU', 'RO': 'ROU', 'RS': 'SRB',
    'RU': 'RUS', 'RW': 'RWA', 'SA': 'SAU', 'SB': 'SLB', 'SC': 'SYC', 'SD': 'SDN',
    'SE': 'SWE', 'SG': 'SGP', 'SH': 'SHN', 'SI': 'SVN', 'SJ': 'SJM', 'SK': 'SVK',
    'SL': 'SLE', 'SM': 'SMR', 'SN': 'SEN', 'SO': 'SOM', 'SR': 'SUR', 'SS': 'SSD',
    'ST': 'STP', 'SV': 'SLV', 'SX': 'SXM', 'SY': 'SYR', 'SZ': 'SWZ', 'TC': 'TCA',
    'TD': 'TCD', 'TF': 'ATF', 'TG': 'TGO', 'TH': 'THA', 'TJ': 'TJK', 'TK': 'TKL',
    'TL': 'TLS', 'TM': 'TKM', 'TN': 'TUN', 'TO': 'TON', 'TP': 'TLS', 'TR': 'TUR',
    'TT': 'TTO', 'TV': 'TUV', 'TW': 'TWN', 'TZ': 'TZA', 'UA': 'UKR', 'UG': 'UGA',
    'UM': 'UMI', 'US': 'USA', 'UY': 'URY', 'UZ': 'UZB', 'VA': 'VAT', 'VC': 'VCT',
    'VE': 'VEN', 'VG': 'VGB', 'VI': 'VIR', 'VN': 'VNM', 'VU': 'VUT', 'WF': 'WLF',
    'WS': 'WSM', 'XK': 'XKX', 'YE': 'YEM', 'YT': 'MYT', 'YU': 'YUG', 'ZA': 'ZAF',
    'ZM': 'ZMB', 'ZR': 'COD', 'ZW': 'ZWE'
}

def create_corrected_csvs_in_batches(input_folder, output_folder, batch_size=4000):
    """
    Reads all CSVs in a folder, converts country codes, and saves the corrected
    data in smaller, batched files to an output folder. It is resilient to
    malformed rows in the source data.
    """
    print(f"--- Starting CSV Correction and Batching Process ---")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Batch size: {batch_size} records per file")
    
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.csv'):
            input_filepath = os.path.join(input_folder, filename)
            
            print(f"\n{'='*50}\nProcessing file: {filename}\n{'='*50}")

            try:
                # 1. Read the original file to get the special OTM header lines
                with open(input_filepath, 'r') as f:
                    original_lines = f.readlines()
                
                # --- THIS IS THE KEY FIX FOR THE PARSING ERROR ---
                # We use engine='python' for more flexibility with bad data.
                # on_bad_lines='warn' will report errors but not crash the script.
                df = pd.read_csv(
                    input_filepath, 
                    skiprows=[0, 2], 
                    dtype=str, 
                    keep_default_na=False, 
                    engine='python', 
                    on_bad_lines='warn'
                )
                df.replace('nan', '', inplace=True)
                print(f"-> Read {len(df)} data records successfully.")

                # 3. Dynamically find and convert all country code columns
                conversion_count = 0
                for col_name in df.columns:
                    if col_name.endswith('COUNTRY_CODE3_GID'):
                        print(f"-> Found country code column: '{col_name}'. Converting...")
                        df[col_name] = df[col_name].str.upper().map(COUNTRY_CODE_MAPPING).fillna(df[col_name])
                        conversion_count += 1
                
                if conversion_count > 0:
                    print(f"-> Conversion complete for {conversion_count} column(s).")
                else:
                    print("-> No country code columns found to convert.")

                # 4. Get the pristine OTM header content
                otm_header = "".join(original_lines[:3])

                # 5. Split the DataFrame into batches and save each one
                num_batches = (len(df) // batch_size) + (1 if len(df) % batch_size > 0 else 0)
                if num_batches == 0 and len(df) == 0: num_batches = 0
                elif num_batches == 0: num_batches = 1
                
                print(f"-> Splitting into {num_batches} batch file(s)...")

                for i in range(num_batches):
                    start_row = i * batch_size
                    end_row = start_row + batch_size
                    df_batch = df.iloc[start_row:end_row]

                    base_name, extension = os.path.splitext(filename)
                    output_filename = f"{base_name}_batch_{i+1}{extension}"
                    output_filepath = os.path.join(output_folder, output_filename)

                    data_body = df_batch.to_csv(header=False, index=False, lineterminator='\r\n')
                    final_content = otm_header + data_body
                    
                    with open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
                        outfile.write(final_content)
                    
                    print(f"   -> Successfully created batch file: {output_filename} ({len(df_batch)} records)")

            except Exception as e:
                print(f"\n--- FAILED to process {filename}: {e} ---")
                import traceback
                traceback.print_exc()

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    input_folder_path = r"<INPUT FILE>"
    output_folder_path = r"<OUTPUT FILE>"
    
    records_per_file = 4000 

    if os.path.exists(input_folder_path):
        create_corrected_csvs_in_batches(input_folder_path, output_folder_path, batch_size=records_per_file)
        print("\n--- Process Complete ---")
        print(f"Check the '{output_folder_path}' folder for your corrected, batched files.")
        print("These files are now ready for you to upload via the OTM UI.")
    else:
        print(f"FATAL ERROR: The input folder was not found: {input_folder_path}")
