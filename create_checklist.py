import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# ==============================================================================
# == USER VARIABLES ==
# ==============================================================================

# 1. File Paths
XML_INPUT_FILE = 'checklist_categorized.xml'
PDF_OUTPUT_FILE = 'printable_checklist_categorized.pdf'

# 2. Page Layout Configuration
#PAGE_SIZE = (612.0, 400.0)
PAGE_SIZE = (350.0, 500.0)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
NUM_COLUMNS = 4
MARGIN = 0.20 * inch

# 3. Style Configuration
# You can use standard font names like "Helvetica", "Times-Roman", etc.
# Add "-Bold", "-Italic", or "-BoldItalic" for variations.
# Colors can be imported from `reportlab.lib.colors`.

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
    """Parses the categorized XML and returns a list of categories."""
    try:
        tree = ET.parse(XML_INPUT_FILE)
        root = tree.getroot()
        checklist_title = root.get('title', 'Checklist')
        
        categories = []
        for category in root.findall('category'):
            name = category.get('name')
            items = [item.text for item in category.findall('item') if item.text]
            if name and items:
                categories.append({"name": name, "items": items})
        
        print(f"✅ Parsed '{XML_INPUT_FILE}'. Title: '{checklist_title}'. Found {len(categories)} categories.")
        return checklist_title, categories
        
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at '{XML_INPUT_FILE}'.")
        return None, None
    except ET.ParseError:
        print(f"❌ Error: Could not parse '{XML_INPUT_FILE}'. Check XML format.")
        return None, None

def generate_checklist_pdf():
    """Generates a categorized PDF checklist based on user variables."""
    title, categories = parse_xml_data()
    if not categories:
        print("No categories with items found. Aborting PDF generation.")
        return

    # --- Setup PDF Canvas and Title ---
    c = canvas.Canvas(PDF_OUTPUT_FILE, pagesize=PAGE_SIZE)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - MARGIN, title)

    # --- Calculate Layout Dimensions ---
    printable_width = PAGE_WIDTH - (2 * MARGIN)
    column_width = printable_width / NUM_COLUMNS
    top_y = PAGE_HEIGHT - MARGIN - (0.2 * inch)
    bottom_y = MARGIN
    
    current_x = MARGIN
    current_y = top_y
    col_index = 0

    # --- Draw Categories and Items ---
    for category in categories:
        # Calculate the total height this category block will occupy
        category_height = CATEGORY_STYLE["size"] * 1 # Approx height of title
        category_height += CATEGORY_STYLE["space_after"]
        category_height += len(category["items"]) * ITEM_STYLE["line_height"]
        
        # If block doesn't fit in current column, move to the next
        if current_y - category_height < bottom_y:
            col_index += 1
            # If we run out of columns, create a new page
            if col_index >= NUM_COLUMNS:
                c.showPage()
                c.setFont("Helvetica-Bold", 18) # Re-draw title on new page
                c.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - MARGIN, title)
                col_index = 0

            current_x = MARGIN + (col_index * column_width)
            current_y = top_y
        
        # --- Draw the Category Header ---
        c.setFont(CATEGORY_STYLE["font"], CATEGORY_STYLE["size"])
        c.setFillColor(CATEGORY_STYLE["color"])
        c.drawString(current_x, current_y, category["name"])
        current_y -= (CATEGORY_STYLE["size"] * 1.2 + CATEGORY_STYLE["space_after"])
        
        # --- Draw the Items in the Category ---
        c.setFont(ITEM_STYLE["font"], ITEM_STYLE["size"])
        c.setFillColor(ITEM_STYLE["color"])
        checkbox_size = ITEM_STYLE["size"] * 0.8
        
        for item_text in category["items"]:
            # Draw checkbox
            # c.rect(current_x, current_y - (checkbox_size * 0.2), checkbox_size, checkbox_size)
            # Draw item text
            # c.drawString(current_x + (checkbox_size * 1.8), current_y, item_text)
            # Draw item text without checkbox
            c.drawString(current_x, current_y, item_text)
            current_y -= ITEM_STYLE["line_height"]

        # Add a little padding after the entire category block
        current_y -= 0.2 * inch

    # --- Save the PDF file ---
    c.save()
    print(f"🎉 Checklist successfully generated and saved to '{PDF_OUTPUT_FILE}'.")

if __name__ == '__main__':
    generate_checklist_pdf()