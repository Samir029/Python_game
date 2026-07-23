import pygame
import settings as cfg

class Bonus:
    """ Power-up entity falling from destroyed bricks. """
    TYPES = {
        'extend':     {'letter': 'E', 'color': cfg.GREEN},
        'shrink':     {'letter': 'S', 'color': cfg.RED},       # Paddle Shrink
        'speed_up':   {'letter': 'F', 'color': cfg.ORANGE},    # Ball Speed Up
        'speed_down': {'letter': 'D', 'color': cfg.CYAN},      # Ball Speed Down
    }

    def __init__(self, x: int, y: int, bonus_type: str) -> None:
        self.type = bonus_type
        self.rect = pygame.Rect(x, y, 24, 16)
        self.speed = 3
        
        info = self.TYPES.get(bonus_type, {'letter': '?', 'color': cfg.WHITE})
        self.letter = info['letter']
        self.color = info['color']

    def update(self) -> None:
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        pygame.draw.rect(screen, cfg.WHITE, self.rect, 1, border_radius=4)

        text_surf = font.render(self.letter, True, cfg.WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class Paddle:
    """ Our main player, Paddle, moves only horizontally. """

    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, cfg.PADDLE_WIDTH, cfg.PADDLE_HEIGHT)
        self.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0
        self.size_timer = 0

    def move(self, keys):
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
        
        self.rect.x += self.vx

        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def update(self, *args, **kwargs) -> None:
        """ Decrements timer and resets width after 15 seconds. """
        if self.size_timer > 0:
            self.size_timer -= 1
            if self.size_timer == 0:
                center_x = self.rect.centerx
                self.rect.width = cfg.PADDLE_WIDTH
                self.rect.centerx = center_x

    def apply_size_change(self, new_width: int, duration_sec: float = 15.0) -> None:
        center_x = self.rect.centerx
        self.rect.width = new_width
        self.rect.centerx = center_x
        self.size_timer = int(duration_sec * cfg.FPS)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, cfg.PADDLE_COLOR, self.rect, border_radius=5)


class Brick:
    """ Class for Game's brick. """
    
    def __init__(self, col: int, row: int, hp: int) -> None:
        self.hp = hp
        self.color = cfg.BRICK_COLORS.get(hp, cfg.GRAY)
        self.rect = pygame.Rect(
            cfg.FIELD_LEFT + col * cfg.BRICK_WIDTH,
            cfg.TOP_OFFSET + row * cfg.BRICK_HEIGHT,
            cfg.BRICK_WIDTH,
            cfg.BRICK_HEIGHT,
        )

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)
    
    def hit(self) -> None:
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS.get(self.hp, cfg.GRAY)


class Ball:
    """ Ball Actor class. """

    def __init__(self, x: int, y: int) -> None:
        self.radius = cfg.BALL_RADIUS
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 2 * self.radius, 2 * self.radius)
        self.base_speed_x = cfg.BALL_SPEED_X
        self.base_speed_y = cfg.BALL_SPEED_Y
        self.vx = self.base_speed_x
        self.vy = self.base_speed_y
        
        self.speed_timer = 0
        self.speed_multiplier = 1.0

    def apply_speed_multiplier(self, multiplier: float, duration_sec: float = 15.0) -> None:
        self.speed_multiplier = multiplier
        self.speed_timer = int(duration_sec * cfg.FPS)
        self._recalculate_velocity()

    def _recalculate_velocity(self) -> None:
        dir_x = 1 if self.vx >= 0 else -1
        dir_y = 1 if self.vy >= 0 else -1
        self.vx = dir_x * abs(self.base_speed_x) * self.speed_multiplier
        self.vy = dir_y * abs(self.base_speed_y) * self.speed_multiplier

    def update(self) -> None:
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer == 0:
                self.speed_multiplier = 1.0
                self._recalculate_velocity()

        self.rect.x += self.vx
        self.rect.y += self.vy

        # Border bounce logic
        if self.rect.left <= cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
            self.vx = abs(self.vx)

        if self.rect.right >= cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT
            self.vx = -abs(self.vx)

        if self.rect.top <= cfg.TOP_OFFSET:
            self.rect.top = cfg.TOP_OFFSET
            self.vy = abs(self.vy)

        if self.rect.top >= cfg.HEIGHT:
            self.rect.center = (cfg.WIDTH // 2, cfg.HEIGHT // 2)
            self.vx = cfg.BALL_SPEED_X
            self.vy = cfg.BALL_SPEED_Y
            self.speed_timer = 0
            self.speed_multiplier = 1.0

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, cfg.BALL_COLOR, self.rect.center, self.radius)