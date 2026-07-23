import random
import pygame
import settings as cfg
from screens.game_screen import run as game_screen
from game.entities import Paddle, Brick, Ball, Bonus
from game.level import load_level

def ApplyBonus(bonus: Bonus, paddle: Paddle, ball: Ball) -> None:
    """ Applies power-up effect for 15 seconds. """
    if bonus.type == 'shrink':
        paddle.apply_size_change(new_width=50, duration_sec=15.0)
    elif bonus.type == 'extend':
        paddle.apply_size_change(new_width=150, duration_sec=15.0)
    elif bonus.type == 'speed_up':
        ball.apply_speed_multiplier(multiplier=1.5, duration_sec=15.0)
    elif bonus.type == 'speed_down':
        ball.apply_speed_multiplier(multiplier=0.6, duration_sec=15.0)

def _bounce_off_rect(ball: Ball, rect: pygame.Rect):
    """ Checks if the Ball collides with the given rect. """
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(
        overlap_bottom,
        overlap_left,
        overlap_right,
        overlap_top
    )
    
    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vy < 0:
        ball.rect.left = rect.right
        ball.vx *= -1

def _handle_ball_vs_bricks(
    ball: Ball,
    bricks: list[Brick],
    bonuses: list[Bonus]
) -> int:
    scored = 0
    for brick in bricks[:]:  
        if not ball.rect.colliderect(brick.rect):
            continue
        _bounce_off_rect(ball, brick.rect)
        if brick.hp == -1: 
            continue
        
        brick.hit()

        if brick.hp <= 0:
            bricks.remove(brick)
            scored += 10
            
            # 30% CHANCE TO DROP A POWER-UP
            if random.random() < 0.30:
                b_type = random.choice(['shrink', 'extend', 'speed_up', 'speed_down'])
                bonuses.append(Bonus(brick.rect.centerx, brick.rect.centery, b_type))
    return scored

def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """ Handles Ball bounce over the Paddle. """
    _bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 12, bold=True)

    running = True
    paddle = Paddle()
    bonuses: list[Bonus] = []

    bricks, rows, cols = load_level(1)
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT - 100)

    while running:
        screen.fill(cfg.BLACK)

        # Update Section
        keys = pygame.key.get_pressed()

        paddle.move(keys)
        paddle.update()
        ball.update()

        _handle_ball_vs_bricks(ball, bricks, bonuses)

        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            _handle_ball_vs_paddle(ball, paddle)

        # Update and check power-up collections
        for bonus in bonuses[:]:
            bonus.update()
            if paddle.rect.colliderect(bonus.rect):
                ApplyBonus(bonus, paddle, ball)
                bonuses.remove(bonus)
            elif bonus.rect.top > cfg.HEIGHT:
                bonuses.remove(bonus)

        # Draw Section
        for brick in bricks:
            brick.draw(screen)

        for bonus in bonuses:
            bonus.draw(screen, font)

        paddle.draw(screen)
        ball.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()