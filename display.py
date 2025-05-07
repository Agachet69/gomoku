import pygame

def init_game():
    pygame.init()
    screen = pygame.display.set_mode((400,400))

    run = True

    while run == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill("purple")

        pygame.display.flip()

    pygame.quit()

init_game() 