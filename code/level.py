import pygame
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile, Crate, Coin, Heart, Liquid, Flag
from enemy import Enemy
from decoration import Sky, Clouds
from player import Player
from particles import ParticleEffect
from game_data import levels


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # audio
        self.coin_sound = pygame.mixer.Sound('../audio/effects/coin.wav')
        self.stomp_sound = pygame.mixer.Sound('../audio/effects/stomp.wav')

        # overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # user interface
        self.change_coins = change_coins
        self.change_health = change_health

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # explosion particles
        self.explosion_sprites = pygame.sprite.Group()

        # terrain setup
        terrain_forest_layout = import_csv_layout(level_data['terrain_forest'])
        self.terrain_forest_sprites = self.create_tile_group(terrain_forest_layout, 'terrain_forest')

        terrain_snow_layout = import_csv_layout(level_data['terrain_snow'])
        self.terrain_snow_sprites = self.create_tile_group(terrain_snow_layout, 'terrain_snow')

        terrain_lava_layout = import_csv_layout(level_data['terrain_lava'])
        self.terrain_lava_sprites = self.create_tile_group(terrain_lava_layout, 'terrain_lava')

        # grass setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # crates
        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crates')

        # coins
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # hearts
        heart_layout = import_csv_layout(level_data['hearts'])
        self.heart_sprites = self.create_tile_group(heart_layout, 'hearts')

        # liquids
        liquid_layout = import_csv_layout(level_data['liquids'])
        self.liquid_sprites = self.create_tile_group(liquid_layout, 'liquids')

        # ladder
        ladder_layout = import_csv_layout(level_data['ladder'])
        self.ladder_sprites = self.create_tile_group(ladder_layout, 'ladder')

        # enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraint')

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_forest_layout[0]) * tile_size
        self.clouds = Clouds(400, level_width, 30)

        # sky type
        self.forest = False
        self.snow = False
        self.lava = False

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain_forest':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/Tileset_Forest.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)

                    if type == 'terrain_snow':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/Tileset_Snow.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)

                    if type == 'terrain_lava':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/Tileset_Lava.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)

                    if type == 'ladder':
                        ladder_tile_list = import_cut_graphics('../graphics/ladder/ladder.png')
                        tile_surface = ladder_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('../graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)

                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)
                        sprite_group.add(sprite)

                    if type == 'liquids' and val == '1':
                        sprite = Liquid(tile_size, x, y, '../graphics/liquids/Animated_Lava', -24)
                        sprite_group.add(sprite)

                    if type == 'liquids' and val == '0':
                        sprite = Liquid(tile_size, x, y, '../graphics/liquids/Static_Lava', 0)
                        sprite_group.add(sprite)

                    if type == 'liquids' and val == '2':
                        sprite = Liquid(tile_size, x, y, '../graphics/liquids/Animated_Water', -10)
                        sprite_group.add(sprite)

                    if type == 'liquids' and val == '3':
                        sprite = Liquid(tile_size, x, y, '../graphics/liquids/Static_Water', 0)
                        sprite_group.add(sprite)

                    if type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size, x, y, '../graphics/coins/gold', 5)
                        if val == '1':
                            sprite = Coin(tile_size, x, y, '../graphics/coins/silver', 1)
                        sprite_group.add(sprite)

                    if type == 'hearts':
                        sprite = Heart(tile_size, x, y, '../graphics/hearts/hearts', 10)
                        sprite_group.add(sprite)

                    if type == 'enemies':
                        global enemy_type
                        if val == '0':
                            sprite = Enemy(tile_size, x, y, '../graphics/enemy/run/snow')
                            enemy_type = 2
                            sprite_group.add(sprite)
                        if val == '1':
                            sprite = Enemy(tile_size, x, y, '../graphics/enemy/run/forest')
                            enemy_type = 1
                            sprite_group.add(sprite)
                        if val == '2':
                            sprite = Enemy(tile_size, x, y, '../graphics/enemy/run/lava')
                            enemy_type = 3
                            sprite_group.add(sprite)

                    if type == 'constraint':
                        sprite = Tile(tile_size, x, y)
                        sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health)
                    self.player.add(sprite)
                if val == '1':
                    sprite = Flag(tile_size,x,y)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_forest_sprites.sprites() + self.terrain_snow_sprites.sprites() + \
                             self.terrain_lava_sprites.sprites() + self.crate_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        forest = self.terrain_forest_sprites
        snow = self.terrain_snow_sprites
        lava = self.terrain_lava_sprites
        crate = self.crate_sprites
        liquid_collision = self.liquid_sprites.sprites()

        for sprite in forest:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    self.snow = False
                    self.forest = True
                    self.lava = False
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        for sprite in snow:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    self.forest = False
                    self.snow = True
                    self.lava = False
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

            for sprite in crate:
                if sprite.rect.colliderect(player.collision_rect):
                    if player.direction.y > 0:
                        player.collision_rect.bottom = sprite.rect.top
                        player.direction.y = 0
                        player.on_ground = True
                    elif player.direction.y < 0:
                        player.collision_rect.top = sprite.rect.bottom
                        player.direction.y = 0
                        player.on_ceiling = True

        for sprite in lava:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    self.forest = False
                    self.snow = False
                    self.lava = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        for sprite in liquid_collision:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.get_damage(-100)

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            self.coin_sound.play()
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_heart_collisions(self):
        collided_hearts = pygame.sprite.spritecollide(self.player.sprite, self.heart_sprites, False)
        if collided_hearts:
            for heart in collided_hearts:
                self.change_health(heart.value)
                heart.kill()

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.stomp_sound.play()
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    if enemy_type == 1:
                        self.player.sprite.get_damage(-20)
                    if enemy_type == 2:
                        self.player.sprite.get_damage(-10)
                    if enemy_type == 3:
                        self.player.sprite.get_damage(-30)

    def check_ladder_collisions(self):
        ladder_collision = pygame.sprite.spritecollide(self.player.sprite, self.ladder_sprites, False)
        keys = pygame.key.get_pressed()

        if ladder_collision:
            if keys[pygame.K_UP] or keys[ord('w')]:
                self.player.sprite.direction.y = -5

    def run(self):
        if self.forest:
            self.sky.draw_forest(self.display_surface)
            self.clouds.draw(self.display_surface, self.world_shift)

        if self.snow:
            self.sky.draw_snow(self.display_surface)
            self.clouds.draw(self.display_surface, self.world_shift)

        if self.lava:
            self.sky.draw_lava(self.display_surface)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # liquids
        self.liquid_sprites.update(self.world_shift)
        self.liquid_sprites.draw(self.display_surface)

        # terrain
        self.terrain_forest_sprites.update(self.world_shift)
        self.terrain_forest_sprites.draw(self.display_surface)

        self.terrain_snow_sprites.update(self.world_shift)
        self.terrain_snow_sprites.draw(self.display_surface)

        self.terrain_lava_sprites.update(self.world_shift)
        self.terrain_lava_sprites.draw(self.display_surface)

        # ladder
        self.ladder_sprites.update(self.world_shift)
        self.ladder_sprites.draw(self.display_surface)

        # enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        # crate
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        # grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        # coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # hearts
        self.heart_sprites.update(self.world_shift)
        self.heart_sprites.draw(self.display_surface)

        # player sprites
        self.player.update()
        self.horizontal_movement_collision()

        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()

        self.check_coin_collisions()
        self.check_heart_collisions()
        self.check_enemy_collisions()
        self.check_ladder_collisions()
