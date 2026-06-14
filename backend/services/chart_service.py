import base64
import math

from models.schemas import ScoreRadar


class ChartService:
    def radar_chart_base64(self, radar: ScoreRadar) -> str:
        svg = self.radar_chart_svg(radar)
        return base64.b64encode(svg.encode("utf-8")).decode("ascii")

    @staticmethod
    def radar_chart_svg(radar: ScoreRadar) -> str:
        labels = ["Technical", "Communication", "Presence", "Grammar"]
        values = [radar.technical, radar.communication, radar.presence, radar.grammar]
        cx, cy, radius = 150, 150, 100
        points: list[tuple[float, float]] = []

        for index, value in enumerate(values):
            angle = -math.pi / 2 + (2 * math.pi * index / len(values))
            r = radius * (value / 100)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))

        polygon = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        rings = []
        for level in (25, 50, 75, 100):
            ring_points = []
            for index in range(len(labels)):
                angle = -math.pi / 2 + (2 * math.pi * index / len(labels))
                r = radius * (level / 100)
                ring_points.append(
                    f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}"
                )
            rings.append(
                f'<polygon points="{" ".join(ring_points)}" fill="none" stroke="#334155" stroke-width="1"/>'
            )

        axes = []
        label_nodes = []
        for index, label in enumerate(labels):
            angle = -math.pi / 2 + (2 * math.pi * index / len(labels))
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            lx = cx + (radius + 22) * math.cos(angle)
            ly = cy + (radius + 22) * math.sin(angle)
            axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#475569" stroke-width="1"/>')
            label_nodes.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#bfdbfe" font-size="12" text-anchor="middle">{label}</text>'
            )

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300">
  <rect width="300" height="300" fill="#0b1020"/>
  {''.join(rings)}
  {''.join(axes)}
  <polygon points="{polygon}" fill="rgba(79,124,255,0.25)" stroke="#4f7cff" stroke-width="2"/>
  {''.join(label_nodes)}
  <text x="150" y="24" fill="#e2e8f0" font-size="14" text-anchor="middle">Interview Score Profile</text>
</svg>"""


chart_service = ChartService()
