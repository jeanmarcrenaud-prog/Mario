import re

with open('C:/Users/johns/Documents/GitHub/Mario/src/models/text_to_speech.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer les logs de synthèse en DEBUG
replacements = [
    (r'logger\.info\(\[OUTIL\] Voix', r'logger.debug("[OUTIL] Voix'),
    (r'logger\.info(\[AUDIO\] Synthèse audio en', r'logger.debug("[AUDIO] Synthèse audio en'),
    (r'logger\.info\(\[DEBUG\] Audio data', r'logger.debug("[DEBUG] Audio data'),
    (r'logger\.info\(\[DEBUG\] Sample rate', r'logger.debug("[DEBUG] Sample rate'),
    (r'logger\.info\(f"\[DEBUG\] Valeur max \(int16\)', r'logger.debug(f"[DEBUG] Valeur max (int16'),
    (r'logger\.info\(f"\[DEBUG\] Valeur max \(float32\)', r'logger.debug(f"[DEBUG] Valeur max (float32'),
    (r'logger\.info\(\[DEBUG\] Lecture debug'),
    (r'logger\.info\(\[TEST\] Test de synthèse', r'logger.debug("[TEST] Test de synthèse'),
    (r'logger\.info\(f"\[TEST\] \.', r'logger.debug(f"[TEST] '),
]

pattern = r'(logger\.info)\((.+?)\)'
replacement = r'\1.debug(\2'

for old, new in replacements:
    content = content.replace(old, new)

# Also handle [AUDIO] Lecture audio terminée
content = content.replace('logger.info("[AUDIO] Lecture audio terminée avec succès")', 
                           'logger.debug("[AUDIO] Lecture audio terminée avec succès")')

# Handle model_path and config_path
content = content.replace('logger.info(f"model_path: {model_path} ")', 
                           'logger.debug(f"model_path: {model_path} ")')
content = content.replace('logger.info(f"config_path: {config_path} ")', 
                           'logger.debug(f"config_path: {config_path} ")')

with open('C:/Users/johns/Documents/GitHub/Mario/src/models/text_to_speech.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fichier mis à jour avec logs DEBUG')
