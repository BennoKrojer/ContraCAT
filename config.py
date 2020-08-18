import os
from pathlib import Path

base = Path(os.path.dirname(os.path.realpath(__file__)))
data_dir = base / 'data'
adversarial_data_dir = data_dir / 'adversarial_ContraPro'
template_data_dir = data_dir / 'templates'
contrapro_file = base / 'ContraPro' / 'contrapro.json'
resources_dir = base / 'resources'
