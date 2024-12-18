from PIL import Image, ImageDraw, ImageFont

# Define the logo size and background color
logo_width = 400
logo_height = 400
background_color = (45, 118, 187)  # Dark blue: #2D76BB

# Create a new image with the specified dimensions and background color
logo_image = Image.new("RGB", (logo_width, logo_height), background_color)

# Set up the drawing context
draw = ImageDraw.Draw(logo_image)

# Define the text and font for the logo
text = "ACLARK.NET, LLC"
font_size = 40  # Adjust as desired to shrink the text
font_color = (255, 255, 255)  # White

# Load the Arial font and calculate the text size
font = ImageFont.truetype("Arial.ttf", font_size)

# https://stackoverflow.com/a/77074371/185820
text_width = draw.textlength(text, font=font)
text_height = font_size

# Calculate the position to center the text on the logo
text_x = (logo_width - text_width) // 2
text_y = (logo_height - text_height) // 2

# Calculate the dimensions for the rectangle
padding_x = 20
padding_y = 10
rectangle_width = text_width + (2 * padding_x)
rectangle_height = text_height + (2 * padding_y)

# Calculate the position to center the rectangle around the text
rectangle_x = text_x - padding_x
rectangle_y = text_y - padding_y

# Draw the rectangle
rectangle_coords = [
    (rectangle_x, rectangle_y),
    (rectangle_x + rectangle_width, rectangle_y + rectangle_height),
]
border_color = (255, 255, 255)  # White
border_width = 2  # Adjust as desired
draw.rectangle(rectangle_coords, outline=border_color, width=border_width)

# Draw the text on the logo
draw.text((text_x, text_y), text, font=font, fill=font_color)

# Save the logo as a PNG image
logo_image.save("aclarknet.png")
