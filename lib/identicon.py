from PIL import Image, ImageDraw
import random
import io

def generate_identicon(size=80, grid_size=10):
    """
    Generates a random identicon with a black and orange color scheme.

    :param size: Size of the identicon image (in pixels, square).
    :param grid_size: Number of squares in the grid (per row and column).
    :return: A PIL Image object representing the identicon.
    """
    # Cell size in pixels
    cell_size = size // grid_size

    # Create a blank transparent image
    image = Image.new("RGBA", (size, size), (27, 27, 27, 255))
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=size // 2, fill=255)

    draw = ImageDraw.Draw(image)

    # Generate random pattern
    pattern = []
    for i in range(grid_size):
        row = [random.choice([True, False]) for _ in range((grid_size + 1) // 2)]
        pattern.append(row + row[::-1][:grid_size // 2])

    # Draw the pattern on the grid
    for y, row in enumerate(pattern):
        for x, cell in enumerate(row):
            if cell:
                x0 = x * cell_size
                y0 = y * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                draw.rectangle([x0, y0, x1, y1], fill="orange")

    # Apply corner radius mask
    final_image = Image.new("RGBA", (size, size), (27, 27, 27, 0))  # Dark gray background
    final_image.paste(image, (0, 0), mask)

    buffer = io.BytesIO()
    final_image.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer.read()
