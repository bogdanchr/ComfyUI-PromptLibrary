import random

from ..models import SelectionResult
from ..storage import pick_unique_line

class PromptSelector:
    @staticmethod
    def select(prompt_file, mode, seed, index=0, salt=0):
        entries = prompt_file.entries
        if prompt_file.error or not entries:
            raise ValueError(prompt_file.error or "No prompt entries")
        count = len(entries)
        effective_seed = int(seed) + int(salt)
        if mode == "sequential":
            selected = int(index) % count
        elif mode == "weighted":
            weights = [entry.weight for entry in entries]
            if sum(weights) <= 0:
                weights = [1.0] * count
            selected = random.Random(effective_seed).choices(range(count), weights=weights, k=1)[0]
        elif mode == "unique":
            texts = [entry.text for entry in entries]
            text, selected = pick_unique_line(prompt_file.path, texts, effective_seed)
            return SelectionResult(text=text, index=selected, count=count)
        else:
            selected = random.Random(effective_seed).randrange(count)
        return SelectionResult(text=entries[selected].text, index=selected, count=count)
