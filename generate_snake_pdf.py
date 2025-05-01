# -----------------------------------------------------------------------------
# generate_snake_pdf.py
#
# Author: RAJOJU SAI CHARAN
#
# Description:
# Generates a playable Snake game embedded within a PDF document.
# This script defines the PDF structure, including AcroForm button fields
# for the game grid and UI elements (Start button, Keystroke catcher).
# It reads JavaScript game logic from 'snake_game.js', injects configuration
# constants, and embeds it into the PDF.
#
# The game utilizes the '.hidden' property of button fields for visual rendering,
# ensuring better compatibility across different PDF viewers (like browser-based ones).
# A static grid background is drawn directly onto the page content for visual structure.
# Input is handled via a hidden text field capturing WASD keys.
#
# Usage:
# 1. Ensure 'snake_game.js' is in the same directory.
# 2. Run from terminal: python generate_snake_pdf.py
# 3. Output: snake.pdf
# -----------------------------------------------------------------------------

import math
import os # To check if JS file exists

# --- Configuration Constants ---
# Game Grid Setup
GRID_WIDTH = 20      # Number of cells horizontally
GRID_HEIGHT = 20     # Number of cells vertically
CELL_SIZE = 15       # Visual size of each cell in PDF points (1 inch = 72 points)

# Game Behavior
INITIAL_GAME_SPEED_MS = 300 # Milliseconds per game tick (higher value = slower game)
INITIAL_SNAKE_LENGTH = 3    # Starting length of the snake

# --- Calculated Layout Constants ---
GRID_PIXEL_WIDTH = GRID_WIDTH * CELL_SIZE
GRID_PIXEL_HEIGHT = GRID_HEIGHT * CELL_SIZE
PAGE_WIDTH = 612    # Standard US Letter width in points
PAGE_HEIGHT = 792   # Standard US Letter height in points
PAGE_CENTER_X = PAGE_WIDTH / 2
PAGE_CENTER_Y = PAGE_HEIGHT / 2
# Position grid higher up on the page
GRID_OFF_X = math.floor(PAGE_CENTER_X - GRID_PIXEL_WIDTH / 2)
GRID_OFF_Y = 480 # Y offset of the grid's bottom edge from the page bottom

# --- PDF Structure Templates ---
# These are multi-line strings defining the raw PDF object structure.
# Placeholders like ###PLACEHOLDER### will be replaced by the script.

PDF_FILE_TEMPLATE = """%PDF-1.6
% PDF Snake Game Generator

% Catalog Object (Root of the document)
1 0 obj
<<
  /Type /Catalog
  /Pages 2 0 R                  % Reference to Page Tree
  /OpenAction 17 0 R            % Execute JS action object 17 when opened (to load script context)
  /AcroForm <<                  % Interactive Form Dictionary
    /Fields [ ###FIELD_LIST### ] % List of all interactive fields (buttons, text field)
    /NeedAppearances true        % Hint for viewers to generate appearances if needed
    /DR <<                       % Default Resources for forms
      /Encoding << /PDFDocEncoding 8 0 R >>
      /Font << /ZaDb 9 0 R /HeBo 10 0 R >> % Default fonts (ZapfDingbats, Helvetica-Bold)
    >>
    /DA (/HeBo 0 Tf 0 g)        % Default Appearance string for fields
    /SigFlags 3                 % Enable JavaScript actions
  >>
>>
endobj

% Page Tree Object
2 0 obj << /Type /Pages /Count 1 /Kids [ 16 0 R ] >> endobj

% Page Object (The single page in this document)
16 0 obj
<<
  /Type /Page
  /Parent 2 0 R
  /MediaBox [ 0 0 612 792 ]      % Page dimensions (US Letter)
  /Contents 3 0 R               % Reference to Page Content Stream (draws static grid)
  /Resources <<                  % Resources needed by this page & form appearances
    /ProcSet [ /PDF /Text ]
    /Font << /HeBo 10 0 R >>     % Font for the Start Button appearance
  >>
  /Annots [ ###FIELD_LIST### ]    % List of annotations (our form fields) on this page
>>
endobj

% Page Content Stream (Object 3) - Draws the static background grid
3 0 obj << /Length ###PAGE_CONTENT_LEN### >>
stream
###PAGE_CONTENT###
endstream
endobj

% Standard PDF Objects (Encoding, Fonts)
8 0 obj << /Type /Encoding /BaseEncoding /PDFDocEncoding >> endobj
9 0 obj << /Type /Font /Subtype /Type1 /Name /ZaDb /BaseFont /ZapfDingbats >> endobj
10 0 obj << /Type /Font /Subtype /Type1 /Name /HeBo /BaseFont /Helvetica-Bold >> endobj

% JavaScript Context Object (triggered by OpenAction to ensure JS is loaded)
17 0 obj << /S /JavaScript /JS 18 0 R >> endobj % Points to the JS Stream Object

% --- Embedded Objects Start Here ---
###JS_STREAM_PLACEHOLDER###   # Main JavaScript code stream
###UI_ELEMENT_OBJS###        # Start Button & Keystroke Field objects
###FIELDS###                 # Grid cell button objects

% --- Trailer ---
trailer << /Root 1 0 R /Size ###OBJECT_COUNT### >> %%EOF
"""

# Template for a single Grid Cell (Button) - Represents one pixel/cell of the game area
CELL_OBJ_TEMPLATE = """
###IDX### 0 obj
<<
  /FT /Btn                        % Field Type: Button
  /T (P_###X###_###Y###)          % Unique Field Name (e.g., P_10_15) used by JS
  /Rect [ ###RECT### ]            % Position [Left Bottom Right Top]
  /P 16 0 R                       % Parent page reference
  /Subtype /Widget                % Annotation is an interactive widget
  /MK <<                          % Appearance Characteristics (for visible state)
    /BG [ 0.75 0.75 0.75 ]        % Background Color: Gray
    /BC [ 0.5 0.5 0.5 ]           % Border Color: Darker Gray (may not render)
    /CA ()                        % Caption: Empty
  >>
  /F 4                            % Flags: Printable
  /Ff 65536                       % Field Flags: Pushbutton
  % No /BS (Border Style) - unreliable rendering
  % No /A (Action) - clicks on grid do nothing
>>
endobj
"""

# Template for the interactive Start Button
BUTTON_OBJ_TEMPLATE = """
###IDX### 0 obj
<<
  /FT /Btn                        % Field Type: Button
  /T (###NAME###)                 % Field Name (e.g., StartButton)
  /Rect [ ###RECT### ]            % Position
  /P 16 0 R                       % Parent page
  /Subtype /Widget
  /F 4                            % Flags: Printable
  /Ff 65536                       % Field Flags: Pushbutton
  /H /P                           % Highlight mode: Push (inverts appearance on click)
  /MK << /CA (###LABEL###) >>     % Default caption (for accessibility)
  /AP << /N ###AP_IDX### 0 R >>   % Appearance Dictionary (Normal state points to AP Stream)
  /A <<                           % Action Dictionary (on Mouse Up)
    /S /JavaScript
    /JS ( try { ###JS_ACTION### } catch(e) { app.alert('JS Error: '+e); } ) % Execute JS
  >>
>>
endobj
"""

# Template for the Appearance Stream (drawing) for the Start Button
BUTTON_AP_STREAM_TEMPLATE = """
###IDX### 0 obj
<<
  /Type /XObject                  % It's an external object (used for appearance)
  /Subtype /Form                  % It's a Form XObject
  /FormType 1
  /BBox [ 0 0 ###WIDTH### ###HEIGHT### ] % Bounding box (size of button)
  /Matrix [ 1 0 0 1 0 0 ]         % Identity matrix (no transformation)
  /Resources <<                   % Resources needed for drawing
    /ProcSet [ /PDF /Text ]
    /Font << /HeBo 10 0 R >>      % Reference to Helvetica-Bold font object
  >>
  /Length ###LEN###               % Length of the stream content below
>>
stream
###STREAM_CONTENT###              % PDF drawing commands go here
endstream
endobj
"""

# Template for the hidden Text Field used for Keystroke Capture
TEXT_FIELD_TEMPLATE = """
###IDX### 0 obj
<<
  /FT /Tx                         % Field Type: Text
  /T (###NAME###)                 % Field Name (e.g., KeystrokeCatcher)
  /Rect [ ###RECT### ]            % Position
  /P 16 0 R                       % Parent page
  /Subtype /Widget
  /F 4                            % Flags: Printable
  /Ff 0                           % Field Flags: None (not multiline, etc.)
  /DA (/HeBo 10 Tf 0 g)           % Default Appearance (font/color for value)
  /V () /DV ()                    % Value / Default Value (empty)
  /MK << /BC [1 1 1] /BG [1 1 1] >> % Appearance: White border/background (to hide)
  /BS << /W 0 >>                  % Border Style: Width 0
  /Q 1                            % Quadding (Alignment): Center (optional)
  /AA <<                          % Additional Actions Dictionary
    /K <<                         % Keystroke Action (triggers on key press)
      /S /JavaScript
      /JS ( try { handleKeystroke(event); } catch(e) { app.alert('Keystroke JS Error: '+e); } )
    >>
  >>
>>
endobj
"""

# Template for the main JavaScript Stream Object (wrapper for the code)
JS_STREAM_OBJ = """
18 0 obj << /Length ###LEN### >> stream
###JS_CODE###
endstream endobj
"""

# --- Helper Function to Generate Static Grid Lines ---
def generate_grid_lines_content(g_off_x, g_off_y, g_width, g_height, cell_size):
    """Generates PDF drawing commands for a static background grid."""
    g_pixel_w = g_width * cell_size
    g_pixel_h = g_height * cell_size
    content = "q\n"       # Save graphics state
    content += "0.5 w\n"    # Line width (adjust as needed)
    content += "0.8 G\n"    # Stroke color (Light Gray) - Less intrusive
    # PDF Drawing Commands: m = move to, l = line to, S = stroke, Q = restore state
    # Horizontal lines
    for i in range(g_height + 1):
        y = g_off_y + i * cell_size
        content += f"{g_off_x:.1f} {y:.1f} m {g_off_x + g_pixel_w:.1f} {y:.1f} l\n"
    # Vertical lines
    for i in range(g_width + 1):
        x = g_off_x + i * cell_size
        content += f"{x:.1f} {g_off_y:.1f} m {x:.1f} {g_off_y + g_pixel_h:.1f} l\n"
    content += "S\n"       # Stroke the defined paths (draw the lines)
    content += "Q\n"       # Restore graphics state
    return content

# --- Main Script Logic ---

print("Starting PDF Snake Game Generation...")

# 1. Read JavaScript code from external file
js_file_path = "snake_game.js"
javascript_code = ""
if not os.path.exists(js_file_path):
    print(f"ERROR: JavaScript file not found at '{js_file_path}'")
    print("Please create snake_game.js in the same directory.")
    exit()
try:
    with open(js_file_path, "r") as f:
        javascript_code = f.read()
    print(f"- Successfully read JavaScript from {js_file_path}")
except Exception as e:
    print(f"Error reading JavaScript file: {e}")
    exit()

# 2. Inject Python constants into the JavaScript code string
# This allows easy configuration from the Python script
javascript_code = javascript_code.replace("###GRID_WIDTH###", str(GRID_WIDTH))
javascript_code = javascript_code.replace("###GRID_HEIGHT###", str(GRID_HEIGHT))
javascript_code = javascript_code.replace("###INITIAL_GAME_SPEED_MS###", str(INITIAL_GAME_SPEED_MS))
javascript_code = javascript_code.replace("###INITIAL_SNAKE_LENGTH###", str(INITIAL_SNAKE_LENGTH))
print("- Injected configuration constants into JavaScript.")

# 3. Initialize PDF Object Generation Variables
ui_element_objs_text = "" # Stores Start Button, Text Field objects
fields_text = ""          # Stores Grid Cell button objects
field_indexes = []        # List of *all* field object indices for AcroForm /Fields array
obj_idx_ctr = 20          # Start custom object indices after predefined ones (1-10, 16-18)

# 4. Generate UI Elements (Start Button, Keystroke Field)
print("- Generating UI elements...")
# 4a. Start Button Appearance Stream
start_button_label = "Start Game"; start_button_width = 100; start_button_height = 30
label_width_approx = len(start_button_label) * 12 * 0.6 # Rough estimate for centering text
text_pos_x = (start_button_width - label_width_approx) / 2
text_pos_y = (start_button_height - 12) / 2 + 2 # Adjust for font baseline
# PDF commands to draw button background, border, and text
ap_content_start_button = f"q 0.85 g 0 0 {start_button_width} {start_button_height} re f 0.5 G 0.5 w 0.25 0.25 {start_button_width}-0.5 {start_button_height}-0.5 re S Q\nq BT /HeBo 12 Tf 0 g {text_pos_x:.1f} {text_pos_y:.1f} Td ({start_button_label}) Tj ET Q"
ap_content_start_button_bytes = ap_content_start_button.encode('latin-1')
start_button_ap_idx = obj_idx_ctr
ap_stream = BUTTON_AP_STREAM_TEMPLATE; ap_stream = ap_stream.replace("###IDX###", str(start_button_ap_idx)); ap_stream = ap_stream.replace("###WIDTH###", str(start_button_width)); ap_stream = ap_stream.replace("###HEIGHT###", str(start_button_height)); ap_stream = ap_stream.replace("###LEN###", str(len(ap_content_start_button_bytes))); ap_stream = ap_stream.replace("###STREAM_CONTENT###", ap_content_start_button_bytes.decode('latin-1'))
ui_element_objs_text += ap_stream + "\n"; obj_idx_ctr += 1
# 4b. Start Button Widget Object
start_button_idx = obj_idx_ctr
start_button_y = GRID_OFF_Y - start_button_height - 20 # Position below grid
start_button_x = PAGE_CENTER_X - start_button_width / 2
start_button_rect = f"{start_button_x:.1f} {start_button_y:.1f} {start_button_x + start_button_width:.1f} {start_button_y + start_button_height:.1f}"
button_obj = BUTTON_OBJ_TEMPLATE; button_obj = button_obj.replace("###IDX###", str(start_button_idx)); button_obj = button_obj.replace("###NAME###", "StartButton"); button_obj = button_obj.replace("###LABEL###", start_button_label); button_obj = button_obj.replace("###RECT###", start_button_rect); button_obj = button_obj.replace("###AP_IDX###", str(start_button_ap_idx)); button_obj = button_obj.replace("###JS_ACTION###", "startGame();")
ui_element_objs_text += button_obj + "\n"; field_indexes.append(start_button_idx); obj_idx_ctr += 1
# 4c. Keystroke Catcher Text Field
keystroke_field_idx = obj_idx_ctr
kf_width = 50; kf_height = 10; kf_x = PAGE_CENTER_X - kf_width / 2; kf_y = start_button_y - kf_height - 5 # Position below button
kf_rect = f"{kf_x:.1f} {kf_y:.1f} {kf_x + kf_width:.1f} {kf_y + kf_height:.1f}"
text_field_obj = TEXT_FIELD_TEMPLATE; text_field_obj = text_field_obj.replace("###IDX###", str(keystroke_field_idx)); text_field_obj = text_field_obj.replace("###NAME###", "KeystrokeCatcher"); text_field_obj = text_field_obj.replace("###RECT###", kf_rect)
ui_element_objs_text += text_field_obj + "\n"; field_indexes.append(keystroke_field_idx); obj_idx_ctr += 1

print(f"- Generating {GRID_WIDTH * GRID_HEIGHT} grid cell objects...")
# 5. Generate the grid cell button objects
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        cell_template = CELL_OBJ_TEMPLATE
        # Calculate position based on grid coords, cell size, and offset
        left = GRID_OFF_X + x * CELL_SIZE
        bottom = GRID_OFF_Y + y * CELL_SIZE
        right = left + CELL_SIZE
        top = bottom + CELL_SIZE
        rect = f"{left:.1f} {bottom:.1f} {right:.1f} {top:.1f}"
        # Fill placeholders in template
        cell_object_str = cell_template.replace("###IDX###", f"{obj_idx_ctr}")
        cell_object_str = cell_object_str.replace("###X###", f"{x}")
        cell_object_str = cell_object_str.replace("###Y###", f"{y}")
        cell_object_str = cell_object_str.replace("###RECT###", rect)
        # Add generated object string to the collection
        fields_text += cell_object_str + "\n"
        field_indexes.append(obj_idx_ctr) # Add its index to the list
        obj_idx_ctr += 1 # Increment for next object

# 6. Prepare list of field indices for PDF structure
field_list_str = " ".join([f"{i} 0 R" for i in field_indexes]) # Format as "index 0 R" list

# 7. Create the main JS stream object string
js_bytes = javascript_code.encode('latin-1', 'ignore') # Encode for length calculation
js_stream_len = len(js_bytes)
js_stream_obj_str = JS_STREAM_OBJ # Use fixed ID 18
js_stream_obj_str = js_stream_obj_str.replace("###LEN###", str(js_stream_len))
# Decode back using same encoding for insertion into template
js_stream_obj_str = js_stream_obj_str.replace("###JS_CODE###", js_bytes.decode('latin-1'))

# 8. Generate Page Content Stream (Static Background Grid)
print("- Generating static background grid...")
page_content = generate_grid_lines_content(
    GRID_OFF_X, GRID_OFF_Y, GRID_WIDTH, GRID_HEIGHT, CELL_SIZE
)
page_content_bytes = page_content.encode('latin-1')
page_content_len = len(page_content_bytes)

# 9. Assemble the final PDF string by replacing all placeholders
print("- Assembling final PDF content...")
filled_pdf = PDF_FILE_TEMPLATE
# Insert Page Content (Static Grid)
filled_pdf = filled_pdf.replace("###PAGE_CONTENT_LEN###", str(page_content_len))
filled_pdf = filled_pdf.replace("###PAGE_CONTENT###", page_content_bytes.decode('latin-1'))
# Insert other generated parts
filled_pdf = filled_pdf.replace("###FIELD_LIST###", field_list_str)
filled_pdf = filled_pdf.replace("###FIELDS###", fields_text) # Grid cells
filled_pdf = filled_pdf.replace("###UI_ELEMENT_OBJS###", ui_element_objs_text) # Button, Text Field
filled_pdf = filled_pdf.replace("###JS_STREAM_PLACEHOLDER###", js_stream_obj_str)
filled_pdf = filled_pdf.replace("###OBJECT_COUNT###", f"{obj_idx_ctr}") # Trailer size = last object index + 1

# 10. Write the final string to a PDF file
output_filename = "snake.pdf"
print(f"- Writing PDF to {output_filename}...")
try:
    # Use 'latin-1' encoding when writing to preserve byte values if needed
    # It's generally safe for PDF structure which is mostly ASCII compatible
    with open(output_filename, "w", encoding='latin-1') as pdffile:
        pdffile.write(filled_pdf)
    print(f"-----------------------------------------------------")
    print(f"Successfully created {output_filename}")
    print(f"Ensure 'snake_game.js' is in the same directory.")
    print(f"-----------------------------------------------------")
except Exception as e:
    print(f"Error writing PDF file: {e}")
