import os 
import qrcode
import pandas as pd
from PIL import Image, ImageDraw
from barcode import Code128
from barcode.writer import ImageWriter,SVGWriter
from io import BytesIO

# Function to add rounded corners to a single rectangle (module)
def draw_rounded_rect(draw, position, size, radius, fill_color):
    """Draw a single rounded rectangle at a given position."""
    x, y = position
    width, height = size
    draw.rounded_rectangle([x, y, x + width, y + height], radius=radius, fill=fill_color)

# Function to add rounded corners to the QR code
def add_rounded_corners(img, radius):
    # Create an image with transparent background
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw a rounded rectangle on the mask
    draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius, fill=255)
    
    # Apply the rounded rectangle mask to the image
    img.putalpha(mask)
    
    return img

def qrcode_generator(base_url,student_id,output_path):
    qr_url = f"{base_url}{student_id}"  # Create the full URL

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=12,
        border=2,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    # img = qr.make_image(fill_color="black", back_color="white")


    # Create a blank white image to draw on
    img_size = len(qr.get_matrix()) * qr.box_size
    img = Image.new('RGB', (img_size, img_size), 'white')
    draw = ImageDraw.Draw(img)
    
    # Set the radius for rounded corners
    radius = 10  # Adjust this to control how rounded the corners are
    
    # Iterate over the QR code matrix and draw rounded rectangles for each module
    for row_index, row_data in enumerate(qr.get_matrix()):
        for col_index, value in enumerate(row_data):
            if value:  # Only draw black (filled) modules
                x = col_index * qr.box_size
                y = row_index * qr.box_size
                if (row_index < 9 and col_index < 9) or (row_index < 9 and col_index >= len(qr.get_matrix())-9) or (row_index >= len(qr.get_matrix())-9 and col_index < 9):
                    continue
            
                if value:  # Only draw filled (black) modules
                    draw_rounded_rect(draw, (x, y), (qr.box_size, qr.box_size), radius, 'black')

    # Draw the three large corner blocks with rounded borders (single rectangle)
    # Top-left corner
    draw_rounded_rect(draw, (24, 24), (7 * qr.box_size, 7 * qr.box_size), 20, 'crimson')
    draw_rounded_rect(draw, (36, 36), (5 * qr.box_size, 5 * qr.box_size), 15, 'white')
    draw_rounded_rect(draw, (48, 48), (3 * qr.box_size, 3 * qr.box_size), 10, 'crimson')
    # Top-right corner
    draw_rounded_rect(draw, ((len(qr.get_matrix())-9) * qr.box_size, 24), (7 * qr.box_size, 7 * qr.box_size), 20, 'darkorange')
    draw_rounded_rect(draw, ((len(qr.get_matrix())-8) * qr.box_size, 36), (5 * qr.box_size, 5 * qr.box_size), 15, 'white')
    draw_rounded_rect(draw, ((len(qr.get_matrix())-7) * qr.box_size, 48), (3 * qr.box_size, 3 * qr.box_size), 10, 'darkorange')
    # Bottom-left corner
    draw_rounded_rect(draw, (24, (len(qr.get_matrix())-9) * qr.box_size), (7 * qr.box_size, 7 * qr.box_size), 20, 'deepskyblue')
    draw_rounded_rect(draw, (36, (len(qr.get_matrix())-8) * qr.box_size), (5 * qr.box_size, 5 * qr.box_size), 15, 'white')
    draw_rounded_rect(draw, (48, (len(qr.get_matrix())-7) * qr.box_size), (3 * qr.box_size, 3 * qr.box_size), 10, 'deepskyblue')

    img = add_rounded_corners(img, radius)
    # Save QR code image using Admission Number as the file name
    img.save(output_path)

# Function to generate barcode for student ID
def generate_barcode(student_id, output_path):
    """Generate a barcode (Code128) for the student ID and save it."""

    barcode_instance = Cod(student_id, writer=ImageWriter())
    barcode_instance.writer.module_height = 5
    print(barcode_instance)
    barcode_instance.save(output_path,{"module_width":0.35, "module_height":8, "font_size": 6, "text_distance": 4, "quiet_zone": 3})

candidate_data = pd.read_excel('E:/Storage Folder/Sibaq/qrcode/candidates.xlsx')

base_url = 'https://result.sibaq.in/search?student='
qrcode_folder = 'qrcodes'
barcode_folder = 'barcodes'
os.makedirs(qrcode_folder, exist_ok=True)
os.makedirs(barcode_folder, exist_ok=True)
# Convert 'DateOfBirth' to datetime and handle different formats
candidate_data['dob'] = pd.to_datetime(candidate_data['dob'], errors='coerce', utc=True)  # Handle invalid formats with 'coerce'

# Format the DateOfBirth as DDMMYYYY
candidate_data['dob'] = candidate_data['dob'].dt.strftime('%d%m%Y')

# Loop through each student and generate QR code
base_url = "https://result.sibaq.in/search?student="
for index, row in candidate_data.iterrows():
    student_id = f"{row['chestNo']}{row['dob']}"  # Combine Admission Number and DOB
    print(student_id)
    qrcode_path = os.path.join(qrcode_folder, f"{row['chestNo']}.png")
    print(qrcode_path)
    qrcode_generator(base_url,student_id,qrcode_path)
    
    barcode_filepath = os.path.join(barcode_folder, f"{row['chestNo']}")
    if student_id.isdigit():
        generate_barcode(student_id,barcode_filepath)
    else:
        print("Error in generating Barcode: ", student_id, 'is not valueable Number') 
    
print(f"QR codes and Bar codes have been saved in the '{qrcode_folder}' folder and '{barcode_folder}' with Admission Numbers as file names.")
