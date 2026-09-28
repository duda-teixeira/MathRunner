from pathlib import Path

import pygame


LANE_COLORS = [(255, 91, 126), (135, 91, 255), (255, 184, 54)]


class Runner:
    def __init__(self, lane, y):
        self.lane = lane
        self.y = y
        self.x = 0
        self.target_x = 0
        self.rect = pygame.Rect(0, 0, 46, 58)
        image_path = Path(__file__).resolve().parent.parent / "assets" / "jogadora (2).png"
        self.image = None
        if image_path.exists():
            try:
                # Nearest-neighbor scaling keeps the pixel art crisp.
                self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (76, 76))
            except (pygame.error, OSError):
                self.image = None

    def update(self, dt, lane_centers):
        self.target_x = lane_centers[self.lane]
        self.x += (self.target_x - self.x) * min(1, dt * 13)
        self.rect.center = round(self.x), self.y

    def draw(self, screen):
        x, y = self.rect.center
        if self.image:
            screen.blit(self.image, self.image.get_rect(center=(x, y)))
            return
        # Bright arcade mascot fallback if the player image cannot be loaded.
        pygame.draw.ellipse(screen, (255, 184, 54), (x - 19, y - 26, 38, 48))
        pygame.draw.rect(screen, (135, 91, 255), (x - 12, y - 8, 24, 24), border_radius=7)
        pygame.draw.rect(screen, (255, 255, 255), (x - 9, y - 19, 18, 10), border_radius=5)
        pygame.draw.circle(screen, (35, 35, 61), (x + 3, y - 14), 2)
        pygame.draw.rect(screen, (255, 91, 126), (x - 12, y + 13, 8, 12), border_radius=3)
        pygame.draw.rect(screen, (255, 91, 126), (x + 4, y + 13, 8, 12), border_radius=3)
        pygame.draw.rect(screen, (35, 35, 61), (x - 16, y + 22, 12, 5), border_radius=2)
        pygame.draw.rect(screen, (35, 35, 61), (x + 4, y + 22, 12, 5), border_radius=2)


class AnswerGate:
    def __init__(self, lane, answer, y):
        self.lane = lane
        self.answer = answer
        self.y = y
        self.passed = False

    def draw(self, screen, rect, selected=False):
        color = LANE_COLORS[self.lane]
        gate = pygame.Rect(rect.x + 17, self.y - 24, rect.width - 34, 48)
        pygame.draw.rect(screen, (255, 255, 255), gate, border_radius=10)
        pygame.draw.rect(screen, color, gate, 3)
        pygame.draw.rect(screen, color, (gate.x, gate.y, 8, gate.height), border_radius=4)
        if selected:
            pygame.draw.rect(screen, (255, 255, 255), gate, 2)
