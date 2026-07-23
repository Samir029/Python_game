import random
import pygame
import settings as cfg
from game.entities import Paddle, Ball, Bonus, Brick

def ApplyBonus(bonus: Bonus, paddle: Paddle, ball: Ball) -> None:
    """
    Applies power-up behavior for 15 seconds:
    - shrink: Paddle Shrink
    - extend: Paddle Extend
    - speed_up: Ball Speed Up
    - speed_down: Ball Speed Down
    """
    if bonus.type == 'shrink':
        paddle.apply_size_change(new_width=50, duration_sec=15.0)
    elif bonus.type == 'extend':
        paddle.apply_size_change(new_width=150, duration_sec=15.0)
    elif bonus.type == 'speed_up':
        ball.apply_speed_multiplier(multiplier=1.5, duration_sec=15.0)
    elif bonus.type == 'speed_down':
        ball.apply_speed_multiplier(multiplier=0.6, duration_sec=15.0)


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> None:
    font = pygame.font.SysFont("Arial", 12, bold=True)
    paddle = Paddle()
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT - 100)
    bonuses: list[Bonus] = []

    # Generate a grid of bricks to play with
    bricks: list[Brick] = []
    for row in range(4):
        for col in range(cfg.FIELD_COLS):
            hp = random.choice([1, 1, 2])
            bricks.append(Brick(col, row, hp))

    running = True
    while running:
        clock.tick(cfg.FPS)

        # 1. Handle Window Close / Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Key presses & movement
        keys = pygame.key.get_pressed()
        paddle.move(keys)
        paddle.update()
        ball.update()

        # 3. Ball vs Paddle Collision
        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            ball.vy = -abs(ball.vy)

        # 4. Ball vs Bricks Collision
        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                ball.vy = -ball.vy
                is_destroyed = brick.hit()
                
                if is_destroyed:
                    bricks.remove(brick)
                    
                    # 30% CHANCE TO DROP A POWER-UP
                    if random.random() < 0.30:
                        bonus_type = random.choice(['shrink', 'extend', 'speed_up', 'speed_down'])
                        bonuses.append(Bonus(brick.rect.centerx, brick.rect.centery, bonus_type))
                break

        # 5. Update Falling Power-Ups & Check Paddle Collection
        for bonus in bonuses[:]:
            bonus.update()
            if paddle.rect.colliderect(bonus.rect):
                ApplyBonus(bonus, paddle, ball)
                bonuses.remove(bonus)
            elif bonus.rect.top > cfg.HEIGHT:
                bonuses.remove(bonus)

        # 6. Render Everything to Screen
        screen.fill(cfg.BLACK)
        
        for brick in bricks:
            brick.draw(screen)

        for bonus in bonuses:
            bonus.draw(screen, font)

        paddle.draw(screen)
        ball.draw(screen)

        pygame.display.flip()