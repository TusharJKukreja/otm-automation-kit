import os
import csv
import re
from bs4 import BeautifulSoup
from lxml import etree
import io

def create_batched_clean_otm_xml(input_folder, output_folder, batch_size=2000, char_limit=50):
    """
    Reads CSV files, intelligently finds the header, uses a robust CSV parser,
    performs a definitive multi-stage cleaning on all special characters, and
    converts the data into batched, valid OTM XML files.
    """
    
    print(f"--- Starting The Definitive OTM CSV to XML Conversion ---")
    print(f"Reading from: {input_folder}")
    print(f"Saving to:    {output_folder}")
    
    if not os.path.isdir(input_folder):
        print(f"\nFATAL ERROR: Input folder not found at '{input_folder}'")
        return
        
    os.makedirs(output_folder, exist_ok=True)
    
    files_to_process = [f for f in os.listdir(input_folder) if f.lower().endswith('.csv')]
    
    if not files_to_process:
        print(f"\nNo .csv files found in '{input_folder}'.")
        return

    ns = {'otm': 'http://xmlns.oracle.com/apps/otm/transmission/v6.4',
          'gtm': 'http://xmlns.oracle.com/apps/gtm/transmission/v6.4'}
    etree.register_namespace('otm', ns['otm'])
    etree.register_namespace('gtm', ns['gtm'])

    for filename in files_to_process:
        input_filepath = os.path.join(input_folder, filename)
        base_name, _ = os.path.splitext(filename)
        
        print(f"\nProcessing '{filename}'...")
        
        try:
            with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                lines = infile.readlines()
            
            header_row_index = -1
            for i, line in enumerate(lines):
                if 'CORPORATION_GID' in line and 'CORPORATION_XID' in line:
                    header_row_index = i
                    break
            
            if header_row_index == -1:
                print(f"-> ERROR: No valid header row found. Skipping '{filename}'.")
                continue
                
            csv_content = "".join(lines[header_row_index:])
            csv_file_like_object = io.StringIO(csv_content)
            csv_reader = csv.DictReader(csv_file_like_object)
            all_records = list(csv_reader)
            total_records = len(all_records)

            if not total_records:
                print("-> No valid data records found to process.")
                continue

            batch_count = 0
            for i in range(0, total_records, batch_size):
                current_batch = all_records[i : i + batch_size]
                if not current_batch: continue

                batch_count += 1
                transmission = etree.Element('Transmission', nsmap={None: ns['otm']})
                etree.SubElement(transmission, '{' + ns['otm'] + '}TransmissionHeader', nsmap=ns)
                transmission_body = etree.SubElement(transmission, 'TransmissionBody')
                
                for row in current_batch:
                    def clean_and_truncate(text):
                        if not text: return ""
                        
                        # STAGE 1: Aggressive, case-insensitive fix for all ampersand variations, including those with spaces.
                        # This is the most important fix.
                        temp_cleaned = re.sub(r'&\s*amp\s*;', '&', text, flags=re.IGNORECASE)
                        
                        # STAGE 2: Use BeautifulSoup for all other standard HTML entities.
                        soup = BeautifulSoup(temp_cleaned, 'html.parser')
                        final_cleaned = soup.get_text()
                        
                        return final_cleaned.strip()[:char_limit]

                    corp_id = clean_and_truncate(row.get('CORPORATION_XID', ''))
                    if not corp_id: continue

                    domain_name = row.get('DOMAIN_NAME', '<YOUR_DOMAIN>')
                    is_master = row.get('IS_DOMAIN_MASTER', 'N')
                    is_shipping_active = row.get('IS_SHIPPING_AGENTS_ACTIVE', 'Y')
                    allow_collect = row.get('ALLOW_HOUSE_COLLECT', 'Y')

                    glog_element = etree.SubElement(transmission_body, 'GLogXMLElement')
                    corporation = etree.SubElement(glog_element, '{' + ns['otm'] + '}Corporation')
                    corp_gid = etree.SubElement(corporation, '{' + ns['otm'] + '}CorporationGid')
                    gid = etree.SubElement(corp_gid, '{' + ns['otm'] + '}Gid')
                    etree.SubElement(gid, '{' + ns['otm'] + '}DomainName').text = domain_name
                    etree.SubElement(gid, '{' + ns['otm'] + '}Xid').text = corp_id
                    
                    etree.SubElement(corporation, '{' + ns['otm'] + '}TransactionCode').text = 'IU'
                    etree.SubElement(corporation, '{' + ns['otm'] + '}IsDomainMaster').text = is_master
                    etree.SubElement(corporation, '{' + ns['otm'] + '}IsShippingAgentsActive').text = is_shipping_active
                    etree.SubElement(corporation, '{' + ns['otm'] + '}IsAllowHouseCollect').text = allow_collect
                
                output_filename = f"{base_name}_cleaned_batch_{batch_count}.xml"
                output_filepath = os.path.join(output_folder, output_filename)
                
                tree = etree.ElementTree(transmission)
                tree.write(output_filepath, pretty_print=True, xml_declaration=True, encoding='utf-8')
            
            print(f"-> Success! Converted {total_records} records into {batch_count} XML file(s).")

        except Exception as e:
            print(f"\n--- ERROR occurred while processing '{filename}': {e} ---")
            import traceback
            traceback.print_exc()

# ===================================================================
# --- CONFIGURATION SECTION ---
# ===================================================================
if __name__ == "__main__":
    
    input_folder_path = r"<INPUT FILE FOLDER PATH>"
    output_folder_path = r"<OUTPUT FILE FOLDER PATH>"
    
    otm_character_limit = 50
    records_per_xml_file = 500

    create_batched_clean_otm_xml(input_folder_path, output_folder_path, batch_size=records_per_xml_file, char_limit=otm_character_limit)
    
    print(f"\n--- All files have been processed. ---")
    print(f"Check the '{output_folder_path}' folder for your final XML files.")
