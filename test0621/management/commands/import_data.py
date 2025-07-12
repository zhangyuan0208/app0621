import json
import os
from django.core.management.base import BaseCommand
from test0621 import Planet, Chapter, Character, Dialogue, Question

class Command(BaseCommand):
    help = 'Imports story data from a specified JSON file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The path to the JSON file to import.')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing.',
        )

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File "{json_file_path}" does not exist.'))
            return

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Question.objects.all().delete()
            Dialogue.objects.all().delete()
            Character.objects.all().delete()
            Chapter.objects.all().delete()
            Planet.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write('Starting data import...')

        # 1. 建立星球 (Planet)
        # 【已優化】優先使用 'planet_name' 欄位，如果沒有則使用 'theme'
        planet_name = data.get('planet_name') or data.get('theme', '預設星球')
        planet, created = Planet.objects.get_or_create(
            planet_name=planet_name
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Planet "{planet.planet_name}" created.'))

        # 2. 預處理並建立所有角色 (Character)
        characters_data = {}
        for story in data.get('stories', []):
            for dialogue in story.get('dialogues', []):
                char_name = dialogue.get('character')
                if char_name and char_name not in characters_data:
                    characters_data[char_name] = {
                        'name': char_name,
                        'intro': dialogue.get('intro'),
                        'character_avatar': dialogue.get('avatar', ''),
                        'image_left': dialogue.get('image1'),
                        'image_right': dialogue.get('image2'),
                    }
        
        character_objects = {}
        for name, char_data in characters_data.items():
            character, created = Character.objects.get_or_create(
                name=name,
                defaults=char_data
            )
            character_objects[name] = character
            if created:
                self.stdout.write(f'  Character "{name}" created.')

        # 3. 遍歷故事並建立章節、對話和問題
        for story in data.get('stories', []):
            chapter, created = Chapter.objects.get_or_create(
                planet=planet,
                chapter_number=story.get('chapter'),
                defaults={
                    'title': story.get('title'),
                    'description': story.get('description'),
                    'bg_music': story.get('music'),
                    'background_image': 'chapters/default_bg.jpg'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Chapter "{chapter.title}" ({chapter.chapter_number}) created.'))

            # 建立對話
            for dialogue_data in story.get('dialogues', []):
                char_name = dialogue_data.get('character')
                if not char_name or char_name not in character_objects:
                    continue
                
                character = character_objects.get(char_name)
                Dialogue.objects.create(
                    chapter=chapter,
                    character=character,
                    sequence=dialogue_data.get('sequence'),
                    text=dialogue_data.get('text'),
                    voice_file=dialogue_data.get('voice'),
                    background_image=dialogue_data.get('background')
                )
            self.stdout.write(f'  - Imported {len(story.get("dialogues", []))} dialogues for chapter "{chapter.title}".')

            # 建立問題
            quiz_data = story.get('quiz', {})
            player_info = story.get('player', {})
            enemy_info = story.get('enemy', {})
            question_count = 0
            
            for difficulty, questions in quiz_data.items():
                for q_data in questions:
                    Question.objects.create(
                        chapter=chapter,
                        difficulty=difficulty,
                        question_text=q_data.get('question'),
                        options=q_data.get('options'),
                        correct_answer=q_data.get('correct_answer'), # JSON 格式修正後，此處為 'answer'
                        player_image=player_info.get('image'),
                        enemy_image=enemy_info.get('image'),
                        background=enemy_info.get('background')
                    )
                    question_count += 1
            self.stdout.write(f'  - Imported {question_count} questions for chapter "{chapter.title}".')

        self.stdout.write(self.style.SUCCESS('Data import finished successfully!'))