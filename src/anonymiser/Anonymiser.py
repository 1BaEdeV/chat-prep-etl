import json
import re
import sys
from pathlib import Path

import warnings
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

# Фикс для Python 3.12+ (pkg_resources)
try:
    import pkg_resources
except ImportError:
    try:
        from pip._vendor import pkg_resources

        sys.modules["pkg_resources"] = pkg_resources
    except ImportError:
        pass

from natasha import (
    Segmenter, MorphVocab, NewsEmbedding,
    NewsNERTagger, Doc
)


class TelegramAnonymizer:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)

        self.mapping = {}
        self.entities = {}
        self.counters = {"PER": 1, "LOC": 1, "ORG": 1, "PHONE": 1, "EMAIL": 1, "URL": 1, "USERID": 1}

    def __get_label(self, text, entity_type):
        if not text: return text
        key = (text.strip().lower(), entity_type)
        if key not in self.mapping:
            count = self.counters.get(entity_type, 1)
            self.mapping[key] = f"[{entity_type} {count}]"
            self.counters[entity_type] = count + 1
            self.entities[key[0]] = self.mapping[key]
        return self.mapping[key]

    def __regex_anonymize(self, text):
        """Очистка телефонов, почты и ссылок"""
        if not isinstance(text, str): return text

        # 1. Emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        text = re.sub(email_pattern, lambda m: self.__get_label(m.group(), "EMAIL"), text)

        # 2. URLs (http, https, t.me)
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|t\.me/[^\s<>"]+'
        text = re.sub(url_pattern, lambda m: self.__get_label(m.group(), "URL"), text)

        # 3. Телефоны
        phone_pattern = r'(?:\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}'
        text = re.sub(phone_pattern, lambda m: self.__get_label(m.group(), "PHONE"), text)

        # 4. User id
        id_pattern = r'user\d+'
        text = re.sub(id_pattern, lambda m: self.__get_label(m.group(), "USERID"), text)

        return text

    def __process_text(self, text):
        if not isinstance(text, str) or not text:
            return text

        # Сначала RegEx (почта, ссылки, телефоны)
        text = self.__regex_anonymize(text)

        # Затем Natasha (имена, города)
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_ner(self.ner_tagger)

        spans = sorted(doc.spans, key=lambda x: x.start, reverse=True)
        for span in spans:
            span.normalize(self.morph_vocab)
            label = self.__get_label(span.normal or span.text, span.type)
            text = text[:span.start] + label + text[span.stop:]

        return text

    def __process_text_again(self, text):
        if not isinstance(text, str) or not text:
            return text

        for entity in self.entities.keys():
            if entity not in text.lower(): continue
            text = re.sub(re.escape(entity), self.entities[entity], text, flags=re.IGNORECASE)

        return text

    def __zero_step(self, data):
        for msg in data.get('messages', []):
            # Анонимизация метаданных отправителя
            for field in ['from', 'actor']:
                if field in msg and isinstance(msg[field], str):
                    msg[field] = self.__get_label(msg[field], "PER")
        return data

    def __anonymise(self, data, process_text_fn):
        if isinstance(data, str):
            return process_text_fn(data)
        for key in data:
            val = data[key]
            if isinstance(val, str):
                data[key] = process_text_fn(val)
            elif isinstance(val, dict):
                data[key] = self.__anonymise(val, process_text_fn)
            elif isinstance(val, list):
                for i in range(len(val)):
                    val[i] = self.__anonymise(val[i], process_text_fn)

        return data

    def run(self, input_file, output_file):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Ошибка: Файл {input_file} не найден.")
            return

        data = self.__zero_step(data)
        data = self.__anonymise(data, self.__process_text)
        data = self.__anonymise(data, self.__process_text_again)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Обработано и сохранено в {output_file}")
        # вывод найденных сущностей с ключами
        print(self.entities)