import yaml
import os
import pytest

def test_validate_config():
    filename = os.path.join("","config.yaml")
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)

    for prompt in data['prompts']:
        assert 'type' in prompt
        
        assert prompt['type'] == 'SimpleText' or prompt['type'] == 'VideoClipArray'
    
        assert 'instructions' in prompt
        assert 'outputfilename' in prompt
        
        if prompt['type'] == 'VideoClipArray':
            assert 'count' in prompt
            assert 'videoclipnamepattern' in prompt
            assert 'videoextension' in prompt