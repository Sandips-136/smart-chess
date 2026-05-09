import time
import board
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# --- OLED setup ---
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear screen
oled.fill(0)
oled.show()

# Create image buffer
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Font (default)
font = ImageFont.load_default()

# --- Test loop ---
while True:
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    draw.text((0, 0), "OLED TEST OK", font=font, fill=255)
    draw.text((0, 20), "If you see this", font=font, fill=255)
    draw.text((0, 40), "hardware is fine", font=font, fill=255)

    oled.image(image)
    oled.show()

    time.sleep(1)
