# your_app/management/commands/import_data.py

import json
import os
from django.core.management.base import BaseCommand
# 引入所有需要的模型
from test0621.models import (
    Planet, GameType, Character, Chapter, Dialogue, Question, FullStory
)

class Command(BaseCommand):
    help = 'Imports game data from a specified JSON file that matches the final format.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The path to the JSON file.')
        parser.add_argument(
            '--clear', action='store_true', help='Clear existing game content data before importing.'
        )

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File "{json_file_path}" does not exist.'))
            return

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing game content data...'))
            # 刪除順序：從子模型到父模型
            Question.objects.all().delete()
            Dialogue.objects.all().delete()
            FullStory.objects.all().delete()
            Chapter.objects.all().delete()
            Character.objects.all().delete()
            GameType.objects.all().delete()
            Planet.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Game content data cleared.'))

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write('Starting data import...')

        # 1. 建立星球
        planet, _ = Planet.objects.get_or_create(planet_name=data['planet_name'])
        self.stdout.write(f'Planet "{planet.planet_name}" processed.')

        # 2. 建立所有遊戲類型
        game_type_objects = {}
        for gt_data in data.get('game_types', []):
            gt, created = GameType.objects.get_or_create(
                name=gt_data['name'], 
                defaults={
                    'description': gt_data.get('description'),
                    'background_image': gt_data.get('background_img') # JSON 'background_img' -> model 'background_image'
                }
            )
            game_type_objects[gt.name] = gt
            if created: self.stdout.write(f'  GameType "{gt.name}" created.')

        # 3. 建立所有角色
        character_objects = {}
        for char_data in data.get('characters', []):
            char, created = Character.objects.get_or_create(
                name=char_data['name'], 
                defaults={
                    'intro': char_data.get('intro'),
                    'character_avatar': char_data.get('character_avatar'),
                    'character_sprite': char_data.get('character_img') # JSON 'character_img' -> model 'character_sprite'
                }
            )
            character_objects[char.name] = char
            if created: self.stdout.write(f'  Character "{char.name}" created.')
        character_objects[None] = None # 處理對話中角色為 null 的情況

        # 4. 遍歷故事，建立章節、對話、問題、完整故事
        for story_data in data.get('stories', []):
            game_type_name = story_data.get('game_type')
            game_type_obj = game_type_objects.get(game_type_name)
            if not game_type_obj:
                self.stdout.write(self.style.ERROR(f"GameType '{game_type_name}' not found. Skipping chapter '{story_data['title']}'."))
                continue
            
            # 建立章節
            chapter, created = Chapter.objects.get_or_create(
                planet=planet,
                chapter_number=story_data['chapter_num'], # JSON 'chapter_num' -> model 'chapter_number'
                defaults={
                    'title': story_data['title'],
                    'game_type': game_type_obj,
                    'description': story_data.get('description'),
                    'background_image': story_data.get('novel_bg'), # JSON 'novel_bg' -> model 'background_image'
                    'bg_music': story_data.get('novel_music'), # JSON 'novel_music' -> model 'bg_music'
                }
            )
            if created: self.stdout.write(f'  Chapter "{chapter.title}" created.')

            # 建立對話
            for dialogue_data in story_data.get('dialogues', []):
                Dialogue.objects.create(
                    chapter=chapter,
                    sequence=dialogue_data['sequence'],
                    speaker=character_objects[dialogue_data['speaker']],
                    character_on_left=character_objects[dialogue_data.get('character_left')], # JSON 'character_left' -> model 'character_on_left'
                    character_on_right=character_objects[dialogue_data.get('character_right')], # JSON 'character_right' -> model 'character_on_right'
                    text=dialogue_data['text'],
                    voice_file=dialogue_data.get('voice'), # JSON 'voice' -> model 'voice_file'
                    background_image=dialogue_data.get('bg_img'), # JSON 'bg_img' -> model 'background_image'
                    bg_music=dialogue_data.get('bg_music'),
                )
            
            # 建立問題
            for question_data in story_data.get('questions', []):
                Question.objects.create(
                    chapter=chapter,
                    difficulty=question_data['difficulty'],
                    question_text=question_data['question_text'],
                    options=question_data['options'],
                    correct_answer=question_data['answer'], # JSON 'answer' -> model 'correct_answer'
                    enemy_image=question_data.get('enemy_img'), # JSON 'enemy_img' -> model 'enemy_image'
                    player_image=question_data.get('player_img'), # JSON 'player_img' -> model 'player_image'
                )
            
            # 建立完整故事
            full_story_data = story_data.get('full_story')
            if full_story_data:
                fs, created = FullStory.objects.get_or_create(chapter=chapter, defaults={'planet': planet})
                fs.introduction = full_story_data.get('introduction', '')
                fs.full_text = full_story_data.get('full_text', '')
                character_names = full_story_data.get('character_names', [])
                characters_to_add = [character_objects[name] for name in character_names if name in character_objects]
                fs.characters.set(characters_to_add)
                fs.save()

        self.stdout.write(self.style.SUCCESS('Data import finished successfully!'))