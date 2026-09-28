import pygame


def text(surface, font, value, position, color=(239, 247, 255), center=False):
    image = font.render(str(value), False, color)
    rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
    surface.blit(image, rect)
    return rect


def panel(surface, rect, fill=(13, 24, 44), border=(93, 220, 207)):
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.rect(surface, border, rect, 2)


def bar(surface, rect, value, maximum, color=(87, 231, 190)):
    pygame.draw.rect(surface, (9, 15, 29), rect)
    ratio = max(0, min(1, value / maximum)) if maximum else 0
    pygame.draw.rect(surface, color, (rect.x + 2, rect.y + 2, int((rect.width - 4) * ratio), rect.height - 4))
    pygame.draw.rect(surface, (226, 241, 248), rect, 1)
