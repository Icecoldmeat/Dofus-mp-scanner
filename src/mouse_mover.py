import mouse
import time
import random
import math


class MouseMover:

    def move_mouse_natural(self,x1, y1, x2, y2, max_step=15):
        """
        Move mouse from (x1, y1) to (x2, y2) in a human-like, natural way.
        Short movements remain small and jittery; long movements are curved and smooth.

        max_step: maximum pixels per movement step (controls speed)
        """
        # Calculate distance
        distance = math.hypot(x2 - x1, y2 - y1)

        # If movement is very short, use tiny jittery linear steps
        if distance < 50:
            steps = max(int(distance / 2), 1)  # smaller steps for precision
            for i in range(1, steps + 1):
                t = i / steps
                nx = x1 + (x2 - x1) * t + random.uniform(-1, 1)
                ny = y1 + (y2 - y1) * t + random.uniform(-1, 1)
                mouse.move(int(nx), int(ny))
                time.sleep(random.uniform(0.03, 0.06))  # slower, natural movement
            return

        # For longer movements, use a curved Bezier path
        # Random control point
        cx = (x1 + x2) / 2 + random.randint(-100, 100)
        cy = (y1 + y2) / 2 + random.randint(-100, 100)

        # Quadratic Bezier interpolation
        def bezier(t, p0, p1, p2):
            return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

        steps = max(int(distance / max_step), 1)

        for i in range(1, steps + 1):
            t = i / steps
            nx = bezier(t, x1, cx, x2) + random.uniform(-2, 2)
            ny = bezier(t, y1, cy, y2) + random.uniform(-2, 2)
            mouse.move(int(nx), int(ny))

            # Speed modulation: start slow, fast in middle, slow at end
            speed = 0.002 + 0.004 * (1 - math.cos(t * math.pi))
            time.sleep(speed)



class NaturalMouseMover:
    def __init__(self, speed: float = 1.0):
        """
        speed:
            0.5  -> slow
            1.0  -> normal
            2.0+ -> fast
        """
        self.speed = max(0.1, speed)

    def _ease_in_out(self, t):
        return 3 * t**2 - 2 * t**3

    def _bezier(self, t, p0, p1, p2, p3):
        return (
            (1 - t)**3 * p0 +
            3 * (1 - t)**2 * t * p1 +
            3 * (1 - t) * t**2 * p2 +
            t**3 * p3
        )

    def _move_curve(self, x1, y1, x2, y2, duration, overshoot=False):
        distance = math.hypot(x2 - x1, y2 - y1)
        steps = max(20, int(distance / 4))

        ctrl_offset = distance * 0.3
        cx1 = x1 + random.uniform(-ctrl_offset, ctrl_offset)
        cy1 = y1 + random.uniform(-ctrl_offset, ctrl_offset)
        cx2 = x2 + random.uniform(-ctrl_offset, ctrl_offset)
        cy2 = y2 + random.uniform(-ctrl_offset, ctrl_offset)

        start_time = time.time()

        for i in range(steps + 1):
            t = i / steps
            eased = self._ease_in_out(t)

            x = self._bezier(eased, x1, cx1, cx2, x2)
            y = self._bezier(eased, y1, cy1, cy2, y2)

            # Reduced jitter near final target
            jitter_strength = max(0.5, distance * (0.003 if not overshoot else 0.002))
            x += random.uniform(-jitter_strength, jitter_strength)
            y += random.uniform(-jitter_strength, jitter_strength)

            mouse.move(int(x), int(y), absolute=True)

            # Speed variation
            base_delay = duration / steps
            variation = random.uniform(0.7, 1.3)
            time.sleep(base_delay * variation)

    def move(self, x1, y1, x2, y2):
        distance = math.hypot(x2 - x1, y2 - y1)
        base_duration = max(0.25, distance / (800 * self.speed))

        # --- Overshoot calculation ---
        overshoot_distance = min(8, distance * random.uniform(0.02, 0.05))
        angle = math.atan2(y2 - y1, x2 - x1)

        ox = x2 + math.cos(angle) * overshoot_distance
        oy = y2 + math.sin(angle) * overshoot_distance

        # --- Main movement (to overshoot) ---
        self._move_curve(
            x1, y1,
            ox, oy,
            base_duration * random.uniform(0.85, 1.1),
            overshoot=True
        )

        # Small human pause
        time.sleep(random.uniform(0.04, 0.12))

        # --- Correction movement (slow & precise) ---
        self._move_curve(
            ox, oy,
            x2, y2,
            base_duration * random.uniform(0.25, 0.4)
        )

        mouse.move(x2, y2, absolute=True)
