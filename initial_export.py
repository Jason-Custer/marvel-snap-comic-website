import sqlite3
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as OpenPyXLImage
import os
from config import DATABASE_PATH, EXPORT_DIR
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

# Define the order of columns for the Excel export
COLUMN_ORDER = [
    "variant_image", # Column A (index 0). Formula points to variant_url (Column D/index 3)
    "snap_card_name", # Column B (index 1) - Now pulled from cards table via JOIN
    "variant_image_url", # Column C (index 2) - Now redundant/duplicate of variant_url as per user request
    "variant_url", # Column D (index 3) - This URL is now crucial for variant_image and holds the primary URL.
    "inker", # Column E (index 4)
    "sketcher", # Column F (index 5)
    "colorist", # Column G (index 6)
    "ReleaseDate", # Column H (index 7) 
    "full_description", # Column I (index 8)
    "comic_title", # Column J (index 9) - Populated from DB or extracted from description
    "comic_year", # Column K (index 10) - Populated from DB or extracted from description
    "issue_number", # Column L (index 11) - Populated from DB or extracted from description
    "manual_status", # Column M (index 12) - Mapped from variants.status
    "is_original_commission", # Column N (index 13) - Now in DB schema, will be populated if data exists
    "commission_image_url", # Column O (index 14) - Now in DB schema, will be populated if data exists
    "commission_image", # Column P (index 15). Formula points to commission_image_url (Column O/index 14)
    "identified_date", # Column Q (index 16) - Now in DB schema, will be populated if data exists
    "manual_notes", # Column R (index 17) - Now in DB schema, will be populated if data exists
    "reference_links", # Column S (index 18) - Now in DB schema, will be populated if data exists
    "variant_id", # Column T (index 19)
    "snap_card_vid", # Column U (index 20) - Mapped from variants.vid
    "comic_cover_link", # Column V (index 21) - Mapped from comics.cover_image
    "comic_cover_image", # Column W (index 22). Formula points to comic_cover_link (Column V/index 21)
    "marvel_link", # Column X (index 23) - From comics table
    "marvel_unlimited_link", # Column Y (index 24) - From comics table
    "amazon_link", # Column Z (index 25) - From comics table
    "source_type", # Column AA (index 26) - Now in DB schema, will be populated if data exists
    "source_url_type", # Column AB (index 27) - Now in DB schema, will be populated if data exists
]

def get_all_variant_data_for_export():
    """Retrieves all necessary variant data, including associated card and comic details, for export."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Updated SELECT statement to fetch card name and comic details
        # Uses a subquery to get the "first" comic link's data for each variant_id.
        # COALESCE is used to ensure empty strings instead of None for easier handling in Excel.
        cursor.execute("""
            SELECT
                v.variant_id, v.cid, v.vid, v.variant_url, v.variant_image,
                v.rarity, v.rarity_slug, v.variant_order, v.status,
                v.full_description, v.inker, v.sketcher, v.colorist,
                v.ReleaseDate,
                c.name AS card_name,
                COALESCE(com.marvel_link, '') AS marvel_link,
                COALESCE(com.marvel_unlimited_link, '') AS marvel_unlimited_link,
                COALESCE(com.amazon_link, '') AS amazon_link,
                COALESCE(com.cover_image, '') AS comic_cover_link,
                -- New comic-specific fields (taking from the first comic link if multiple)
                COALESCE(com.is_original_commission, '') AS is_original_commission,
                COALESCE(com.commission_image_url, '') AS commission_image_url,
                COALESCE(com.commission_image_path, '') AS commission_image_path,
                COALESCE(com.identified_date, '') AS identified_date,
                COALESCE(com.manual_notes, '') AS manual_notes,
                COALESCE(com.reference_links, '') AS reference_links,
                COALESCE(com.source_type, '') AS source_type,
                COALESCE(com.source_url_type, '') AS source_url_type
            FROM variants v
            JOIN cards c ON v.cid = c.cid
            LEFT JOIN (
                SELECT
                    variant_id,
                    marvel_link, marvel_unlimited_link, amazon_link, cover_image,
                    is_original_commission, commission_image_url, commission_image_path,
                    identified_date, manual_notes, reference_links, source_type, source_url_type
                FROM comics
                -- Using GROUP BY to get one row per variant_id from comics.
                -- This will implicitly pick one of the comic_link_id rows if multiple exist for a variant.
                GROUP BY variant_id
            ) AS com ON v.variant_id = com.variant_id
            ORDER BY c.name, v.vid -- Order for consistent output
        """)
        rows = cursor.fetchall()

        # Column names in the order they are selected above
        columns = [
            'variant_id', 'cid', 'vid', 'variant_url', 'variant_image',
            'rarity', 'rarity_slug', 'variant_order', 'status',
            'full_description', 'inker', 'sketcher', 'colorist',
            'ReleaseDate',
            'card_name', 'marvel_link', 'marvel_unlimited_link', 'amazon_link', 'comic_cover_link',
            'is_original_commission', 'commission_image_url', 'commission_image_path',
            'identified_date', 'manual_notes', 'reference_links', 'source_type', 'source_url_type'
        ]

        all_variant_data = []
        for row in rows:
            variant_data = dict(zip(columns, row))

            # --- Data Cleaning and Extraction ---
            # Set 'snap_card_name' from 'card_name'
            variant_data['snap_card_name'] = variant_data['card_name']

            # Set 'snap_card_vid' from 'vid'
            variant_data['snap_card_vid'] = variant_data['vid']

            # Populate 'variant_image_url' (duplicate of 'variant_url' as per user request)
            variant_data['variant_image_url'] = variant_data['variant_url']

            # Initialize comic fields to empty strings if not present
            variant_data['comic_title'] = ''
            variant_data['comic_year'] = ''
            variant_data['issue_number'] = ''

            # Extract Comic Title, Year, and Issue Number from full_description
            full_description = variant_data.get('full_description', '')
            if full_description:
                # Regex to find "from [TITLE] #ISSUE (YEAR)" or "from [TITLE] (YEAR)"
                match = re.search(r'from\s+([A-Za-z0-9\s\'"&\-]+?)(?:\s+#(\d+))?\s+\((\d{4})\)', full_description)
                if match:
                    variant_data['comic_title'] = match.group(1).strip()
                    variant_data['issue_number'] = match.group(2).strip() if match.group(2) else ''
                    variant_data['comic_year'] = match.group(3).strip()

            # Map status to 'manual_status'
            status_mapping = {
                'released': 'Released',
                'unreleased': 'Unreleased',
                'datamined': 'Datamined'
            }
            variant_data['manual_status'] = status_mapping.get(variant_data.get('status', '').lower(), 'Unknown')
            # --- End Data Cleaning and Extraction ---

            all_variant_data.append(variant_data)

        logging.info(f"Retrieved {len(all_variant_data)} variant records from the database.")
        return all_variant_data

    except sqlite3.Error as e:
        logging.error(f"Database error in get_all_variant_data_for_export: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred in get_all_variant_data_for_export: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_column_index(column_name):
    """Returns the 0-based index of a column in COLUMN_ORDER."""
    try:
        return COLUMN_ORDER.index(column_name)
    except ValueError:
        logging.warning(f"Column '{column_name}' not found in COLUMN_ORDER. This might cause issues.")
        return -1 # Or raise an error, depending on desired strictness

def create_spreadsheet(data):
    """
    Creates an Excel spreadsheet from the provided data, applying formatting and image formulas.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Marvel Snap Variants"

    # Write headers
    headers = [col.replace('_', ' ').title() for col in COLUMN_ORDER]
    ws.append(headers)

    # Set column widths
    ws.column_dimensions[get_column_letter(get_column_index("variant_image") + 1)].width = 20 # Column A
    ws.column_dimensions[get_column_letter(get_column_index("snap_card_name") + 1)].width = 20 # Column B
    ws.column_dimensions[get_column_letter(get_column_index("inker") + 1)].width = 15 # Column E
    ws.column_dimensions[get_column_letter(get_column_index("sketcher") + 1)].width = 15 # Column F
    ws.column_dimensions[get_column_letter(get_column_index("colorist") + 1)].width = 15 # Column G
    ws.column_dimensions[get_column_letter(get_column_index("ReleaseDate") + 1)].width = 12 # Column H
    ws.column_dimensions[get_column_letter(get_column_index("full_description") + 1)].width = 40 # Column I
    ws.column_dimensions[get_column_letter(get_column_index("comic_title") + 1)].width = 25 # Column J
    ws.column_dimensions[get_column_letter(get_column_index("comic_year") + 1)].width = 10 # Column K
    ws.column_dimensions[get_column_letter(get_column_index("issue_number") + 1)].width = 15 # Column L
    ws.column_dimensions[get_column_letter(get_column_index("manual_status") + 1)].width = 15 # Column M
    ws.column_dimensions[get_column_letter(get_column_index("is_original_commission") + 1)].width = 15 # Column N
    ws.column_dimensions[get_column_letter(get_column_index("commission_image") + 1)].width = 20 # Column P
    ws.column_dimensions[get_column_letter(get_column_index("identified_date") + 1)].width = 15 # Column Q
    ws.column_dimensions[get_column_letter(get_column_index("manual_notes") + 1)].width = 40 # Column R
    ws.column_dimensions[get_column_letter(get_column_index("reference_links") + 1)].width = 40 # Column S
    ws.column_dimensions[get_column_letter(get_column_index("comic_cover_image") + 1)].width = 20 # Column W
    ws.column_dimensions[get_column_letter(get_column_index("marvel_link") + 1)].width = 30 # Column X
    ws.column_dimensions[get_column_letter(get_column_index("marvel_unlimited_link") + 1)].width = 30 # Column Y
    ws.column_dimensions[get_column_letter(get_column_index("amazon_link") + 1)].width = 30 # Column Z
    ws.column_dimensions[get_column_letter(get_column_index("source_type") + 1)].width = 20 # Column AA
    ws.column_dimensions[get_column_letter(get_column_index("source_url_type") + 1)].width = 20 # Column AB


    # Add data rows
    for row_idx, item in enumerate(data, start=2): # Start from row 2 for data
        row_data = []
        for col_name in COLUMN_ORDER:
            if col_name == "variant_image":
                # Formula for displaying image from URL in Column D
                # Assumes the "variant_url" column is at index 3 (D)
                variant_url_col = get_column_letter(get_column_index("variant_url") + 1)
                row_data.append(f'=IF({variant_url_col}{row_idx}<>"",IMAGE({variant_url_col}{row_idx}),"")')
            elif col_name == "commission_image":
                # Formula for displaying commission image from URL in Column O
                # Assumes the "commission_image_url" column is at index 14 (O)
                commission_image_url_col = get_column_letter(get_column_index("commission_image_url") + 1)
                row_data.append(f'=IF({commission_image_url_col}{row_idx}<>"",IMAGE({commission_image_url_col}{row_idx}),"")')
            elif col_name == "comic_cover_image":
                # Formula for displaying comic cover image from URL in Column V
                # Assumes the "comic_cover_link" column is at index 21 (V)
                comic_cover_link_col = get_column_letter(get_column_index("comic_cover_link") + 1)
                row_data.append(f'=IF({comic_cover_link_col}{row_idx}<>"",IMAGE({comic_cover_link_col}{row_idx}),"")')
            else:
                row_data.append(item.get(col_name, '')) # Use .get() for safety

        ws.append(row_data)
        ws.row_dimensions[row_idx].height = 100 # Adjust row height for images

    output_file = os.path.join(EXPORT_DIR, "marvel_snap_variants_export.xlsx")
    wb.save(output_file)
    logging.info(f"Spreadsheet created successfully at: {output_file}")

def main():
    logging.info("Starting initial export process...")
    variant_data = get_all_variant_data_for_export()
    if variant_data:
        create_spreadsheet(variant_data)
    else:
        logging.warning("No variant data found to export.")
    logging.info("Export process completed.")

if __name__ == "__main__":
    main()