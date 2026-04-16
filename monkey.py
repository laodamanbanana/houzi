import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = -13
DOUBLE_JUMP_FORCE = -11
MOVE_SPEED = 6
DASH_SPEED = 18
DASH_DURATION = 10
DASH_COOLDOWN = 45
ATTACK_DURATION = 15
ATTACK_COOLDOWN = 20
INVINCIBILITY_FRAMES = 60

# 颜色定义
SKY_BLUE = (135, 206, 235)
DARK_RED = (74, 14, 14)
BROWN = (101, 67, 33)
SAND = (230, 194, 128)
LAVA = (255, 69, 0)
GRASS = (34, 139, 34)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (75, 0, 130)
GRAY = (128, 128, 128)

# 设置窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("悟空：成佛之路 (Python/Pygame)")
clock = pygame.time.Clock()

# 尝试获取支持中文的字体
def get_font(size):
    import os
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except Exception:
                pass
    return pygame.font.Font(None, size)

font_large = get_font(36)
font_small = get_font(24)

class Assets:
    loaded = False
    characters = []
    enemies = {}
    items = {}
    backgrounds = []
    sounds = {}
    item_images = {}

    @classmethod
    def init(cls):
        if cls.loaded: 
            return
        try:
            import os
            def load_single(path, target_size):
                if not os.path.exists(path): 
                    return None
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, target_size)

            def create_item_image(color, shape, size=(30, 30)):
                surf = pygame.Surface(size, pygame.SRCALPHA)
                if shape == 'circle':
                    pygame.draw.circle(surf, color, (size[0]//2, size[1]//2), size[0]//2 - 2)
                elif shape == 'diamond':
                    pts = [(size[0]//2, 2), (size[0]-2, size[1]//2), (size[0]//2, size[1]-2), (2, size[1]//2)]
                    pygame.draw.polygon(surf, color, pts)
                elif shape == 'star':
                    cx, cy = size[0]//2, size[1]//2
                    r = size[0]//2 - 2
                    pts = []
                    for i in range(10):
                        angle = i * 3.14159 / 5 - 3.14159 / 2
                        rr = r if i % 2 == 0 else r // 2
                        pts.append((cx + rr * math.cos(angle), cy + rr * math.sin(angle)))
                    pygame.draw.polygon(surf, color, pts)
                elif shape == 'heart':
                    w, h = size
                    pygame.draw.ellipse(surf, color, (2, h//4, w//2-2, h//2))
                    pygame.draw.ellipse(surf, color, (w//2, h//4, w//2-2, h//2))
                    pygame.draw.polygon(surf, color, [(w//4, h//2), (w*3//4, h//2), (w//2, h-2)])
                elif shape == 'box':
                    pygame.draw.rect(surf, color, (2, 2, size[0]-4, size[1]-4), border_radius=4)
                elif shape == 'pill':
                    pygame.draw.rect(surf, color, (size[0]//4, 2, size[0]//2, size[1]-4), border_radius=size[0]//4)
                return surf

            import math
            cls.item_images = {
                'jingu': create_item_image((255, 215, 0), 'diamond'),
                'document': create_item_image((255, 255, 255), 'box'),
                'fan': create_item_image((255, 100, 100), 'pill'),
                'heart': create_item_image((255, 50, 50), 'heart'),
                'star': create_item_image((255, 255, 0), 'star'),
                'coin': create_item_image((255, 215, 0), 'circle'),
                'gem': create_item_image((0, 255, 255), 'diamond'),
                'shield': create_item_image((100, 100, 255), 'circle'),
                'speed': create_item_image((0, 255, 0), 'star'),
                'magic': create_item_image((200, 0, 200), 'star'),
            }

            cls.characters = [
                [
                    load_single('assets/spr_monkey_walk_0.png', (40, 40)),
                    load_single('assets/spr_monkey_walk_1.png', (40, 40)),
                    load_single('assets/spr_monkey_walk_2.png', (40, 40)),
                    load_single('assets/spr_monkey_walk_3.png', (40, 40))
                ],
                [
                    load_single('assets/spr_monkey_king_walk_0.png', (40, 40)),
                    load_single('assets/spr_monkey_king_walk_1.png', (40, 40)),
                    load_single('assets/spr_monkey_king_walk_2.png', (40, 40)),
                    load_single('assets/spr_monkey_king_walk_3.png', (40, 40))
                ],
                [
                    load_single('assets/buddha_walk_0.png', (40, 40)),
                    load_single('assets/buddha_walk_1.png', (40, 40)),
                    load_single('assets/buddha_walk_2.png', (40, 40)),
                    load_single('assets/buddha_walk_3.png', (40, 40))
                ]
            ]
            
            cls.enemies['bear'] = load_single('assets/enemy_0.png', (50, 50))
            cls.enemies['sha_illusion'] = load_single('assets/enemy_1.png', (40, 50))
            cls.enemies['bull_demon'] = load_single('assets/enemy_2.png', (100, 150))
            cls.enemies['rolling_stone'] = load_single('assets/enemy_3.png', (40, 40))

            # 保留并优化三层关卡的背景素材的等比缩放，避免拉伸问题
            def load_slice(path, cols, rows, target_size=None, colorkey_pos=(0,0)):
                if not os.path.exists(path): 
                    return []
                sheet = pygame.image.load(path).convert_alpha()
                w, h = sheet.get_width() // cols, sheet.get_height() // rows
                slices = []
                for y in range(rows):
                    for x in range(cols):
                        rect = pygame.Rect(x * w, y * h, w, h)
                        sub = sheet.subsurface(rect).copy()
                        slices.append(sub)
                return slices
            
            bgs = load_slice('assets/backgrounds.png', 1, 3)
            scaled_bgs = []
            for bg in bgs:
                scale = max(800 / bg.get_width(), 600 / bg.get_height())
                new_w = int(bg.get_width() * scale)
                new_h = int(bg.get_height() * scale)
                scaled = pygame.transform.scale(bg, (new_w, new_h))
                scaled_bgs.append(scaled)
            cls.backgrounds = scaled_bgs
            
            try:
                pygame.mixer.init()
                sound_names = ['jump', 'hit', 'item', 'dash', 'evolve', 'hurt']
                for name in sound_names:
                    path = f'assets/audio/{name}.wav'
                    if os.path.exists(path):
                        cls.sounds[name] = pygame.mixer.Sound(path)
                
                if os.path.exists('assets/audio/bgm.wav'):
                    pygame.mixer.music.load('assets/audio/bgm.wav')
                    pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"音频加载失败: {e}")
                
            cls.loaded = True
        except Exception as e:
            print(f"加载素材失败: {e}")

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vx = 0
        self.vy = 0
        self.form = 0
        self.max_hp = 3
        self.hp = 3
        self.score = 0
        self.facing_right = True
        self.is_grounded = False
        self.can_double_jump = False
        
        self.is_attacking = False
        self.attack_timer = 0
        
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        
        self.invincibility_timer = 0
        self.speed_boost_timer = 0

    def evolve(self, new_form):
        self.form = new_form
        if self.form == 1:
            self.max_hp = 5
        elif self.form == 2:
            self.max_hp = 7
        self.hp = self.max_hp

    def update(self, keys, platforms):
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer < ATTACK_COOLDOWN - ATTACK_DURATION:
                self.is_attacking = False
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1

        left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.vx = DASH_SPEED if self.facing_right else -DASH_SPEED
            self.vy = 0
            if self.dash_timer == 0:
                self.is_dashing = False
        else:
            speed = MOVE_SPEED
            if self.speed_boost_timer > 0:
                speed *= 1.5
            in_quicksand = any(p.colliderect(self.rect) and p_type == 'quicksand' for p, p_type in platforms)
            if in_quicksand:
                speed *= 0.4

            target_vx = 0
            if left_pressed:
                target_vx = -speed
                self.facing_right = False
            if right_pressed:
                target_vx = speed
                self.facing_right = True
            
            self.vx += (target_vx - self.vx) * 0.3

            self.vy += GRAVITY
            if in_quicksand and self.vy > 2:
                self.vy = 2

        # X轴碰撞
        self.rect.x += self.vx
        for p, p_type in platforms:
            if p_type == 'solid' and self.rect.colliderect(p):
                if self.vx > 0:
                    self.rect.right = p.left
                elif self.vx < 0:
                    self.rect.left = p.right
                self.vx = 0

        # Y轴碰撞
        self.rect.y += self.vy
        self.is_grounded = False
        for p, p_type in platforms:
            if p_type == 'solid' and self.rect.colliderect(p):
                if self.vy > 0:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.is_grounded = True
                elif self.vy < 0:
                    self.rect.top = p.bottom
                    self.vy = 0

    def jump(self):
        if self.is_grounded:
            self.vy = JUMP_FORCE
            self.is_grounded = False
            self.can_double_jump = True
            if 'jump' in Assets.sounds: 
                Assets.sounds['jump'].play()
        elif self.can_double_jump and self.form >= 1:
            self.vy = DOUBLE_JUMP_FORCE
            self.can_double_jump = False
            if 'jump' in Assets.sounds: 
                Assets.sounds['jump'].play()

    def attack(self):
        if self.form >= 1 and self.attack_timer <= 0:
            self.is_attacking = True
            self.attack_timer = ATTACK_COOLDOWN

    def dash(self):
        if self.form >= 2 and self.dash_cooldown <= 0:
            self.is_dashing = True
            self.dash_timer = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            self.invincibility_timer = DASH_DURATION
            if 'dash' in Assets.sounds: 
                Assets.sounds['dash'].play()

    def draw(self, surface, camera_x):
        if self.invincibility_timer % 10 > 5:
            return

        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y

        img = None
        valid_frames = []
        if Assets.characters and self.form < len(Assets.characters):
            frames = Assets.characters[self.form]
            valid_frames = [f for f in frames if f is not None]
            
            if valid_frames:
                is_walking = self.vx != 0 and self.is_grounded
                
                if is_walking and len(valid_frames) > 1:
                    frame_idx = (pygame.time.get_ticks() // 150) % len(valid_frames)
                    img = valid_frames[frame_idx]
                else:
                    img = valid_frames[0]
        
        if img is not None:
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            surface.blit(img, (draw_x, draw_y))
            return

        if self.form == 0:
            pygame.draw.rect(surface, (139, 69, 19), (draw_x, draw_y, self.rect.width, self.rect.height))
        elif self.form == 1:
            pygame.draw.rect(surface, GOLD, (draw_x, draw_y, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, RED, (draw_x, draw_y + 5, self.rect.width, 5))
        elif self.form == 2:
            pygame.draw.rect(surface, GOLD, (draw_x, draw_y, self.rect.width, self.rect.height))
            pygame.draw.circle(surface, GOLD, (draw_x + self.rect.width//2, draw_y + self.rect.height//2), 30, 2)

        # 绘制攻击
        if self.is_attacking:
            aw, ah = 60, 4
            ax = draw_x + self.rect.width if self.facing_right else draw_x - aw
            ay = draw_y + self.rect.height//2
            pygame.draw.line(surface, GOLD, (ax, ay), (ax + aw, ay), ah)

class Enemy:
    def __init__(self, x, y, w, h, e_type, hp, patrol_start=0, patrol_end=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.type = e_type
        self.hp = hp
        self.max_hp = hp
        self.vx = 2 if e_type == 'bear' else 0
        self.vy = 0
        self.patrol_start = patrol_start
        self.patrol_end = patrol_end
        self.facing_right = True
        self.attack_cooldown = 0
        self.dead = False

    def update(self, player, platforms):
        if self.dead: 
            return

        if self.type == 'bear':
            self.rect.x += self.vx
            if self.vx > 0 and self.rect.x > self.patrol_end:
                self.vx = -self.vx
            elif self.vx < 0 and self.rect.x < self.patrol_start:
                self.vx = -self.vx
        
        elif self.type == 'rolling_stone':
            self.rect.x -= 4
            self.vy += GRAVITY
            self.rect.y += self.vy
            for p, p_type in platforms:
                if p_type == 'solid' and self.rect.colliderect(p):
                    if self.vy > 0:
                        self.rect.bottom = p.top
                        self.vy = 0
            if self.rect.right < 0:
                self.dead = True
                
        elif self.type == 'sha_illusion':
            dist = player.rect.x - self.rect.x
            if abs(dist) < 300 and self.attack_cooldown <= 0:
                self.vx = 6 if dist > 0 else -6
                self.attack_cooldown = 120
            self.rect.x += self.vx
            self.vx *= 0.95
            if self.attack_cooldown > 0: self.attack_cooldown -= 1
            
        elif self.type == 'bull_demon':
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 150
                if random.random() > 0.5:
                    self.vx = -8
            self.rect.x += self.vx
            if self.rect.x < 1500: self.vx = 2
            if self.rect.x > 2200: self.vx = 0
            if self.attack_cooldown > 0: self.attack_cooldown -= 1

    def draw(self, surface, camera_x):
        if self.dead: 
            return
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        
        img = Assets.enemies.get(self.type) if hasattr(Assets, 'enemies') else None
        if img is not None:
            flip = (self.vx < 0) if self.type != 'bull_demon' else (self.vx > 0)
            if flip:
                img = pygame.transform.flip(img, True, False)
            surface.blit(img, (draw_x, draw_y))
            if self.type == 'bull_demon':
                pygame.draw.rect(surface, RED, (draw_x, draw_y - 15, self.rect.width * (self.hp / self.max_hp), 5))
            return

        if self.type == 'bear': color = BLACK
        elif self.type == 'rolling_stone': color = GRAY
        elif self.type == 'sha_illusion': color = PURPLE
        elif self.type == 'bull_demon': color = DARK_RED
        else: color = RED

        if self.type == 'rolling_stone':
            pygame.draw.circle(surface, color, (draw_x + self.rect.width//2, draw_y + self.rect.height//2), self.rect.width//2)
        else:
            pygame.draw.rect(surface, color, (draw_x, draw_y, self.rect.width, self.rect.height))

        if self.type == 'bull_demon':
            pygame.draw.rect(surface, RED, (draw_x, draw_y - 15, self.rect.width * (self.hp / self.max_hp), 5))

class Game:
    def __init__(self):
        self.level = 1
        self.player = Player(100, 300)
        self.camera_x = 0
        self.dialogue = None
        self.dialogue_timer = 0
        self.game_over = False
        self.game_won = False
        self.player.score = 0
        self.load_level(1)

    def load_level(self, level, keep_form=True):
        self.level = level
        self.platforms = []
        self.enemies = []
        self.items = []
        self.hazards = []
        self.level_width = 3000
        
        if not keep_form:
            self.player.form = 0
            self.player.max_hp = 3
            self.player.hp = 3
            
        self.player.rect.topleft = (100, 300)
        self.player.vx = 0
        self.player.vy = 0

        if level == 1:
            self.level_width = 3000
            self.platforms = [
                (pygame.Rect(0, 500, 3000, 100), 'solid'),
                (pygame.Rect(400, 400, 200, 20), 'solid'),
                (pygame.Rect(700, 300, 200, 20), 'solid'),
                (pygame.Rect(1100, 350, 200, 20), 'solid'),
                (pygame.Rect(1500, 250, 200, 20), 'solid'),
                (pygame.Rect(2000, 400, 300, 20), 'solid')
            ]
            self.enemies = [
                Enemy(800, 450, 50, 50, 'bear', 3, 600, 1000),
                Enemy(1600, 450, 50, 50, 'bear', 3, 1400, 1900),
                Enemy(1200, 460, 40, 40, 'rolling_stone', 1),
                Enemy(2200, 360, 40, 40, 'rolling_stone', 1)
            ]
            self.items = [
                {'rect': pygame.Rect(2800, 450, 30, 30), 'type': 'jingu', 'collected': False},
                {'rect': pygame.Rect(600, 400, 30, 30), 'type': 'heart', 'collected': False},
                {'rect': pygame.Rect(1200, 400, 30, 30), 'type': 'coin', 'collected': False},
                {'rect': pygame.Rect(1800, 350, 30, 30), 'type': 'star', 'collected': False},
            ]
            self.show_dialogue("小猴：我要踏上取经路，先闯过这黑风山！", 180)
            
        elif level == 2:
            self.level_width = 4000
            self.platforms = [
                (pygame.Rect(0, 500, 500, 100), 'solid'),
                (pygame.Rect(500, 500, 1000, 100), 'quicksand'),
                (pygame.Rect(1500, 500, 500, 100), 'solid'),
                (pygame.Rect(2000, 500, 1000, 100), 'quicksand'),
                (pygame.Rect(3000, 500, 1000, 100), 'solid'),
                (pygame.Rect(700, 350, 150, 20), 'solid'),
                (pygame.Rect(1000, 250, 150, 20), 'solid'),
                (pygame.Rect(1300, 350, 150, 20), 'solid'),
                (pygame.Rect(2200, 400, 100, 20), 'solid'),
                (pygame.Rect(2500, 300, 100, 20), 'solid'),
                (pygame.Rect(2800, 200, 100, 20), 'solid')
            ]
            self.enemies = [
                Enemy(1600, 450, 40, 50, 'sha_illusion', 5),
                Enemy(3200, 450, 40, 50, 'sha_illusion', 5)
            ]
            self.items = [
                {'rect': pygame.Rect(3800, 450, 30, 30), 'type': 'document', 'collected': False},
                {'rect': pygame.Rect(800, 400, 30, 30), 'type': 'gem', 'collected': False},
                {'rect': pygame.Rect(1500, 350, 30, 30), 'type': 'shield', 'collected': False},
                {'rect': pygame.Rect(2500, 400, 30, 30), 'type': 'speed', 'collected': False},
            ]
            self.show_dialogue("齐天大圣：俺老孙来也！这流沙河也拦不住我！", 180)
            
        elif level == 3:
            self.level_width = 2500
            self.platforms = [
                (pygame.Rect(0, 500, 400, 100), 'solid'),
                (pygame.Rect(400, 550, 1700, 50), 'lava'),
                (pygame.Rect(2100, 500, 400, 100), 'solid'),
                (pygame.Rect(500, 400, 100, 20), 'solid'),
                (pygame.Rect(800, 300, 100, 20), 'solid'),
                (pygame.Rect(1100, 400, 100, 20), 'solid'),
                (pygame.Rect(1400, 250, 100, 20), 'solid'),
                (pygame.Rect(1700, 350, 100, 20), 'solid'),
                (pygame.Rect(1900, 450, 100, 20), 'solid')
            ]
            self.hazards = [
                {'rect': pygame.Rect(600, 100, 40, 450), 'timer': 0, 'active': False},
                {'rect': pygame.Rect(1200, 100, 40, 450), 'timer': 60, 'active': False},
                {'rect': pygame.Rect(1800, 100, 40, 450), 'timer': 120, 'active': False}
            ]
            self.enemies = [Enemy(2200, 350, 100, 150, 'bull_demon', 20)]
            self.items = [
                {'rect': pygame.Rect(2400, 450, 30, 30), 'type': 'fan', 'collected': False},
                {'rect': pygame.Rect(600, 350, 30, 30), 'type': 'magic', 'collected': False},
                {'rect': pygame.Rect(1200, 400, 30, 30), 'type': 'gem', 'collected': False},
                {'rect': pygame.Rect(1800, 300, 30, 30), 'type': 'heart', 'collected': False},
            ]
            self.show_dialogue("斗战胜佛：历经磨难，终成正果。牛魔王，受死吧！", 180)

    def show_dialogue(self, text, duration):
        self.dialogue = text
        self.dialogue_timer = duration

    def update(self, keys):
        if self.game_over or self.game_won:
            if keys[pygame.K_r]:
                self.game_over = False
                self.game_won = False
                self.load_level(1, False)
            return

        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
            if self.dialogue_timer <= 0:
                self.dialogue = None

        self.player.update(keys, self.platforms)
        
        # 掉出屏幕
        if self.player.rect.y > HEIGHT + 200:
            self.player.hp = 0
            self.game_over = True
            self.show_dialogue("胜败乃兵家常事，按 R 键重新来过。", 9999)

        # 攻击判定
        if self.player.is_attacking:
            aw, ah = 60, 10
            ax = self.player.rect.right if self.player.facing_right else self.player.rect.left - aw
            ay = self.player.rect.centery - ah//2
            attack_rect = pygame.Rect(ax, ay, aw, ah)
            
            for enemy in self.enemies:
                if not enemy.dead and attack_rect.colliderect(enemy.rect):
                    enemy.hp -= 1
                    if 'hit' in Assets.sounds: 
                        Assets.sounds['hit'].play()
                    enemy.rect.x += 20 if self.player.facing_right else -20
                    if enemy.hp <= 0:
                        enemy.dead = True
                        if enemy.type == 'bull_demon':
                            self.show_dialogue("牛魔王：啊！我竟然败了...", 180)

        # 敌人更新与碰撞
        for enemy in self.enemies:
            enemy.update(self.player, self.platforms)
            if not enemy.dead and self.player.invincibility_timer <= 0 and self.player.rect.colliderect(enemy.rect):
                self.player.hp -= 1
                self.player.invincibility_timer = INVINCIBILITY_FRAMES
                if 'hurt' in Assets.sounds: 
                    Assets.sounds['hurt'].play()
                if self.player.hp <= 0:
                    self.game_over = True
                    self.show_dialogue("胜败乃兵家常事，按 R 键重新来过。", 9999)

        # 陷阱更新与碰撞
        for h in self.hazards:
            h['timer'] += 1
            if h['timer'] > 180:
                h['active'] = not h['active']
                h['timer'] = 0
            if h['active'] and self.player.invincibility_timer <= 0 and self.player.rect.colliderect(h['rect']):
                self.player.hp -= 1
                self.player.invincibility_timer = INVINCIBILITY_FRAMES
                if 'hurt' in Assets.sounds: 
                    Assets.sounds['hurt'].play()

        # 岩浆碰撞
        for p, p_type in self.platforms:
            if p_type == 'lava' and self.player.rect.colliderect(p) and self.player.invincibility_timer <= 0:
                self.player.hp -= 1
                self.player.vy = -10
                self.player.invincibility_timer = INVINCIBILITY_FRAMES
                if 'hurt' in Assets.sounds: 
                    Assets.sounds['hurt'].play()

        # 物品收集
        for item in self.items:
            if not item['collected'] and self.player.rect.colliderect(item['rect']):
                item['collected'] = True
                item_type = item['type']
                
                if item_type in ('jingu', 'document', 'fan'):
                    if 'evolve' in Assets.sounds: 
                        Assets.sounds['evolve'].play()
                
                if item_type == 'jingu':
                    self.player.evolve(1)
                    self.show_dialogue("获得金箍棒碎片！进化为齐天大圣！", 120)
                    self.load_level(2)
                elif item_type == 'document':
                    self.player.evolve(2)
                    self.show_dialogue("获得通关文牒！进化为斗战胜佛！", 120)
                    self.load_level(3)
                elif item_type == 'fan':
                    self.game_won = True
                    self.show_dialogue("取得芭蕉扇，成功抵达灵山！修成正果！按 R 键重玩", 9999)
                elif item_type == 'heart':
                    self.player.hp = min(self.player.hp + 1, self.player.max_hp)
                    self.show_dialogue("获得爱心！生命值 +1", 60)
                elif item_type == 'star':
                    self.player.score += 100
                    self.show_dialogue("获得星星！分数 +100", 60)
                elif item_type == 'coin':
                    self.player.score += 50
                    self.show_dialogue("获得金币！分数 +50", 60)
                elif item_type == 'gem':
                    self.player.score += 200
                    self.show_dialogue("获得宝石！分数 +200", 60)
                elif item_type == 'shield':
                    self.player.invincibility_timer = 180
                    self.show_dialogue("获得护盾！3秒无敌", 60)
                elif item_type == 'speed':
                    self.player.speed_boost_timer = 300
                    self.show_dialogue("获得速度提升！5秒内移动速度加快", 60)
                elif item_type == 'magic':
                    for enemy in self.enemies:
                        if not enemy.dead:
                            enemy.hp = 0
                            enemy.dead = True
                    self.show_dialogue("释放魔法！击败所有敌人", 60)

        # 摄像机跟随
        target_x = self.player.rect.x - WIDTH // 2
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_x = max(0, min(self.camera_x, self.level_width - WIDTH))

    def draw(self, surface):
        if Assets.backgrounds and self.level - 1 < len(Assets.backgrounds):
            surface.blit(Assets.backgrounds[self.level - 1], (0, 0))
        else:
            surface.fill(DARK_RED if self.level == 3 else SKY_BLUE)
        
        # 绘制平台
        for p, p_type in self.platforms:
            color = BROWN if p_type == 'solid' else SAND if p_type == 'quicksand' else LAVA
            pygame.draw.rect(surface, color, (p.x - self.camera_x, p.y, p.width, p.height))
            if p_type == 'solid':
                pygame.draw.rect(surface, GRASS, (p.x - self.camera_x, p.y, p.width, 10))

        # 绘制陷阱
        for h in self.hazards:
            if h['active']:
                pygame.draw.rect(surface, LAVA, (h['rect'].x - self.camera_x, h['rect'].y, h['rect'].width, h['rect'].height))
            else:
                pygame.draw.rect(surface, (255, 69, 0, 100), (h['rect'].x - self.camera_x, h['rect'].bottom - 20, h['rect'].width, 20))

        # 绘制物品
        for item in self.items:
            if not item['collected']:
                item_type = item['type']
                img = Assets.item_images.get(item_type)
                if img:
                    x = item['rect'].x - self.camera_x
                    y = item['rect'].y
                    surface.blit(img, (x, y))
                else:
                    pygame.draw.circle(surface, GOLD, (item['rect'].centerx - self.camera_x, item['rect'].centery), item['rect'].width//2)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(surface, self.camera_x)

        # 绘制玩家
        self.player.draw(surface, self.camera_x)

        # UI
        form_names = ["花果山小猴", "齐天大圣", "斗战胜佛"]
        level_names = ["黑风山", "流沙河", "火焰山"]
        
        ui_text = font_small.render(f"关卡 {self.level}: {level_names[self.level-1]} | 形态: {form_names[self.player.form]}", True, WHITE)
        surface.blit(ui_text, (10, 10))
        
        score_text = font_small.render(f"分数: {self.player.score}", True, GOLD)
        surface.blit(score_text, (10, 35))
        
        for i in range(self.player.max_hp):
            color = RED if i < self.player.hp else GRAY
            pygame.draw.circle(surface, color, (30 + i * 30, 60), 10)
        
        if self.player.speed_boost_timer > 0:
            speed_text = font_small.render("速度提升!", True, (0, 255, 0))
            surface.blit(speed_text, (10, 85))

        # 对话框
        if self.dialogue:
            dialogue_surf = font_large.render(self.dialogue, True, GOLD)
            bg_rect = dialogue_surf.get_rect(center=(WIDTH//2, HEIGHT - 50))
            pygame.draw.rect(surface, BLACK, bg_rect.inflate(20, 20))
            surface.blit(dialogue_surf, bg_rect)

        if self.game_over:
            over_surf = font_large.render("游戏结束 - 按 R 键重新开始", True, RED)
            surface.blit(over_surf, over_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))
        elif self.game_won:
            won_surf = font_large.render("修成正果！ - 按 R 键重新开始", True, GOLD)
            surface.blit(won_surf, won_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    Assets.init()
    game = Game()
    print(f"资源加载状态: {Assets.loaded}")
    print(f"角色帧数: {len(Assets.characters)}")
    if Assets.characters:
        print(f"第一形态帧数: {len(Assets.characters[0])}")
        print(f"有效帧: {[f is not None for f in Assets.characters[0]]}")
    
    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                    game.player.jump()
                if event.key == pygame.K_j:
                    game.player.attack()
                if event.key == pygame.K_k:
                    game.player.dash()
        
        if keys[pygame.K_j]:
            game.player.attack()
        if keys[pygame.K_k]:
            game.player.dash()

        game.update(keys)
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()