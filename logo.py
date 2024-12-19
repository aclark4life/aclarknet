from PIL import Image, ImageDraw, ImageFont

# Define the logo dimensions (circle)
logo_size = 500

# Create a new transparent image with RGBA mode
logo_image = Image.new(
    "RGBA", (logo_size, logo_size), (0, 0, 0, 0)
)  # Fully transparent

# Set up the drawing context
draw = ImageDraw.Draw(logo_image)

# Define the stacked text and font for the logo
lines = ["ACLARK.", "NET,", "LLC"]
font_size = 40  # Adjust as desired
font_color = (45, 118, 187, 255)  # #2D76BB in RGBA (dark blue)
circle_color = (45, 118, 187, 255)  # #2D76BB in RGBA (dark blue)

# Load the Arial font
font = ImageFont.truetype("Arial.ttf", font_size)

# Calculate the total text height
text_heights = [
    draw.textbbox((0, 0), line, font=font)[3]
    - draw.textbbox((0, 0), line, font=font)[1]
    for line in lines
]
total_text_height = (
    sum(text_heights) + (len(lines) - 1) * 10
)  # Add spacing between lines

# Calculate the position to center the circle and text
padding = 50
circle_radius = (logo_size - padding * 2) // 2
circle_center = (logo_size // 2, logo_size // 2)

# Draw the circle border
circle_bbox = [
    (circle_center[0] - circle_radius, circle_center[1] - circle_radius),
    (circle_center[0] + circle_radius, circle_center[1] + circle_radius),
]
border_width = 4
draw.ellipse(circle_bbox, outline=circle_color, width=border_width)

# Draw each line of text centered inside the circle
current_y = circle_center[1] - total_text_height // 2
for line in lines:
    text_bbox = draw.textbbox((0, 0), line, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (logo_size - text_width) // 2
    draw.text((text_x, current_y), line, font=font, fill=font_color)
    current_y += text_height + 10  # Move to the next line with spacing

# Save the final logo as a PNG image with transparency
logo_image.save("aclarknet_logo_with_circle.png")
