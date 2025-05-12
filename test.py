import pygame
pygame.init()

screen = pygame.display.set_mode((1024,786))
clock = pygame.time.Clock()


# surf = pygame.Surface((200,200))
# rect = surf.get_rect(center=(400,400))
# surf.fill((200,200,200))
pos = (400,400)
isrunning = True
while isrunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isrunning = False
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
    
    pygame.draw.circle(screen,(255,255,100),pos,7)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()