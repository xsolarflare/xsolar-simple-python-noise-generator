import pygame
import numpy as np
from math import *
import os

pygame.init()

class DisplayN:
    def __init__(self):
        self 
    @staticmethod
    def bw(matrix, depth):
        step = 256 // depth 
        normalized = [[(n // step) * step for n in row] for row in matrix]
        normalized = [[min(255, val) for val in row] for row in normalized]
        return normalized
    
    @staticmethod
    def value_to_heatmap(val, min_val, max_val):
        if max_val > min_val:
            normalized = (val - min_val) / (max_val - min_val) * 255
        else:
            normalized = val

        normalized = max(0, min(255, normalized))

        t = normalized / 255.0

        r = min(255, int(normalized * 1.5))
        g = min(255, int(normalized * 0.3))
        b = min(255, int((255 - normalized) * 1.2))

        if t > 0.7:
            r = 255
            g = min(255, int(255 * ((t - 0.7) / 0.3)))
            b = min(255, int(b * (1 - (t - 0.7) / 0.3)))

        return (int(r), int(g), int(b))
    
    @staticmethod
    def extremum(val, min_val, max_val, percent=20):
        
        range = max_val - min_val
        prox = range/100
        epsilon = percent/5

        if val >= (max_val - prox*percent) and val < (max_val - prox*epsilon):
            r, g, b = 10, 180, 0
        elif val >= (max_val - prox*epsilon):
            r, g, b = 115, 255, 0
        elif val <= (min_val + prox*percent) and val > (min_val + prox*epsilon):
            r, g, b = 98, 0, 115
        elif val <= (min_val + prox*epsilon):
            r, g, b = 165, 0, 194
        else: 
            r, g, b = val/4, val/3.5, val/3

        return (int(r), int(g), int(b))


class WhiteNoise:
    caption = "White Noise"
    def __init__(self, name="Олег"):
        self.name = name
        
    def generate(self, seed, size_x, size_y):
        
        M = np.zeros((size_x, size_y))
        s = np.random.default_rng(seed)
        for x in range(size_x):
            for y in range(size_y):
                M[x][y] = s.integers(0, 256)
        return M
    
class AverageWhiteNoise:
    caption_rand = "Random Average White Noise"
    caption_ord = "Ordered Average White Noise"

    def __init__(self, name="Квазимир", iterations=1):
        self.name = name
        self.iterations = iterations
    
    def _apply_average(self, M, x, y):
        rows, cols = M.shape
        neighbors = []

        if x > 0:
            neighbors.append(M[x-1][y])
        else:
            neighbors.append(M[x+1][y])
            
        if x < rows - 1:
            neighbors.append(M[x+1][y])
        else:
            neighbors.append(M[x-1][y])
            
        if y > 0:
            neighbors.append(M[x][y-1])
        else:
            neighbors.append(M[x][y+1])
            
        if y < cols - 1:
            neighbors.append(M[x][y+1])
        else:
            neighbors.append(M[x][y-1])
        
        return sum(neighbors) // 4
    
    def generate_random(self, seed, size_x, size_y):
        s = np.random.default_rng(seed)
        M = whitenoise.generate(seed, size_x, size_y)
        
        total_ops = self.iterations * size_x * size_y * 10
        for i in range(total_ops):
            x = s.integers(0, size_x)
            y = s.integers(0, size_y)
            M[x][y] = self._apply_average(M, x, y)
        
        return M
    
    def generate_ordered(self, seed, size_x, size_y):
        s = np.random.default_rng(seed)
        M = whitenoise.generate(seed, size_x, size_y)
    
        for i in range(self.iterations):
            for x in range(size_x):
                for y in range(size_y):
                    M[x][y] = self._apply_average(M, x, y)
        return M


SCREEN_X = 640
SCREEN_Y = 640
PPP = 20 #Pixel Per Pixel 
Px_X = SCREEN_X // PPP #Pixels X
Px_Y = SCREEN_Y // PPP #Pixels Y
zoom = 0

icon = pygame.Surface((32, 32))
icon.fill((0, 0, 0, 0))
icon.set_colorkey((0, 0, 0))
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
pygame.display.set_caption("")

seed = 1
c_depth = 256
percentage = 20
iterations = 1
whitenoise = WhiteNoise()
averagewhitenoise = AverageWhiteNoise()
NOISETYPE = 0
style = "bw"

def extremum_caption(val, row, col):
    center_x = row * PPP + PPP // 2
    center_y = col * PPP + PPP // 2

    if zoom == -1: size_coef = 2 
    else: size_coef = 1

    rad = pi/4

    WHITE = (255, 255, 255)
    pygame.draw.circle(screen, WHITE, (center_x, center_y), 3*size_coef)
    length = 20*size_coef
    angle = rad
    dx = length * cos(angle)
    dy = length * sin(angle)
    end_x = center_x + dx
    end_y = center_y + dy
    pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), int(2*size_coef))
    font = pygame.font.Font(None, int(24*size_coef))
    text_surface = font.render(str(int(val)), True, WHITE)
    text_x, text_y = end_x + 5*size_coef, end_y - 5*size_coef
    screen.blit(text_surface, (text_x, text_y))



def draw():
    averagewhitenoise.iterations = iterations
    
    match NOISETYPE:
         case 0: Matrix = whitenoise.generate(seed, Px_X, Px_Y)
         case 1: Matrix = averagewhitenoise.generate_random(seed, Px_X, Px_Y)
         case 2: Matrix = averagewhitenoise.generate_ordered(seed, Px_X, Px_Y)
         case _: Matrix = np.zeros((Px_X, Px_Y))
    
    match style:
         case "bw": 
            Matrix = DisplayN.bw(Matrix, c_depth)
            
            for x in range(Px_X):
                for y in range(Px_Y):
                    color = Matrix[x][y]
                    pygame.draw.rect(screen, (color, color, color),
                                    (x * PPP, y * PPP, PPP, PPP))
                    
         case "heatmap":
            min, max = np.min(Matrix), np.max(Matrix) 
            for x in range(Px_X):
                for y in range(Px_Y):
                    r, g, b = DisplayN.value_to_heatmap(Matrix[x][y], min, max)
                    pygame.draw.rect(screen, (r, g, b),
                                    (x * PPP, y * PPP, PPP, PPP))
                    
         case "extremum":
            min, max = np.min(Matrix), np.max(Matrix) 
            for x in range(Px_X):
                for y in range(Px_Y):
                    r, g, b = DisplayN.extremum(Matrix[x][y], min, max, percent=percentage)
                    pygame.draw.rect(screen, (r, g, b),
                                    (x * PPP, y * PPP, PPP, PPP))
            
            row, col = np.unravel_index(np.argmin(Matrix), Matrix.shape)
            extremum_caption(min, row, col)
            row, col = np.unravel_index(np.argmax(Matrix), Matrix.shape)
            extremum_caption(max, row, col)
            

    
    
    return np.mean(Matrix)
    
font = pygame.font.Font(None, 28)

draw()
pygame.display.flip()

clock = pygame.time.Clock()

while True:
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            
            updated = False

            ### ПРИБЛИЖЕНИЕ
            if event.key == pygame.K_UP:
                if PPP > 2 and zoom < 2:
                    Px_X *= 2
                    Px_Y *= 2
                    PPP //= 2
                    zoom += 1
                    updated = True
            
            elif event.key == pygame.K_DOWN:
                if PPP > 2 and zoom > -1:
                    Px_X //= 2
                    Px_Y //= 2
                    PPP *= 2
                    zoom -= 1
                    updated = True
            
            ### СМЕНА СИДА
            elif event.key == pygame.K_RIGHT:
                seed += 1
                updated = True
            
            elif event.key == pygame.K_LEFT:
                if seed != 0:
                    seed -= 1
                    updated = True
            
            ### ГЛУБИНА ЦВЕТА
            elif event.key == pygame.K_PERIOD:
                if c_depth < 256 and style == "bw":
                    c_depth *= 2
                if percentage < 50 and style == "extremum":
                    percentage += 1
                updated = True
            
            elif event.key == pygame.K_COMMA:
                if c_depth > 2 and style == "bw":
                    c_depth //= 2
                if percentage > 1 and style == "extremum":
                    percentage -= 1
                updated = True

            
            ### ТИПЫ ШУМА
            elif event.key == pygame.K_1:
                NOISETYPE = 0
                updated = True
            
            elif event.key == pygame.K_2:
                NOISETYPE = 1
                updated = True
            
            elif event.key == pygame.K_3:
                NOISETYPE = 2
                updated = True

            ### CТИЛИ
            elif event.key == pygame.K_h:
                if style == "bw" or style == "extremum": style = "heatmap"
                else: style = "bw"
                updated = True 
            
            elif event.key == pygame.K_j:
                if style == "bw" or style == "heatmap": style = "extremum"
                else: style = "bw"
                updated = True 
            
            ### ИТЕРАЦИИ
            elif event.key == pygame.K_m:
                if iterations != 7:
                    iterations += 1
                    updated = True
            
            elif event.key == pygame.K_n:
                if iterations != 1:
                    iterations -= 1
                    updated = True
            
            ### ВЫВОД ДАННЫХ
            elif event.key == pygame.K_d:
                print("="*10)
                match NOISETYPE:
                    case 0: print(WhiteNoise.caption)
                    case 1: print(AverageWhiteNoise.caption_rand, "\n" + f"iterations {iterations}")
                    case 2: print(AverageWhiteNoise.caption_ord, "\n" + f"iterations {iterations}")
                    case _: print("?")
                
                print(f"seed {seed}")
                print(f"scale {zoom}")
                if style == "bw": print(f"depth {c_depth}")
                if style == "extremum": print(f"percentage {percentage}")
                print(f"style {style}")

            ### СОХРАНЕНИЕ СКРИНШОТА
            elif event.key == pygame.K_s:
                desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
                filename = os.path.join(desktop, f"{style}SEED{seed}TYPE{NOISETYPE}I{iterations}Z{zoom}.png")
                pygame.image.save(screen, filename)
                print("Скриншот сохранен на рабочий стол")

            if updated:
                draw()
                pygame.display.flip()
