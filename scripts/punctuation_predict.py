from deepmultilingualpunctuation import PunctuationModel
import sys

segment = sys.stdin.read().strip()

model = PunctuationModel()
result = model.restore_punctuation(segment)
print(result)