from PIL import Image, ImageDraw, ImageFont

# Define the logo dimensions
logo_width = 400
logo_height = 200  # Rectangle dimensions

# Create a new transparent image with RGBA mode
logo_image = Image.new(
    "RGBA", (logo_width, logo_height), (0, 0, 0, 0)
)  # Fully transparent

# Set up the drawing context
draw = ImageDraw.Draw(logo_image)

# Define the text and font for the logo
text = "ACLARK.NET, LLC"
font_size = 40  # Adjust as desired
font_color = (45, 118, 187, 255)  # #2D76BB in RGBA (dark blue)
border_color = (45, 118, 187, 255)  # #2D76BB in RGBA (dark blue)

# Load the Arial font and calculate the text size
font = ImageFont.truetype("Arial.ttf", font_size)
text_width = draw.textlength(text, font=font)
text_height = font_size

# Add padding around the text for the border
padding_x = 20
padding_y = 10
rectangle_width = text_width + 2 * padding_x
rectangle_height = text_height + 2 * padding_y

# Calculate the position to center the rectangle
rectangle_x = (logo_width - rectangle_width) // 2
rectangle_y = (logo_height - rectangle_height) // 2

# Draw the rectangle border
rectangle_coords = [
    (rectangle_x, rectangle_y),
    (rectangle_x + rectangle_width, rectangle_y + rectangle_height),
]
border_width = 2
draw.rectangle(rectangle_coords, outline=border_color, width=border_width)

# Draw the text inside the rectangle
text_x = rectangle_x + padding_x
text_y = rectangle_y + padding_y
draw.text((text_x, text_y), text, font=font, fill=font_color)

# Crop the image tightly around the rectangle
cropped_image = logo_image.crop(
    (
        rectangle_coords[0][0] - border_width,  # Left
        rectangle_coords[0][1] - border_width,  # Top
        rectangle_coords[1][0] + border_width,  # Right
        rectangle_coords[1][1] + border_width,  # Bottom
    )
)

# Save the cropped logo as a PNG image with transparency
cropped_image.save("aclarknet_logo_transparent_blue.png")
