import json
import random
from pathlib import Path

import pygame

from .entities import AnswerGate, Runner, LANE_COLORS
from .ui import bar, panel, text


PHASES = [
    ("ADICAO E SUBTRACAO", 5, 18, 0.0, (255, 220, 196)),
    ("MULTIPLICACAO", 6, 20, 0.0, (255, 237, 174)),
    ("DIVISAO E FRACOES", 7, 22, 0.5, (194, 236, 219)),
    ("EQUACOES DE 1o GRAU", 8, 24, 0.8, (205, 218, 255)),
    ("DESAFIO MISTURADO", 9, 26, 1.0, (245, 202, 238)),
]
LEADERBOARD = Path(__file__).resolve().parent.parent / "ranking.json"
ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"


def make_question(phase):
    if phase == 0:
        a, b = random.randint(2, 18), random.randint(1, 15)
        op = random.choice(("+", "-"))
        if op == "-" and b > a:
            a, b = b, a
        return f"{a} {op} {b} = ?", a + b if op == "+" else a - b
    if phase == 1:
        a, b = random.randint(2, 12), random.randint(2, 9)
        return f"{a} x {b} = ?", a * b
    if phase == 2:
        if random.random() < 0.5:
            answer, divisor = random.randint(2, 12), random.randint(2, 9)
            return f"{answer * divisor} / {divisor} = ?", answer
        den = random.choice((2, 3, 4, 5, 6))
        num = random.randint(1, den - 1)
        return f"{num}/{den} de {den * 4} = ?", num * 4
    if phase == 3:
        answer = random.randint(2, 18)
        if random.random() < 0.5:
            offset = random.randint(1, 12)
            return f"x + {offset} = {answer + offset}", answer
        factor = random.randint(2, 9)
        return f"{factor}x = {factor * answer}", answer
    kind = random.choice((0, 1, 2, 3))
    if kind == 0:
        a, b = random.randint(5, 25), random.randint(2, 18)
        return f"{a} + {b} = ?", a + b
    if kind == 1:
        a, b = random.randint(3, 12), random.randint(2, 9)
        return f"{a} x {b} = ?", a * b
    if kind == 2:
        answer, divisor = random.randint(2, 15), random.randint(2, 9)
        return f"{answer * divisor} / {divisor} = ?", answer
    answer, offset = random.randint(2, 18), random.randint(2, 12)
    return f"x + {offset} = {answer + offset}", answer


def make_choices(correct):
    values = {correct}
    while len(values) < 3:
        delta = random.choice((-12, -9, -6, -4, -3, -2, -1, 1, 2, 3, 4, 6, 9, 12))
        values.add(max(0, correct + delta))
    choices = list(values)
    random.shuffle(choices)
    return choices


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.bounds = screen.get_rect()
        self.font = pygame.font.Font(None, 24)
        self.small = pygame.font.Font(None, 19)
        self.big = pygame.font.Font(None, 54)
        self.title = pygame.font.Font(None, 76)
        self.state = "menu"
        self.name = "JOGADOR"
        self.best = self.load_scores()
        self.scroll = 0
        self.background_image = None
        background_path = ASSET_DIR / "background.png"
        if background_path.exists():
            try:
                self.background_image = pygame.transform.smoothscale(
                    pygame.image.load(background_path).convert(), self.screen.get_size())
            except (pygame.error, OSError):
                self.background_image = None
        self.reset_run()

    def load_scores(self):
        try:
            data = json.loads(LEADERBOARD.read_text(encoding="utf-8"))
            return sorted(data, key=lambda row: row.get("score", 0), reverse=True)[:10]
        except (OSError, ValueError, TypeError):
            return []

    def save_score(self):
        scores = self.load_scores()
        scores.append({"name": self.name.strip() or "JOGADOR", "score": self.score, "phase": self.phase + 1})
        scores.sort(key=lambda row: row.get("score", 0), reverse=True)
        self.best = scores[:10]
        LEADERBOARD.write_text(json.dumps(self.best, ensure_ascii=False, indent=2), encoding="utf-8")

    def reset_run(self):
        self.phase = 0
        self.score = 0
        self.streak = 0
        self.question_number = 0
        self.phase_points = 0
        self.time_left = PHASES[0][2]
        self.lane_centers = [210, 480, 750]
        self.runner = Runner(1, 430)
        self.next_question()

    def next_question(self):
        self.question, self.correct = make_question(self.phase)
        self.choices = make_choices(self.correct)
        self.gates = [AnswerGate(index, answer, -30) for index, answer in enumerate(self.choices)]
        self.gate_speed = 155 + self.phase * 18
        self.time_limit = PHASES[self.phase][2]
        self.time_left = self.time_limit
        self.question_number += 1

    def event(self, event):
        if self.state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset_run()
                    self.state = "play"
                elif event.key == pygame.K_r:
                    self.state = "ranking"
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.unicode and event.unicode.isprintable() and len(self.name) < 14:
                    self.name = ("" if self.name == "JOGADOR" else self.name) + event.unicode.upper()
        elif self.state == "ranking":
            if event.type == pygame.KEYDOWN:
                self.state = "menu"
        elif self.state == "play":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.runner.lane = max(0, self.runner.lane - 1)
                elif event.key == pygame.K_RIGHT:
                    self.runner.lane = min(2, self.runner.lane + 1)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "pause"
        elif self.state == "pause":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "play"
                elif event.key == pygame.K_q:
                    self.state = "menu"
        elif self.state in ("lost", "win"):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_run()
                    self.state = "play"
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = "menu"

    def finish(self, won=False):
        self.state = "win" if won else "lost"
        self.save_score()

    def update(self, dt):
        if self.state != "play":
            return
        self.scroll += dt * self.gate_speed
        self.time_left -= dt
        self.runner.update(dt, self.lane_centers)
        for gate in self.gates:
            gate.y += self.gate_speed * dt
        if self.time_left <= 0:
            self.streak = 0
            self.finish()
            return
        if self.gates and self.gates[0].y >= self.runner.y:
            chosen = self.choices[self.runner.lane]
            if chosen != self.correct:
                self.streak = 0
                self.finish()
                return
            self.streak += 1
            self.phase_points += 1
            multiplier = min(5, self.streak)
            self.score += 100 + self.phase * 30 + (multiplier - 1) * 25
            self.gates = []
            if self.phase_points >= PHASES[self.phase][1]:
                self.score += 250 * (self.phase + 1)
                if self.phase == len(PHASES) - 1:
                    self.finish(won=True)
                    return
                self.phase += 1
                self.phase_points = 0
                self.runner.lane = 1
                self.next_question()
            else:
                self.next_question()

    def background(self, phase=None):
        phase = self.phase if phase is None else phase
        color = PHASES[phase][4]
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(color)
            # Warm paper-like frame around a bright three-lane arcade track.
            pygame.draw.rect(self.screen, (255, 249, 235), (54, 0, 852, 576))
            pygame.draw.rect(self.screen, (255, 255, 255), (79, 0, 802, 576))
        for index, center in enumerate(self.lane_centers):
            lane_rect = pygame.Rect(center - 128, 0, 256, 576)
            lane_fill = ((255, 240, 239), (244, 238, 255), (255, 247, 222))[index]
            pygame.draw.rect(self.screen, lane_fill, lane_rect)
            pygame.draw.line(self.screen, (213, 204, 216), (lane_rect.left, 0), (lane_rect.left, 576), 2)
            pygame.draw.line(self.screen, (213, 204, 216), (lane_rect.right, 0), (lane_rect.right, 576), 2)
        # Scrolling confetti marks and math symbols signal arcade speed.
        for y in range(-32, 600, 64):
            yy = (y + int(self.scroll)) % 640
            pygame.draw.rect(self.screen, (206, 194, 220), (478, yy, 4, 24), border_radius=2)
        symbols = ("+", "x", "÷", "=")
        for x in (22, 928):
            for index, y in enumerate(range(-20, 600, 96)):
                yy = (y + int(self.scroll * 0.72)) % 620
                pygame.draw.circle(self.screen, (255, 255, 255), (x, yy), 17)
                text(self.screen, self.font, symbols[(index + phase) % len(symbols)], (x, yy),
                     (135, 91, 255), True)

    def draw_play(self):
        self.background()
        phase_name, total, _, _, _ = PHASES[self.phase]
        for index, gate in enumerate(self.gates):
            lane_rect = pygame.Rect(self.lane_centers[index] - 128, 0, 256, 576)
            gate.draw(self.screen, lane_rect, index == self.runner.lane)
            text(self.screen, self.big, gate.answer, (self.lane_centers[index], gate.y), LANE_COLORS[index], True)
        pygame.draw.line(self.screen, (250, 228, 157), (80, self.runner.y + 27), (880, self.runner.y + 27), 2)
        self.runner.draw(self.screen)
        panel(self.screen, pygame.Rect(14, 12, 285, 36), (255, 255, 255), (135, 91, 255))
        text(self.screen, self.small, f"FASE {self.phase + 1}/5  |  {phase_name}", (27, 22), (48, 41, 70))
        panel(self.screen, pygame.Rect(315, 12, 330, 58), (53, 43, 82), (255, 184, 54))
        text(self.screen, self.font, self.question, (480, 41), (255, 245, 208), True)
        panel(self.screen, pygame.Rect(674, 12, 272, 36), (255, 255, 255), (255, 91, 126))
        text(self.screen, self.small, f"{self.name[:12]}   PONTOS {self.score}", (687, 22), (48, 41, 70))
        text(self.screen, self.small, f"QUESTAO {self.phase_points + 1}/{total}   SEQUENCIA x{min(5, max(1, self.streak))}", (480, 518), (53, 43, 82), True)
        bar(self.screen, pygame.Rect(382, 540, 196, 16), self.time_left, self.time_limit,
            (92, 225, 179) if self.time_left > self.time_limit * .35 else (245, 111, 105))
        text(self.screen, self.small, "SETA ESQUERDA / DIREITA: TROCAR DE FAIXA", (480, 566), (72, 62, 92), True)

    def draw_center(self, heading, lines, footer, phase=None):
        self.background(phase)
        shade = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        shade.fill((53, 43, 82, 125))
        self.screen.blit(shade, (0, 0))
        panel(self.screen, pygame.Rect(145, 75, 670, 430), (255, 250, 239), (135, 91, 255))
        text(self.screen, self.title, heading, (480, 142), (135, 91, 255), True)
        for index, line in enumerate(lines):
            text(self.screen, self.font, line, (480, 220 + index * 34), (53, 43, 82), True)
        text(self.screen, self.small, footer, (480, 462), (228, 104, 92), True)

    def draw(self):
        if self.state == "play":
            self.draw_play()
        elif self.state == "menu":
            self.draw_center("MATH RUNNER", ["Resolva, troque de faixa e corra ate o fim das cinco fases.",
                "Seu apelido para o ranking: " + self.name + "_", "Adicao, multiplicacao, fracoes, equacoes e desafio misturado."],
                "[ENTER] JOGAR     [R] RANKING     [BACKSPACE] APAGAR NOME")
        elif self.state == "ranking":
            rows = [f"{i + 1:02d}. {row.get('name', 'JOGADOR'):<14}  {row.get('score', 0):>6} PTS  |  FASE {row.get('phase', 1)}"
                    for i, row in enumerate(self.best)]
            if not rows:
                rows = ["Ainda nao ha pontuacoes salvas."]
            self.draw_center("RANKING", rows[:8], "[QUALQUER TECLA] VOLTAR AO MENU")
        elif self.state == "pause":
            self.draw_center("PAUSADO", [f"{PHASES[self.phase][0]}  |  PONTOS {self.score}"],
                             "[ESC] CONTINUAR     [Q] MENU")
        elif self.state == "lost":
            self.draw_center("FIM DE JOGO", ["Resposta incorreta ou tempo esgotado.",
                f"{self.name}  |  PONTOS: {self.score}", f"FASE ALCANCADA: {self.phase + 1}/5"],
                "[R] TENTAR DE NOVO     [ENTER] MENU")
        elif self.state == "win":
            self.draw_center("VOCE VENCEU!", ["Todas as cinco fases concluidas!",
                f"{self.name}  |  PONTOS: {self.score}", "Sua pontuacao foi salva no ranking local."],
                "[R] JOGAR NOVAMENTE     [ENTER] MENU", phase=4)
