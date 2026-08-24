from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "sample_data" / "terrafly_synthetic_aerial.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    width, height = 480, 320
    image = Image.new("RGB", (width, height), "#5f8851")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 250, 136), fill="#96a85c")
    draw.rectangle((258, 0, width, 124), fill="#758e43")
    draw.rectangle((0, 145, 164, height), fill="#7c9b50")
    draw.rectangle((174, 132, width, height), fill="#8ca45a")
    draw.polygon([(0, 118), (480, 202), (480, 250), (0, 166)], fill="#7c8079")
    draw.line([(0, 137), (480, 224)], fill="#d2cbb6", width=4)
    draw.polygon([(278, 54), (402, 75), (386, 166), (262, 143)], fill="#e5ded0")
    draw.polygon([(278, 54), (402, 75), (390, 87), (267, 66)], fill="#fbf7eb")
    draw.rectangle((306, 102, 328, 150), fill="#34483f")
    draw.ellipse((66, 211, 128, 275), fill="#255f3b")
    draw.ellipse((104, 225, 174, 296), fill="#347345")
    draw.ellipse((48, 253, 106, 310), fill="#1e5234")
    draw.ellipse((412, 12, 468, 68), fill="#2c6a3c")
    draw.rectangle((211, 218, 257, 269), fill="#7a543e")
    draw.polygon([(205, 220), (234, 191), (264, 220)], fill="#b76645")
    image.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
