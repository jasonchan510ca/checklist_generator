import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import B6
from reportlab.lib import colors

# ==============================================================================
# == USER VARIABLES ==
# ==============================================================================

# 1. File Paths
XML_INPUT_FILE = 'checklist_categorized.xml'
PDF_OUTPUT_FILE = 'printable_checklist_categorized.pdf'

# 2. Page Layout Configuration
PAGE_SIZE = B6
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
MARGIN = 0.20 * inch

# 3. Style Configuration (Fonts, Colors, etc.)
CATEGORY_STYLE = {
    "font": "Helvetica-Bold",
    "size": 8,
    "color": colors.darkblue,
    "space_after": 0.05 * inch # Extra space after a category title
}

ITEM_STYLE = {
    "font": "Helvetica",
    "size": 8,
    "color": colors.black,
    "line_height": 0.12 * inch # Vertical space for each item
}

# ==============================================================================
# == SCRIPT LOGIC ==
# ==============================================================================

def parse_xml_data():
    """Parses XML for title, columns, and categorized items with styles from child elements."""
    try:
        tree = ET.parse(XML_INPUT_FILE)
        root = tree.getroot()

        # Read title and number of columns from child elements
        title_elem = root.find('title')
        checklist_title = title_elem.text if title_elem is not None else 'Checklist'
        columns_elem = root.find('columns')
        num_columns = int(columns_elem.text) if columns_elem is not None else 1

        categories = []
        for category in root.findall('category'):
            name = category.get('name')
            bullet_style = category.get('bullet_style', '')
            items = [item.text for item in category.findall('item') if item.text]

            if name and items:
                categories.append({
                    "name": name,
                    "items": items,
                    "style": bullet_style
                })

        print(f"✅ Parsed '{XML_INPUT_FILE}'. Using {num_columns} column(s). Found {len(categories)} categories.")
        return checklist_title, num_columns, categories

    except FileNotFoundError:
        print(f"❌ Error: Input file not found at '{XML_INPUT_FILE}'.")
        return None, None, None
    except (ET.ParseError, ValueError) as e:
        print(f"❌ Error: Could not parse '{XML_INPUT_FILE}'. Check XML format and column value. Details: {e}")
        return None, None, None

def generate_checklist_pdf():
    """Generates a categorized PDF checklist based on attributes from the XML."""
    title, num_columns, categories = parse_xml_data()
    if not categories:
        print("No valid categories found. Aborting PDF generation.")
        return

    # --- Setup PDF Canvas and Title ---
    c = canvas.Canvas(PDF_OUTPUT_FILE, pagesize=PAGE_SIZE)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - MARGIN, title)

    # --- Layout Dimensions from parsed values ---
    printable_width = PAGE_WIDTH - (2 * MARGIN)
    column_width = printable_width / num_columns
    top_y = PAGE_HEIGHT - MARGIN - (0.2 * inch)
    bottom_y = MARGIN
    
    current_x = MARGIN
    current_y = top_y
    col_index = 0

    # --- Draw Categories and Items ---
    for category in categories:
        category_height = CATEGORY_STYLE["size"] * 1.0 + CATEGORY_STYLE["space_after"]
        category_height += len(category["items"]) * ITEM_STYLE["line_height"]
        
        if current_y - category_height < bottom_y and current_y != top_y:
            col_index += 1
            if col_index >= num_columns:
                c.showPage()
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - MARGIN, title)
                col_index = 0
            current_x = MARGIN + (col_index * column_width)
            current_y = top_y
        
        # Draw Category Header
        c.setFont(CATEGORY_STYLE["font"], CATEGORY_STYLE["size"])
        c.setFillColor(CATEGORY_STYLE["color"])
        c.drawString(current_x, current_y, category["name"])
        current_y -= (CATEGORY_STYLE["size"] * 1 + CATEGORY_STYLE["space_after"])
        
        # Draw Items in Category
        c.setFont(ITEM_STYLE["font"], ITEM_STYLE["size"])
        c.setFillColor(ITEM_STYLE["color"])
        bullet_area_width = 0.3 * inch

        for i, item_text in enumerate(category["items"]):
            bullet_style = category["style"]
            bullet_x = current_x
            text_x = current_x + bullet_area_width

            # Draw the bullet based on the style from the XML
            if bullet_style == '':
                text_x = current_x  # No bullet, align text to the left
                c.drawString(current_x, current_y, item_text)
            elif bullet_style == 'dot':
                c.circle(bullet_x + 5, current_y - 2, 2, stroke=1, fill=1)
            elif bullet_style == 'box':
                checkbox_size = ITEM_STYLE["size"] * 0.8
                c.rect(bullet_x, current_y - (checkbox_size * 0.1), checkbox_size, checkbox_size)
            elif bullet_style == 'number':
                c.drawRightString(bullet_x + 15, current_y, f"{i+1}.")
            else: # Handles '-', '*', etc.
                c.drawString(bullet_x, current_y, bullet_style)
            
            # Draw item text
            c.drawString(text_x, current_y, item_text)
            current_y -= ITEM_STYLE["line_height"]

        current_y -= 0.2 * inch

    c.save()
    print(f"🎉 Checklist successfully generated and saved to '{PDF_OUTPUT_FILE}'.")

if __name__ == '__main__':
    generate_checklist_pdf()