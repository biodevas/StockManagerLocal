from PIL import Image, ImageDraw

def create_default_image():
    # Create a new image with dark background
    img = Image.new('RGB', (800, 800), color='#2b3035')
    draw = ImageDraw.Draw(img)

    # Draw a simple bottle shape
    draw.rectangle([300, 200, 500, 600], fill='#495057')
    draw.ellipse([300, 150, 500, 250], fill='#495057')
    draw.rectangle([350, 100, 450, 150], fill='#495057')

    # Create the uploads directory if it doesn't exist
    img.save('static/uploads/default_beverage.png')

if __name__ == "__main__":
    create_default_image()
