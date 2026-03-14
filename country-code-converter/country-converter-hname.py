import os
import io
import re
import pandas as pd

# Country code mapping dictionary (2-letter to 3-letter)
# This is the complete and corrected version based on all your feedback.
COUNTRY_CODE_MAPPING = {
    'AD': 'AND', 'AE': 'ARE', 'AF': 'AFG', 'AG': 'ATG', 'AI': 'AIA', 'AL': 'ALB', 'AM': 'ARM', 'AN': 'ANT',
    'AO': 'AGO', 'AQ': 'ATA', 'AR': 'ARG', 'AS': 'ASM', 'AT': 'AUT', 'AU': 'AUS', 'AW': 'ABW', 'AX': 'ALA',
    'AZ': 'AZE', 'BA': 'BIH', 'BB': 'BRB', 'BD': 'BGD', 'BE': 'BEL', 'BF': 'BFA', 'BG': 'BGR', 'BH': 'BHR',
    'BI': 'BDI', 'BJ': 'BEN', 'BL': 'BLM', 'BM': 'BMU', 'BN': 'BRN', 'BO': 'BOL', 'BQ': 'BES', 'BR': 'BRA',
    'BS': 'BHS', 'BT': 'BTN', 'BV': 'BVT', 'BW': 'BWA', 'BY': 'BLR', 'BZ': 'BLZ', 'CA': 'CAN', 'CC': 'CCK',
    'CD': 'COD', 'CF': 'CAF', 'CG': 'COG', 'CH': 'CHE', 'CI': 'CIV', 'CK': 'COK', 'CL': 'CHL', 'CM': 'CMR',
    'CN': 'CHN', 'CO': 'COL', 'CR': 'CRI', 'CU': 'CUB', 'CV': 'CPV', 'CW': 'CUW', 'CX': 'CXR', 'CY': 'CYP',
    'CZ': 'CZE', 'DE': 'DEU', 'DJ': 'DJI', 'DK': 'DNK', 'DM': 'DMA', 'DO': 'DOM', 'DZ': 'DZA', 'EC': 'ECU',
    'EE': 'EST', 'EG': 'EGY', 'EH': 'ESH', 'ER': 'ERI', 'ES': 'ESP', 'ET': 'ETH', 'FI': 'FIN', 'FJ': 'FJI',
    'FK': 'FLK', 'FM': 'FSM', 'FO': 'FRO', 'FR': 'FRA', 'FX': 'FXX', 'GA': 'GAB', 'GB': 'GBR', 'GD': 'GRD',
    'GE': 'GEO', 'GF': 'GUF', 'GG': 'GGY', 'GH': 'GHA', 'GI': 'GIB', 'GL': 'GRL', 'GM': 'GMB', 'GN': 'GIN',
    'GP': 'GLP', 'GQ': 'GNQ', 'GR': 'GRC', 'GS': 'SGS', 'GT': 'GTM', 'GU': 'GUM', 'GW': 'GNB', 'GY': 'GUY',
    'HK': 'HKG', 'HM': 'HMD', 'HN': 'HND', 'HR': 'HRV', 'HT': 'HTI', 'HU': 'HUN', 'ID': 'IDN', 'IE': 'IRL',
    'IL': 'ISR', 'IM': 'IMN', 'IN': 'IND', 'IO': 'IOT', 'IQ': 'IRQ', 'IR': 'IRN', 'IS': 'ISL', 'IT': 'ITA',
    'JE': 'JEY', 'JM': 'JAM', 'JO': 'JOR', 'JP': 'JPN', 'KE': 'KEN', 'KG': 'KGZ', 'KH': 'KHM', 'KI': 'KIR',
    'KM': 'COM', 'KN': 'KNA', 'KP': 'PRK', 'KR': 'KOR', 'KW': 'KWT', 'KY': 'CYM', 'KZ': 'KAZ', 'LA': 'LAO',
    'LB': 'LBN', 'LC': 'LCA', 'LI': 'LIE', 'LK': 'LKA', 'LR': 'LBR', 'LS': 'LSO', 'LT': 'LTU', 'LU': 'LUX',
    'LV': 'LVA', 'LY': 'LBY', 'MA': 'MAR', 'MC': 'MCO', 'MD': 'MDA', 'ME': 'MNE', 'MF': 'MAF', 'MG': 'MDG',
    'MH': 'MHL', 'MK': 'MKD', 'ML': 'MLI', 'MM': 'MMR', 'MN': 'MNG', 'MO': 'MAC', 'MP': 'MNP', 'MQ': 'MTQ',
    'MR': 'MRT', 'MS': 'MSR', 'MT': 'MLT', 'MU': 'MUS', 'MV': 'MDV', 'MW': 'MWI', 'MX': 'MEX', 'MY': 'MYS',
    'MZ': 'MOZ', 'NA': 'NAM', 'NC': 'NCL', 'NE': 'NER', 'NF': 'NFK', 'NG': 'NGA', 'NI': 'NIC', 'NL': 'NLD',
    'NO': 'NOR', 'NP': 'NPL', 'NR': 'NRU', 'NU': 'NIU', 'NZ': 'NZL', 'OM': 'OMN', 'PA': 'PAN', 'PE': 'PER',
    'PF': 'PYF', 'PG': 'PNG', 'PH': 'PHL', 'PK': 'PAK', 'PL': 'POL', 'PM': 'SPM', 'PN': 'PCN', 'PR': 'PRI',
    'PS': 'PSE', 'PT': 'PRT', 'PW': 'PLW', 'PY': 'PRY', 'QA': 'QAT', 'RE': 'REU', 'RO': 'ROU', 'RS': 'SRB',
    'RU': 'RUS', 'RW': 'RWA', 'SA': 'SAU', 'SB': 'SLB', 'SC': 'SYC', 'SD': 'SDN', 'SE': 'SWE', 'SG': 'SGP',
    'SH': 'SHN', 'SI': 'SVN', 'SJ': 'SJM', 'SK': 'SVK', 'SL': 'SLE', 'SM': 'SMR', 'SN': 'SEN', 'SO': 'SOM',
    'SR': 'SUR', 'SS': 'SSD', 'ST': 'STP', 'SV': 'SLV', 'SX': 'SXM', 'SY': 'SYR', 'SZ': 'SWZ', 'TC': 'TCA',
    'TD': 'TCD', 'TF': 'ATF', 'TG': 'TGO', 'TH': 'THA', 'TJ': 'TJK', 'TK': 'TKL', 'TL': 'TLS', 'TM': 'TKM',
    'TN': 'TUN', 'TO': 'TON', 'TP': 'TLS', 'TR': 'TUR', 'TT': 'TTO', 'TV': 'TUV', 'TW': 'TWN', 'TZ': 'TZA',
    'UA': 'UKR', 'UG': 'UGA', 'UM': 'UMI', 'US': 'USA', 'UY': 'URY', 'UZ': 'UZB', 'VA': 'VAT', 'VC': 'VCT',
    'VE': 'VEN', 'VG': 'VGB', 'VI': 'VIR', 'VN': 'VNM', 'VU': 'VUT', 'WF': 'WLF', 'WS': 'WSM', 'XK': 'XKX',
    'YE': 'YEM', 'YT': 'MYT', 'YU': 'YUG', 'ZA': 'ZAF', 'ZM': 'ZMB', 'ZR': 'COD', 'ZW': 'ZWE'
}

def create_corrected_hname_csvs(input_folder, output_folder):
    """
    Reads all CSVs in a folder, converts embedded country codes in HNAME columns, 
    and saves the corrected files to an output folder.
    """
    print(f"--- Starting HNAME CSV Correction Process ---")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Regex to find 2-letter codes like \US\ or /BR/
    country_code_pattern = re.compile(r'([\\/])([A-Z]{2})([\\/])')

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.csv'):
            input_filepath = os.path.join(input_folder, filename)
            output_filepath = os.path.join(output_folder, filename)
            
            print(f"\n{'='*50}\nProcessing file: {filename}\n{'='*50}")

            try:
                # 1. Read original lines to preserve headers
                with open(input_filepath, 'r') as f:
                    original_lines = f.readlines()
                
                # 2. Use pandas to read the data, with fixes for 'NA' and bad lines
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

                # 3. Define a function to perform the replacement
                def convert_codes_in_string(text_value):
                    if not isinstance(text_value, str):
                        return text_value
                    
                    # This function is called for each code found by the regex
                    def replacer(match):
                        # match.group(1) is the first slash, group(2) is the code, group(3) is the second slash
                        code = match.group(2)
                        if code in COUNTRY_CODE_MAPPING:
                            # Rebuild the string with the converted code
                            return f"{match.group(1)}{COUNTRY_CODE_MAPPING[code]}{match.group(3)}"
                        else:
                            # If code not in our map, return the original match
                            return match.group(0)
                    
                    return country_code_pattern.sub(replacer, text_value)

                # 4. Apply the conversion to the target columns
                cols_to_process = ['HNAME', 'HNAME_SET_GID']
                for col_name in cols_to_process:
                    if col_name in df.columns:
                        print(f"-> Converting codes in column: '{col_name}'...")
                        df[col_name] = df[col_name].apply(convert_codes_in_string)
                print("-> Conversion process complete.")

                # 5. Convert the modified DataFrame back to a CSV string
                modified_data_body = df.to_csv(header=False, index=False, lineterminator='\r\n')
                
                # 6. Assemble the final file content with original headers
                final_content = "".join(original_lines[:3]) + modified_data_body
                
                # 7. Write the corrected file
                with open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
                    outfile.write(final_content)
                    
                print(f"-> Successfully created corrected file at: {output_filepath}")

            except Exception as e:
                print(f"\n--- FAILED to process {filename}: {e} ---")
                import traceback
                traceback.print_exc()

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    input_folder_path = r"C:\Users\tusharjairam.k\OneDrive - Infosys Limited\Desktop\Python CSV\CSV"
    output_folder_path = r"C:\Users\tusharjairam.k\OneDrive - Infosys Limited\Desktop\Python CSV\CSV_Corrected"

    if os.path.exists(input_folder_path):
        create_corrected_hname_csvs(input_folder_path, output_folder_path)
        print("\n--- Process Complete ---")
        print(f"Check the '{output_folder_path}' folder for your corrected files.")
        print("These files are now ready for you to upload via the OTM UI.")
    else:
        print(f"FATAL ERROR: The input folder was not found: {input_folder_path}")
